# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import jsonfield.fields

from django.db import migrations, models

import enterprise.constants


class Migration(migrations.Migration):

    dependencies = [
        ('enterprise', '0030_auto_20171005_1600'),
    ]

    operations = [
        migrations.AddField(
            model_name='enterprisecustomercatalog',
            name='enabled_course_modes',
            field=jsonfield.fields.JSONField(default=enterprise.constants.json_serialized_course_modes, help_text='Ordered list of enrollment modes which can be displayed to learners for course runs in this catalog.'),
        ),
        migrations.AddField(
            model_name='historicalenterprisecustomercatalog',
            name='enabled_course_modes',
            field=jsonfield.fields.JSONField(default=enterprise.constants.json_serialized_course_modes, help_text='Ordered list of enrollment modes which can be displayed to learners for course runs in this catalog.'),
        ),
    ]
