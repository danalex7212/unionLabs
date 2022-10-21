# Generated by Django 4.1.2 on 2022-10-20 00:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0002_user_ip'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpenPorts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('port', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='UsedPorts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('port', models.IntegerField()),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='ip',
        ),
        migrations.CreateModel(
            name='UsedInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('ip', models.CharField(max_length=255)),
                ('port', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aws.usedports')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OpenInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('ip', models.CharField(max_length=255)),
                ('port', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aws.usedports')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
