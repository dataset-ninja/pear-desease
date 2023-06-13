Dataset **DiaMOS Plant Desease** can be downloaded in Supervisely format:

 [Download](https://assets.supervise.ly/supervisely-supervisely-assets-public/teams_storage/k/y/OD/3JuN0uvIu8Pdb0FHsC8adJK74wO1Mmcp30kvJhxn1D7fARdOdV16YonZxby01P64gjWtfXvmYYBLCaKdDz1WbduOxjLUjPmsoCx9DiZ6j5T8RxJHAnY4hNOq595P.tar)

As an alternative, it can be downloaded with *dataset-tools* package:
``` bash
pip install --upgrade dataset-tools
```

... using following python code:
``` python
import dataset_tools as dtools

dtools.download(dataset='DiaMOS Plant Desease', dst_path='~/dtools/datasets/DiaMOS Plant Desease.tar')
```
The data in original format can be 🔗[downloaded here.](https://zenodo.org/record/5557313/files/Pear.zip?download=1)