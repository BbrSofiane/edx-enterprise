# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-19 16:46


import uuid

from django.db import migrations, models


def create_uuid(apps, schema_editor):
    reporting_config = apps.get_model('enterprise', 'EnterpriseCustomerReportingConfiguration')
    for config in reporting_config.objects.all():
        config.uuid = uuid.uuid4()
        config.save()


class Migration(migrations.Migration):

    dependencies = [
        ('enterprise', '0072_add_enterprise_report_config_feature_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='enterprisecustomerreportingconfiguration',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, blank=True, null=True),
        ),
        migrations.RunPython(create_uuid, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='enterprisecustomerreportingconfiguration',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, unique=True)
        ),
    ]
