# Generated by Django 4.2.6 on 2023-12-21 19:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('PDF_TESS', '0003_alter_extractedtext_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='extractedtext',
            name='image',
        ),
    ]
