# Generated by Django 4.0.4 on 2022-09-16 19:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bot_api', '0007_alter_order_execution_status_alter_order_pay_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='botusers',
            name='last_shipping_address',
        ),
        migrations.RemoveField(
            model_name='order',
            name='need_milling',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipping',
        ),
        migrations.RemoveField(
            model_name='orderarchive',
            name='need_milling',
        ),
        migrations.RemoveField(
            model_name='orderarchive',
            name='shipping',
        ),
    ]
