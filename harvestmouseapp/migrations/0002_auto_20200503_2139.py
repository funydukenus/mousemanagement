# Generated by Django 3.0.2 on 2020-05-03 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harvestmouseapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='harvestedmouse',
            name='confirmationOfGenoType',
            field=models.TextField(),
        ),
    ]
