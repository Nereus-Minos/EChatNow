# Generated by Django 2.1 on 2019-04-22 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mvc', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatmessage',
            name='write_id',
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='is_read',
            field=models.IntegerField(default=1, verbose_name='是否为已读消息'),
            preserve_default=False,
        ),
    ]
