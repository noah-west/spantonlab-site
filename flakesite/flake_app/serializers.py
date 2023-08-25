import base64
from django.conf import settings
from django.forms.fields import ImageField as ImageFormField
from django.forms.fields import FileField as FileFormField
from django.core.files.storage import default_storage

from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from rest_framework.fields import CurrentUserDefault
from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.exceptions import ValidationError

from rest_framework.validators import UniqueTogetherValidator

from io import BytesIO

from .models import Device, Flake, Graphene, hBN

class UniqueTogetherOrOwnerValidator(UniqueTogetherValidator):
    '''
    Override to allow for non-unique values when the owner is identical.
    Creates are automatically overriden to updates() when the passed values are matching
    '''
    
    def exclude_owned(self, attrs, queryset):
        if 'owner' in attrs:
            queryset = queryset.exclude(owner = attrs["owner"])
        return queryset

    def __call__(self, attrs, serializer):
        self.queryset = self.exclude_owned(attrs, self.queryset)
        super(UniqueTogetherOrOwnerValidator, self).__call__(attrs, serializer)

class BinaryField(serializers.Field):
    '''
    Field that converts base64 strings into bytes appropriate for storage in Django's BinaryField
    '''
    def to_representation(self, value):
        return base64.b64encode(value).decode('ascii')
    
    def to_internal_value(self, data):
        if not isinstance(data, str):
            msg = 'Incorrect type. Expected a string, but got %s'
            raise (msg % type(data).__name__)
        
        return base64.b64decode(data)

# Due to a bug with Django REST framework, the field does not pass on its allow_empty_file argument
# to the parent Django Form ImageField it uses for verification. This fixes that issue.

# TODO: At some point this should be fixed in the Django REST framework itself. Due to the additional
# PIL image verification, this is too complicated to perform a simple fix.

class AllowEmptyImageField(serializers.ImageField):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # This is required to allow empty images, so set it manually.
        self._DjangoImageField = AllowEmptyImageFormField

    def to_internal_value(self, data):
        # See parent class.
        file_object = super(serializers.ImageField, self).to_internal_value(data)
        django_field = self._DjangoImageField(max_length = self.max_length, allow_empty_file = self.allow_empty_file)

        django_field.error_messages = self.error_messages
        return django_field.clean(file_object)

# PIL throws an exception if we attempt to 'verify' an empty file, so we check for that here,
# since we support empty images, provided they have a passed file name.
class AllowEmptyImageFormField(ImageFormField):
    def to_python(self, data):
        if hasattr(data, "read"):
            file = BytesIO(data.read())
            if file.getbuffer().nbytes == 0:
                # The image is blank, only verify file name etc.
                return super(FileFormField, self).to_python(data)
        # Perform PIL image verification.
        data.seek(0)
        return super().to_python(data)

