# Generated by Django 5.1.1 on 2024-09-23 23:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0004_remove_wixproduct_collection_wixproduct_collections'),
    ]

    operations = [
        migrations.AddField(
            model_name='variant',
            name='images',
            field=models.ManyToManyField(blank=True, null=True, related_name='variant_images', to='agent.image'),
        ),
    ]
