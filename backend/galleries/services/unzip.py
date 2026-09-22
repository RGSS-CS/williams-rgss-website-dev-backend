from django.core.exceptions import ValidationError
from django.core.files import File
from galleries.models import MassImport, Photos
import zipfile

def unzip():
    with zipfile.ZipFile