class FlakeSerializer(serializers.HyperlinkedModelSerializer):
    # This is a hidden field so that it is properly appended to the `value` kwarg for validation.
    owner = serializers.HiddenField(default = CurrentUserDefault())
    contour = BinaryField(required = False)

    # These images are allowed to be 'empty' since by default, we're using DropboxStorage.
    # We trust the uploading user may have uploaded them into their proper location manually.
    flake_image = AllowEmptyImageField(required = False, allow_empty_file = True, use_url = False)
    trained_image = AllowEmptyImageField(required = False, allow_empty_file = True, use_url = False)
    map_image = AllowEmptyImageField(required = False, allow_empty_file = True, use_url = False)

    # Optionally let the uploading user point at different Dropbox URL we have access to.
    over_flake_loc = serializers.CharField(max_length = 500, required = False, validators = [validate_path_exists])
    over_trained_loc = serializers.CharField(max_length = 500, required = False, validators = [validate_path_exists])
    over_map_loc = serializers.CharField(max_length = 500, required = False, validators = [validate_path_exists])

    device = serializers.HyperlinkedRelatedField(view_name = 'flake_app:device-detail', queryset = Device.objects.all(), allow_null = True, required = False)

    class Meta:
        model = Flake
        fields = ['box', 'chip', 'num', 'name', 'x_pos', 'y_pos', 'owner', 'contour', 'device', 'map_image', 'flake_image', 'trained_image', 'flake_url', 'trained_url', 'map_url', 'map_path', 'flake_path', 'trained_path']
        validators = [
                UniqueTogetherOrOwnerValidator(
                    queryset = Flake.objects.all(),
                    fields = ['box', 'chip', 'num']
                )
        ]

    def create(self, validated_data):
        # If we find a flake with the same box, chip, and name, than we update it rather than adding a new chip. The UniqueTogetherOrOwnerValidator
        # ensures that the flake can only be updated by its own owner.
        ModelClass = self.Meta.model

        flake, create = ModelClass.objects.update_or_create(box = validated_data.get('box'), chip = validated_data.get('chip'), num = validated_data.get('num'),
                                                          defaults = validated_data)
        return flake
    
    def validate_map_path(self, value):
        if value and not default_storage.exists(value):
            raise serializers.ValidationError('The path provided does not exist.')
        return value

    def validate_flake_path(self, value):
        if value and not default_storage.exists(value):
            raise serializers.ValidationError('The path provided does not exist.')
        return value

    def validate_trained_path(self, value):
        if value and not default_storage.exists(value):
            raise serializers.ValidationError('The path provided does not exist.')
        return value

class GrapheneSerializer(FlakeSerializer):
    
    class Meta:
        model = Graphene
        fields = ['box', 'chip', 'num', 'name', 'x_pos', 'y_pos', 'owner', 'contour', 'device', 'map_image', 'flake_image', 'trained_image', 'monolayers', 'bilayers', 'gates', 'noise', 'map_path', 'flake_path', 'trained_path']
        validators = [
                UniqueTogetherOrOwnerValidator(
                    queryset = Flake.objects.all(),
                    fields = ['box', 'chip', 'num']
                )
        ]
        
        extra_kwargs = {
            'url': {'view_name': 'flake_app:flake-detail', 'lookup_field': 'pk'}
        }

class hBNSerializer(FlakeSerializer):
    class Meta:
        model = hBN
        fields = ['box', 'chip', 'num', 'name', 'x_pos', 'y_pos', 'owner', 'contour', 'device', 'map_image', 'flake_image', 'trained_image', 'thin', 'thick', 'capsule', 'noise', 'map_path', 'flake_path', 'trained_path']
        validators = [
                UniqueTogetherOrOwnerValidator(
                    queryset = Flake.objects.all(),
                    fields = ['box', 'chip', 'num']
                )
        ]
        
        extra_kwargs = {
            'url': {'view_name': 'flake_app:flake-detail', 'lookup_field': 'pk'},
        }


class FlakePolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Graphene: GrapheneSerializer,
        Flake: FlakeSerializer,
        hBN: hBNSerializer
    }

    @property
    def data(self):
        ret = super().data
        if self.instance is not None:
            return ReturnDict(ret, serializer = self._get_serializer_from_model_or_instance(self.instance))
        
        # If we don't have an instance, try to retreive the type from the validated data.
        if hasattr(self, '_validated_data'):
            resource_type = self._get_resource_type_from_mapping(self.validated_data)
            child_serializer = self._get_serializer_from_resource_type(resource_type)

            if child_serializer is not None:
                return ReturnDict(ret, serializer = child_serializer)
        
        return ReturnDict(ret, serializer = self)

class UserSerializer(serializers.HyperlinkedModelSerializer):
    flakes = serializers.HyperlinkedRelatedField(many = True, view_name = 'flake_app:flake-detail', queryset = Flake.objects.all())

    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ['id', 'username', 'flakes']
    
class DeviceSerializer(serializers.HyperlinkedModelSerializer):
    flakes = serializers.HyperlinkedRelatedField(many = True, view_name = 'flake_app:flake-detail', queryset = Flake.objects.all())

    class Meta:
        model = Device
        fields = ['name', 'desc', 'flakes']

        extra_kwargs = {
            'url': {'view_name': 'flake_app:device-detail', 'lookup_field': 'pk'},
        }