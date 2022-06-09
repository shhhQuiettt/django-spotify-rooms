# Generated by Django 3.2.13 on 2022-06-06 13:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_room_host'),
        ('spotify', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spotifyaccesstoken',
            name='room',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='spotify_access_token', serialize=False, to='api.room'),
        ),
    ]