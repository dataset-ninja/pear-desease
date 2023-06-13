import glob
import os

import supervisely as sly
from supervisely.io.fs import file_exists, get_file_name, get_file_name_with_ext


def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    dataset_path = "/home/iwatkot/supervisely/ninja-datasets/Pear"
    annotations_path = "/home/iwatkot/supervisely/ninja-datasets/Pear/annotation/YOLO/"

    batch_size = 10

    def create_ann(image_path):
        labels = []
        tags = []
        obj_class = obj_class_pear

        image_np = sly.imaging.image.read(image_path)[:, :, 0]
        img_height = image_np.shape[0]
        img_wight = image_np.shape[1]

        if ds_name == "leaves":
            tag_name = image_path.split("/")[-2]
            tag_meta = name_to_meta[tag_name]
            tags = [sly.Tag(tag_meta)]
            obj_class = obj_class_leaf

        bbox_name = get_file_name(image_path) + ".txt"
        bbox_path = os.path.join(annotations_path, ds_name, bbox_name)
        if file_exists(bbox_path):
            with open(bbox_path) as f:
                content = f.read().split("\n")

                for curr_data in content:
                    if len(curr_data) != 0:
                        curr_data = list(map(float, curr_data.split(" ")))
                        left = int((curr_data[1] - curr_data[3] / 2) * img_wight)
                        right = int((curr_data[1] + curr_data[3] / 2) * img_wight)
                        top = int((curr_data[2] - curr_data[4] / 2) * img_height)
                        bottom = int((curr_data[2] + curr_data[4] / 2) * img_height)
                        rectangle = sly.Rectangle(top=top, left=left, bottom=bottom, right=right)
                        label = sly.Label(rectangle, obj_class)
                        labels.append(label)

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels, img_tags=tags)

    obj_class_pear = sly.ObjClass("pear", sly.Rectangle)
    obj_class_leaf = sly.ObjClass("leaf", sly.Rectangle)
    curl_tag_meta = sly.TagMeta("curl", sly.TagValueType.NONE)
    healthy_tag_meta = sly.TagMeta("healthy", sly.TagValueType.NONE)
    slug_tag_meta = sly.TagMeta("slug", sly.TagValueType.NONE)
    spot_tag_meta = sly.TagMeta("spot", sly.TagValueType.NONE)

    name_to_meta = {
        "curl": curl_tag_meta,
        "healthy": healthy_tag_meta,
        "slug": slug_tag_meta,
        "spot": spot_tag_meta,
    }

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
    meta = sly.ProjectMeta(
        obj_classes=[obj_class_leaf, obj_class_pear],
        tag_metas=[curl_tag_meta, healthy_tag_meta, slug_tag_meta, spot_tag_meta],
    )
    api.project.update_meta(project.id, meta.to_json())

    ann_folders = next(os.walk(annotations_path))[1]

    for ds_name in ann_folders:
        images_path = os.path.join(dataset_path, ds_name)

        dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)
        if ds_name == "leaves":
            images_pathes = glob.glob(images_path + "/*/*.jpg")
        else:
            images_names = os.listdir(images_path)
            images_pathes = [os.path.join(images_path, im_name) for im_name in images_names]

        progress = sly.Progress("Create dataset {}".format(ds_name), len(images_pathes))

        for img_pathes_batch in sly.batched(images_pathes, batch_size=batch_size):
            normal_images_pathes = []
            for curr_path in img_pathes_batch:
                try:
                    sly.imaging.image.read(curr_path)[:, :, 0]
                except Exception:
                    continue
                normal_images_pathes.append(curr_path)
            img_names_batch = [get_file_name_with_ext(im_path) for im_path in normal_images_pathes]
            img_infos = api.image.upload_paths(dataset.id, img_names_batch, normal_images_pathes)
            img_ids = [im_info.id for im_info in img_infos]

            anns = [create_ann(image_path) for image_path in normal_images_pathes]
            api.annotation.upload_anns(img_ids, anns)

            progress.iters_done_report(len(img_names_batch))

    return project
