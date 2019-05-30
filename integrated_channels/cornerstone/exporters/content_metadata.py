# -*- coding: utf-8 -*-
"""
Content metadata exporter for Cornerstone.
"""

from __future__ import absolute_import, unicode_literals

import datetime
import math
from logging import getLogger

import pytz

from django.apps import apps

from enterprise.utils import get_closest_course_run
from integrated_channels.integrated_channel.exporters.content_metadata import ContentMetadataExporter

LOGGER = getLogger(__name__)


class CornerstoneContentMetadataExporter(ContentMetadataExporter):  # pylint: disable=abstract-method
    """
    Cornerstone implementation of ContentMetadataExporter.
    """
    LONG_STRING_LIMIT = 10000
    DEFAULT_SUBJECT = "Industry Specific"
    DATA_TRANSFORM_MAPPING = {
        'ID': 'key',
        'Title': 'title',
        'Description': 'description',
        'Thumbnail': 'card_image_url',
        'URL': 'enrollment_url',
        'IsActive': 'is_active',
        'LastModifiedUTC': 'modified',
        'Duration': 'estimated_hours',
        'Owners': 'organizations',
        'Languages': 'languages',
        'Subjects': 'subjects',
    }

    def transform_organizations(self, content_metadata_item):
        """
        Return the transformed version of the course organizations
        by converting each organization into cornerstone course owner object.
        """
        owners = []
        for org in content_metadata_item.get('organizations', []):
            org_name = org[:500] if org else ''
            owners.append({"Name": org_name})
        return owners

    def transform_is_active(self, content_metadata_item):
        """
        Return the transformed version of the course is_active status
        by traversing course runs and setting IsActive to True if any of the course
        runs have availability value set to `Current`, `Starting Soon` or `Upcoming`.
        """
        is_active = False
        for course_run in content_metadata_item.get('course_runs', []):
            if course_run.get('availability') in ['Current', 'Starting Soon', 'Upcoming']:
                is_active = True
                break
        return is_active

    def transform_modified(self, content_metadata_item):
        """
        Return the modified datetime of closest course run`.
        """
        modified_datetime = datetime.datetime.now(pytz.UTC)
        course_runs = content_metadata_item.get('course_runs')
        if course_runs:
            closest_course_run = get_closest_course_run(course_runs)
            modified_datetime = closest_course_run.get('modified', modified_datetime)

        return str(modified_datetime)

    def transform_estimated_hours(self, content_metadata_item):
        """
        Return the duration of course in hh:mm:ss format.
        """
        duration = None
        course_runs = content_metadata_item.get('course_runs')
        if course_runs:
            closest_course_run = get_closest_course_run(course_runs)
            estimated_hours = closest_course_run.get('estimated_hours')
            if estimated_hours and isinstance(estimated_hours, (int, float)):
                fraction, whole_number = math.modf(estimated_hours)
                hours = "{:02d}".format(int(whole_number))
                minutes = "{:02d}".format(int(60 * fraction))
                duration = "{hours}:{minutes}:00".format(hours=hours, minutes=minutes)

        return duration

    def transform_languages(self, content_metadata_item):
        """
        Return the languages supported by course or `English` as default if no languages found.
        """
        return content_metadata_item.get('languages', ['English'])

    def transform_description(self, content_metadata_item):
        """
        Return the transformed version of the course description.

        We choose one value out of the course's full description, short description, and title
        depending on availability and length limits.
        """
        full_description = content_metadata_item.get('full_description') or ''
        if 0 < len(full_description) <= self.LONG_STRING_LIMIT:  # pylint: disable=len-as-condition
            return full_description
        return content_metadata_item.get('short_description') or content_metadata_item.get('title') or ''

    def transform_subjects(self, content_metadata_item):
        """
        Return the transformed version of the course subject list.
        """
        subjects = []
        course_subjects = content_metadata_item.get('subjects', [])
        CornerstoneGlobalConfiguration = apps.get_model(  # pylint: disable=invalid-name
            'cornerstone',
            'CornerstoneGlobalConfiguration'
        )
        subjects_mapping_dict = CornerstoneGlobalConfiguration.current().subject_mapping or {}
        for subject in course_subjects:
            for cornerstone_subject, edx_subjects in subjects_mapping_dict.items():
                if subject.lower() in [edx_subject.lower() for edx_subject in edx_subjects]:
                    subjects.append(cornerstone_subject)
        return list(set(subjects)) or [self.DEFAULT_SUBJECT] if course_subjects else []