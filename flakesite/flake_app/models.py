from django.db import models
from django.db.models.signals import pre_delete, pre_save
from django.core.files.storage import default_storage
from django.dispatch import receiver
from django.conf import settings
from django.urls import reverse

from polymorphic.compat import with_metaclass
from polymorphic.models import PolymorphicModel, PolymorphicModelBase
from rules.contrib.models import RulesModel, RulesModelMixin, RulesModelBaseMixin

import rules

from .predicates import is_owner
from .fields import DropboxImageField

# A device containing flakes.
class Device(RulesModel):
    name = models.CharField(max_length = 255, unique = True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, null = True, related_name = 'devices')

    class Meta:
        rules_permissions = {
            "view" : rules.is_authenticated,
            "change" : is_owner
        }

    def __str__(self):
        return "{} ({})".format(self.name, self.owner)

    def get_absolute_url(self):
        return reverse('flake_app:device-detail', kwargs={'pk' : self.pk})

# Base class for the exfoliated flake models.

def get_base_file_location(instance, filename):
    return '{0}/{1}/{2}'.format(instance.box, instance.chip, filename)

def get_trained_file_location(instance, filename):
    if instance.trained_path:
        return instance.trained_path
    return get_base_file_location(instance, filename)

def get_flake_file_location(instance, filename):
    if instance.flake_path:
        return instance.flake_path
    return get_base_file_location(instance, filename)

def get_default_map_file_location(instance, filename):
    if instance.map_path:
        return instance.map_path
    return get_base_file_location(instance, 'map.jpeg')

class PolymorphicRulesMetaclass(RulesModelBaseMixin, PolymorphicModelBase):
    pass

class Flake(RulesModelMixin, PolymorphicModel, metaclass = PolymorphicRulesMetaclass):
    box   = models.CharField(max_length = 255)  # Box in which the flake is located.
    chip  = models.CharField(max_length = 12)   # Chip on which the flake is located.
    num   = models.CharField(max_length = 12)   # Flake number on the chip.
    x_pos = models.BigIntegerField(default = 0) # X-position in pixels at which the flake is located.
    y_pos = models.BigIntegerField(default = 0) # Y-position in pixels at which the flake is located.
    contour = models.BinaryField(null = True)   # base64 representation of the contour that represents the largest non-noise
                                                # feature of the flake.

    name = models.CharField(max_length = 255, blank = True, null = True)    # Readable name for the flake. By default [box]_[chip]_[num] 
    
    # Owner of the flake, who has control over its use. Nominally, whoever scanned it.
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, null = True, related_name = 'flakes')

    map_image     = DropboxImageField(upload_to = get_default_map_file_location, dropbox_url_field = 'map_url', null = True, blank = True)
    flake_image   = DropboxImageField(upload_to = get_flake_file_location, dropbox_url_field = 'flake_url', null = True, blank = True)
    trained_image = DropboxImageField(upload_to = get_trained_file_location, dropbox_url_field = 'trained_url', null = True, blank = True)

    # Cached Shared Link URLS for displaying the flake images. See storage.py and fields.py 
    map_url       = models.URLField(blank = True, null = True, max_length = 500)
    flake_url     = models.URLField(blank = True, null = True, max_length = 500)
    trained_url   = models.URLField(blank = True, null = True, max_length = 500)

    # Overrides for the file locations of the map, flake, and trained images. Currently used so that we don't require the server to have write access to the Dropbox.
    # These are pushed by the FlakeRun.py file.
    map_path     = models.CharField(blank = True, null = True, max_length = 500)
    flake_path   = models.CharField(blank = True, null = True, max_length = 500)
    trained_path = models.CharField(blank = True, null = True, max_length = 500)

    device = models.ForeignKey(Device, on_delete = models.SET_NULL, blank = True, null = True, related_name = 'flakes')

    uploaded_at = models.DateTimeField(auto_now_add = True)

    # Whether or not to display LUT adjusted images on the Flake Detail page.
    has_LUT = False

    class Meta():
        rules_permissions = {
            "view" : rules.is_authenticated,
            "change" : is_owner
        }

    def __init__(self, *args, **kwargs):
        # We use this to keep track of if the Flake is being deleted to know if it's safe to delete the map image file.
        self.deleting = False
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Sketchy override to set the default name value for flakes.
        if not self.name or len(self.name) == 0:
            self.name = self.box + "_" + self.chip + "_" + self.num

        if not self.map_image:
            default_storage_loc = get_default_map_file_location(self, '')
            if default_storage.exists(default_storage_loc):
                self.map_image = default_storage_loc
        
        # Even sketchier override to manually reset the paths of map_image, flake_image, and trained_image to the overrides
        if self.map_path:
            self.map_image.name = self.map_path
        if self.flake_path:
            self.flake_image.name = self.flake_path
        if self.trained_path:
            self.trained_image.name = self.trained_path         

        super().save(*args, **kwargs)

    def __str__(self):
        return self.box + "_" + self.chip + "_" + self.name
    
    # Returns a list of fields to display on the flake detail view, and for sorting on the index view.
    def get_displayed_fields(self):
        displayed = {}
        return displayed

    def get_absolute_url(self):
        return reverse('flake_app:flake-detail', kwargs={'pk' : self.pk})

@receiver(pre_delete, sender = Flake, dispatch_uid = 'flake_predelete_signal')
def set_deleting(sender, instance, using, **kwargs):
    instance.deleting = True

class Graphene(Flake):
    monolayers = models.BigIntegerField(default = 0)
    bilayers   = models.BigIntegerField(default = 0)
    trilayers  = models.BigIntegerField(default = 0)
    gates      = models.BigIntegerField(default = 0)
    noise      = models.BigIntegerField(default = 0)

    def get_displayed_fields(self):
        displayed = super().get_displayed_fields()
        displayed.update({'Monolayers' : self.monolayers, 'Bilayers' : self.bilayers, 'Trilayers' : self.trilayers, 'Gates' : self.gates, 'Noise' : self.noise})
        return displayed

class hBN(Flake):
    
    thin = models.BigIntegerField(default = 0)
    thick = models.BigIntegerField(default = 0)
    capsule = models.BigIntegerField(default = 0) # TODO: This name doesn't really make sense.
    noise = models.BigIntegerField(default = 0)

    batch = models.CharField(max_length = 12, null = True, blank = True) # The hBN batch this exfoliation was sourced from

    has_LUT = True

    def get_displayed_fields(self):
        displayed = super().get_displayed_fields()
        displayed.update({'Capsule area' : self.capsule, 'Few Layer' : self.thin, 'Thick Layer' : self.thick, 'batch' : self.batch})
        return displayed

# Comment on a particular device
class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, null = True)
    device = models.ForeignKey(Device, related_name = 'comments', on_delete = models.CASCADE, null = True)

    body = models.TextField()

    created = models.DateTimeField(auto_now = True)
    parent_comment = models.ForeignKey('self', on_delete = models.CASCADE, null = True, blank = True, related_name = 'replies')

    class Meta:
        ordering = ('created',)
    
    def __str__(self):
        display_name = "No one"
        if self.user:
            display_name = self.user.username
        return "Comment by {0} on device {1}".format(display_name, self.device.name)