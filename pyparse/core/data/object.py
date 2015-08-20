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
from copy import deepcopy
from pyparse.core.data.base import ObjectBase
from pyparse.core.data.fields import Field, AutoDateTimeField
from pyparse.core.data.types import ParseConvertible
from pyparse.request import request
import six
from pyparse.core.data.query import Query


@six.add_metaclass(ObjectBase)
class Object(object):

    # Field

    object_id = Field(readonly=True)
    created_at = AutoDateTimeField(readonly=True)
    updated_at = AutoDateTimeField(readonly=True)

    _fields = None
    """:type: dict[str, Field]"""
    _fields_parse = None
    """:type: dict[str, Field]"""

    # Object

    is_anonymous_class = False

    @classmethod
    def from_object(cls, another_object):
        """
        :type another_object: Object
        :rtype: Object
        """
        assert cls.class_name == another_object.class_name, 'Parse class name of two objects is not the same.'
        return cls(content=another_object._content)

    def __init__(self, content=None, **kwargs):
        self._content = deepcopy(content) or {}
        """:type: dict"""

        # Populate from kwargs
        """:type: dict[str, Field]"""
        for key, value in six.iteritems(kwargs):
            field = self._fields.get(key, None)
            if field:
                key = field.parse_name
            self._content[key] = value

        self._modified_content = {}

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return repr(self._content)

    # Content

    @property
    def dirty(self):
        """:type: bool"""
        return bool(self._modified_content)

    def get(self, key):
        return self._content[key] if key in self._content else None

    def set(self, key, value):
        field = self._fields_parse.get(key, None)
        if field and field.readonly:
            raise KeyError('{} is a readonly field.'.format(key))

        if key not in self._modified_content:
            self._modified_content[key] = self.get(key)

        if value is not None:
            self._content[key] = value
        else:
            del self._content[key]

    # Parse SDK

    class_name = None

    @classmethod
    def from_parse(cls, raw_parse_object):
        """
        :type raw_parse_object: dict
        :rtype: Object
        """
        instance = cls()
        instance._content.update(cls._parse_dict_to_python(raw_parse_object))
        return instance

    @classmethod
    def _parse_dict_to_python(cls, raw_parse_dict):
        result = {}
        for field_name, value in six.iteritems(raw_parse_dict):
            # noinspection PyProtectedMember
            field = cls._fields_parse.get(field_name, None)
            if field:
                value = field.to_python(value)
            else:
                value = ParseConvertible.guess_to_python(value)
            result[field_name] = value
        return result

    # Field Action

    def increment(self, field_parse_name, step=1):
        if self.object_id:
            arguments = {
                field_parse_name: {
                    '__op': 'Increment',
                    'amount': step,
                }
            }
            response = request('put', self._remote_path(self.object_id), arguments=arguments)
            self._content.update(self._parse_dict_to_python(response))
        else:
            self.set(field_parse_name, self.get(field_parse_name)+step)

    # Remote

    @classmethod
    def _remote_path(cls, object_id):
        return 'classes/{}/{}'.format(cls.class_name, object_id)

    @classmethod
    def fetch(cls, object_id):
        """
        :param object_id:
        :type object_id: str
        :return:
        :rtype: Object
        """
        return cls.from_parse(request('get', cls._remote_path(object_id)))

    @classmethod
    def query(cls):
        """
        :return:
        :rtype: Query
        """
        return Query(cls)

    def save(self):
        if self.object_id:
            if not self.dirty:
                return

            # Update object
            payload = {}
            for modified_key, original_value in six.iteritems(self._modified_content):
                current_value = self.get(modified_key)
                if original_value != current_value:
                    payload[modified_key] = current_value
            if not payload:
                return

            remote_path = self._remote_path(self.object_id)
            verb = 'put'
        else:
            # Create object
            payload = self.as_dict
            remote_path = 'classes/{}'.format(self.class_name)
            verb = 'post'

        # Convert Python obj in payload to Parse obj
        final_payload = {}
        for key, value in six.iteritems(payload):
            field = self._fields_parse.get(key, None)
            if field:
                value = field.to_parse(value)
            else:
                value = ParseConvertible.guess_to_parse(value)
            final_payload[key] = value
        payload = final_payload

        response = request(verb, remote_path, arguments=payload)
        if self.object_id:
            # Updated - clean up
            self._modified_content = {}
        else:
            # New created - update info
            response['updatedAt'] = response['createdAt']

        self._content.update(self._parse_dict_to_python(response))

    def delete(self):
        if not self.object_id:
            return
        request('delete', self._remote_path(self.object_id))
        del self._content['objectId']

    # Dict

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, key):
        return key in self._content

    def __iter__(self):
        """
        :rtype: collections.Iterable[str]
        """
        for key in self._content:
            yield key

    def items(self):
        """
        :rtype: collections.Iterable[(str, object)]
        """
        for kv_pair in six.iteritems(self._content):
            yield kv_pair

    def keys(self):
        """
        :rtype: collections.Iterable[str]
        """
        for key in six.iterkeys(self._content):
            yield key

    def values(self):
        """
        :rtype: collections.Iterable[object]
        """
        for value in six.itervalues(self._content):
            yield value

    def update(self, other=None, **kwargs):
        """
        :type other: dict
        """
        update_dict = other or {}

        for field_name, value in six.iteritems(kwargs):
            field = self._fields.get(field_name, None)
            if field:
                key = field.parse_name
            else:
                key = field_name
            update_dict[key] = value

        for field_name, field in six.iteritems(self._fields_parse):
            if field.readonly and field.parse_name in update_dict:
                raise KeyError('{} is a readonly field.'.format(field.parse_name))

        return self._content.update(update_dict)

    @property
    def as_dict(self):
        """
        :rtype: dict
        """
        return deepcopy(self._content)
