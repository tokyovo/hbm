# Generated by Django 5.1.1 on 2024-09-24 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agent', '0007_alter_collection_source_url_alter_image_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='optioncategory',
            name='name',
            field=models.CharField(max_length=521, unique=True),
        ),
        migrations.AlterField(
            model_name='optionvalue',
            name='value',
            field=models.CharField(max_length=521),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='brand',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='discount_mode',
            field=models.CharField(blank=True, max_length=521, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='field_type',
            field=models.CharField(default='Product', max_length=521),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='handle_id',
            field=models.CharField(max_length=521),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='inventory',
            field=models.CharField(default='InStock', max_length=521),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='product_option_type_1',
            field=models.CharField(blank=True, max_length=521, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='product_option_type_2',
            field=models.CharField(blank=True, max_length=521, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='product_option_type_3',
            field=models.CharField(blank=True, max_length=521, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='product_option_type_4',
            field=models.CharField(blank=True, max_length=521, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='product_option_type_5',
            field=models.CharField(blank=True, max_length=521, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='product_option_type_6',
            field=models.CharField(blank=True, max_length=521, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='ribbon',
            field=models.CharField(blank=True, max_length=521, null=True),
        ),
        migrations.AlterField(
            model_name='wixproduct',
            name='sku',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]
