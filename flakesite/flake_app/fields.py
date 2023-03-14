from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from django.forms import FileField

from .storage import SharedLinkDropBoxStorage
from io import BytesIO

# This field references a seperate field which contains a permanent shared url for an image
# stored on Dropbox, reducing the overhead from fetching a temporary URL from Dropbox every request.
# See storages.py

class DropboxImageFieldFile(ImageFieldFile):
    def url(self):
        if not isinstance(self.storage, SharedLinkDropBoxStorage):
            return super().url
        if not hasattr(self.field, 'dropbox_url_field') or not self.field.dropbox_url_field:
            # The corresponding field does not have a dropbox_url_field set, so use the normal
            # behavior.
            return super().url
        self._require_file()
        initial_url = getattr(self.instance, self.field.dropbox_url_field)
        dropbox_url = self.storage.url(self.name, initial_url)
        if initial_url is None:
            # Since we didn't have a saved URL, the storage returned a new one. Set the instance's
            # field to this URL, and save it.
            setattr(self.instance, self.field.dropbox_url_field, dropbox_url)
            self.instance.save()
        return dropbox_url

class DropboxImageField(ImageField):
    attr_class = DropboxImageFieldFile
    def __init__(self, dropbox_url_field = None, **kwargs):
        self.dropbox_url_field = dropbox_url_field
        super().__init__(**kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        if self.dropbox_url_field:
            kwargs["dropbox_url_field"] = self.dropbox_url_field
        return name, path, args, kwargs
