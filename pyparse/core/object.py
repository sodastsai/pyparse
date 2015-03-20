#
# Copyright 2015 Tickle Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import unicode_literals, division, absolute_import, print_function
import six
from pyparse import pyparse
from pyparse.core.base import DictFieldsMixin, AttrFieldsMixin
from pyparse.core.query import ParseQuery
from pyparse.utils import snakecase


class ParseObject(DictFieldsMixin, AttrFieldsMixin):

    # Parse Class

    class_name = None
    """:type: str"""

    @classmethod
    def get_class_name(cls):
        """
        :rtype: str
        """
        return cls.class_name or cls.__name__

    # Fields

    _readonly_fields = {
        'object_id' if pyparse.fields_using_snakecase else 'objectId',
        'created_at' if pyparse.fields_using_snakecase else 'createdAt',
        'updated_at' if pyparse.fields_using_snakecase else 'updatedAt',
    }

    # Object

    def __init__(self, **kwargs):
        self._content = kwargs
        """:type: dict"""

    # Parse dict

    @classmethod
    def from_parse(cls, raw_parse_object):
        """
        :type raw_parse_object: dict
        :rtype: ParseObject
        """
        instance = cls()

        for key, value in six.iteritems(raw_parse_object):
            if pyparse.fields_using_snakecase:
                key = snakecase(key)
            instance._content[key] = value

        return instance

    def to_parse(self):
        pass

    # Fetch and query

    @classmethod
    def get(cls, object_id):
        """
        :param object_id:
        :type object_id: str
        :return:
        :rtype: ParseObject
        """

    @classmethod
    def query(cls):
        """
        :return:
        :rtype: ParseQuery
        """
        return ParseQuery(cls)
