from django.core.exceptions import ValidationError
from django.core.files import File
from galleries.models import MassImport, Photos
from zipfile import ZipFile

def unzipPhotos(club, savePath, zipFile):
    with ZipFile(zipFile) as zObject:
        zObject.extractall(savePath)

    