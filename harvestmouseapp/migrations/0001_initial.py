# Generated by Django 3.1.3 on 2020-12-03 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HarvestedMouse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('handler', models.TextField()),
                ('physicalId', models.TextField(unique=True)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('U', 'Unknown')], max_length=1)),
                ('mouseLine', models.TextField()),
                ('genoType', models.TextField()),
                ('birthDate', models.DateField()),
                ('endDate', models.DateField()),
                ('confirmationOfGenoType', models.TextField()),
                ('phenoType', models.TextField()),
                ('projectTitle', models.TextField()),
                ('experiment', models.TextField()),
                ('comment', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='HarvestedBasedNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liver', models.IntegerField()),
                ('liverTumor', models.IntegerField()),
                ('others', models.TextField()),
                ('harvestedMouseId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='freezeRecord', to='harvestmouseapp.harvestedmouse')),
            ],
        ),
        migrations.CreateModel(
            name='HarvestedAdvancedNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liver', models.IntegerField()),
                ('liverTumor', models.IntegerField()),
                ('smallIntestine', models.IntegerField()),
                ('smallIntestineTumor', models.IntegerField()),
                ('skin', models.IntegerField()),
                ('skinHair', models.IntegerField()),
                ('others', models.TextField()),
                ('harvestedMouseId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pfaRecord', to='harvestmouseapp.harvestedmouse')),
            ],
        ),
    ]
