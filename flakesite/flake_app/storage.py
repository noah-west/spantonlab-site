from requests import delete
from storages.backends.dropbox import DropBoxStorage
from storages.backends.dropbox import _DEFAULT_TIMEOUT, _DEFAULT_MODE
from django.apps import apps
from django.core.exceptions import SuspiciousFileOperation, ImproperlyConfigured
from django.utils._os import safe_join

from dropbox import Dropbox
from dropbox.sharing import SharedLinkSettings, LinkAudience
from dropbox.exceptions import ApiError
from storages.utils import setting

import os
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

        # TODO 2: If the Dropbox API doesn't have write permissions (as it currently doesn't), this will spit out a lot of errors when deleting flakes.
        # The flakes will be deleted, but the images will not.
    
        if name.endswith("map.jpeg"):
            FlakeModel = apps.get_model(app_label='flake_app', model_name='Flake')
            for model_instance in FlakeModel.objects.filter(map_image__endswith = name.lstrip(self.root_path)):
                if not model_instance.deleting:
                    # Another Flake references this map image, so don't delete it.
                    return
        super().delete(name)

    def _full_path(self, name):
        
        # This is a quick fix for Django storages which allows the Dropbox storage to be used on Windows.
        # TODO: Check if this was fixed on the storages package.

        if name == '/':
            name = ''
        if os.name == 'nt':
            final_path = os.path.join(self.root_path, name).replace('\\', '/')
            # Separator on linux system
            sep = '/'
            base_path = self.root_path

            if (not os.path.normcase(final_path).startswith(os.path.normcase(base_path + sep)) and
                    os.path.normcase(final_path) != os.path.normcase(base_path) and
                    os.path.dirname(os.path.normcase(base_path)) != os.path.normcase(base_path)):

                raise SuspiciousFileOperation(
                    'The joined path ({}) is located outside of the base path '
                    'component ({})'.format(final_path, base_path))
            return final_path    
        return safe_join(self.root_path, name).replace('\\', '/')