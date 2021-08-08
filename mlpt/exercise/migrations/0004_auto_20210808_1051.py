# Generated by Django 3.2.6 on 2021-08-08 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exercise', '0003_auto_20210806_1613'),
    ]

    operations = [
        migrations.RenameField(
            model_name='equipmentammo',
            old_name='part',
            new_name='ammo',
        ),
        migrations.AddField(
            model_name='equipmentammo',
            name='unit_type',
            field=models.CharField(choices=[('G', 'Ground Combat Element'), ('N', 'Non-Ground Combat Element')], default='G', max_length=1),
        ),
    ]
