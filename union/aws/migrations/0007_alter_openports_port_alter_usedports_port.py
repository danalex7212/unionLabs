# Generated by Django 4.1.2 on 2022-10-21 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0006_openinstance_sg_id_usedinstance_sg_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openports',
            name='port',
            field=models.IntegerField(unique=True),
        ),
        migrations.AlterField(
            model_name='usedports',
            name='port',
            field=models.IntegerField(unique=True),
        ),
    ]
