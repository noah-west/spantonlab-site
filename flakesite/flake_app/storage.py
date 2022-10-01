from requests import delete
from storages.backends.dropbox import DropBoxStorage
from storages.backends.dropbox import _DEFAULT_TIMEOUT, _DEFAULT_MODE
from django.core.exceptions import SuspiciousFileOperation, ImproperlyConfigured
from django.utils._os import safe_join

from dropbox import Dropbox
from dropbox.sharing import SharedLinkSettings, LinkAudience
from dropbox.exceptions import ApiError
from storages.utils import setting

from .models import Flake

import time
# Override to allow the use of permanent shared links for stored files, where applicable.
# This reduces the overhead from fetching a temporary link from dropbox for every request.

# Also implements some bespoke behavior to prevent deletion of a map file if other references
# still exist.
class SharedLinkDropBoxStorage(DropBoxStorage):

    def _save(self, name, content):
        content.open()
        if content.size == 0:
            content.close()
            return name.lstrip(self.root_path)
        return super()._save(name, content)

    def url(self, name, shared_link):
        # Attempt to fetch a new shared link.
        if shared_link is None:
            try:
                shared_settings = SharedLinkSettings(audience = LinkAudience('public'), allow_download = True)
                shared_link = self.client.sharing_create_shared_link_with_settings(self._full_path(name), shared_settings).url
                 # Modifying so that the path is appropriate for raw viewing.
                shared_link = shared_link.replace('?dl=0', '?raw=1')
            except ApiError:
                # Fetching the shared link failed for some reason, return a temporary link instead.
                return super().url(name)
        return shared_link

    def delete(self, name):
        # Override to only delete map images if there's nothing else referencing them.
        # This must be done here as django-cleanup does not offer a way to prevent deletion of specific fields.
        
        # TODO: This is terrible.
        if name.endswith("map.jpeg"):
            for model_instance in Flake.objects.filter(map_image__endswith = name.lstrip(self.root_path)):
                if not model_instance.deleting:
                    # Another Flake references this map image, so don't delete it.
                    return
        super().delete(name)