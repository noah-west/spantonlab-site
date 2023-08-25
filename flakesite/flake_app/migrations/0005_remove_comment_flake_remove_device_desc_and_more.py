# Generated by Django 4.1.1 on 2023-08-23 19:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('flake_app', '0004_rename_paths'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='flake',
        ),
        migrations.RemoveField(
            model_name='device',
            name='desc',
        ),
        migrations.AddField(
            model_name='comment',
            name='device',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='flake_app.device'),
        ),
    ]
