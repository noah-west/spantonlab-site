# Generated by Django 4.1.1 on 2023-08-17 18:09

from django.db import migrations, models
import django.db.models.deletion
import flake_app.fields
import flake_app.models
import rules.contrib.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('owner', models.IntegerField()),
                ('desc', models.TextField(null=True)),
            ],
            bases=(rules.contrib.models.RulesModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Flake',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('box', models.CharField(max_length=255)),
                ('chip', models.CharField(max_length=12)),
                ('num', models.CharField(max_length=12)),
                ('x_pos', models.BigIntegerField(default=0)),
                ('y_pos', models.BigIntegerField(default=0)),
                ('contour', models.BinaryField(null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('owner', models.IntegerField()),
                ('map_url', models.URLField(blank=True, max_length=500, null=True)),
                ('flake_url', models.URLField(blank=True, max_length=500, null=True)),
                ('trained_url', models.URLField(blank=True, max_length=500, null=True)),
                ('map_image', flake_app.fields.DropboxImageField(blank=True, dropbox_url_field='map_url', null=True, upload_to=flake_app.models.get_default_map_file_location)),
                ('flake_image', flake_app.fields.DropboxImageField(blank=True, dropbox_url_field='flake_url', null=True, upload_to=flake_app.models.get_flake_file_location)),
                ('trained_image', flake_app.fields.DropboxImageField(blank=True, dropbox_url_field='trained_url', null=True, upload_to=flake_app.models.get_flake_file_location)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='flakes', to='flake_app.device')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype')),
            ],
            bases=(rules.contrib.models.RulesModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Graphene',
            fields=[
                ('flake_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='flake_app.flake')),
                ('monolayers', models.BigIntegerField(default=0)),
                ('bilayers', models.BigIntegerField(default=0)),
                ('trilayers', models.BigIntegerField(default=0)),
                ('gates', models.BigIntegerField(default=0)),
                ('noise', models.BigIntegerField(default=0)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('flake_app.flake',),
        ),
        migrations.CreateModel(
            name='hBN',
            fields=[
                ('flake_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='flake_app.flake')),
                ('thin', models.BigIntegerField(default=0)),
                ('thick', models.BigIntegerField(default=0)),
                ('capsule', models.BigIntegerField(default=0)),
                ('noise', models.BigIntegerField(default=0)),
                ('batch', models.CharField(blank=True, max_length=12, null=True)),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('flake_app.flake',),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.IntegerField()),
                ('body', models.TextField()),
                ('created', models.DateTimeField(auto_now=True)),
                ('flake', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='flake_app.flake')),
                ('parent_comment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='flake_app.comment')),
            ],
            options={
                'ordering': ('created',),
            },
        ),
    ]
