# Generated by Django 5.1.1 on 2024-09-24 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0005_variant_images'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='title',
            field=models.CharField(max_length=1024),
        ),
        migrations.AlterField(
            model_name='image',
            name='alt_text',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='title',
            field=models.CharField(max_length=1024),
        ),
        migrations.AlterField(
            model_name='variant',
            name='images',
            field=models.ManyToManyField(blank=True, related_name='variant_images', to='agent.image'),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='additional_info_title_1',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='additional_info_title_2',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='additional_info_title_3',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='additional_info_title_4',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='additional_info_title_5',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='additional_info_title_6',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='name',
            field=models.CharField(max_length=1024),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='product_option_name_1',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='product_option_name_2',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='product_option_name_3',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='product_option_name_4',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='product_option_name_5',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='product_option_name_6',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]
