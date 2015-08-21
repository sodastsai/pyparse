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

from copy import deepcopy

from pyparse.core.data.base import ObjectBase
from pyparse.core.data.fields import Field, AutoDateTimeField
from pyparse.core.data.types import ParseConvertible
from pyparse.request import request_parse
from pyparse.core.data.query import Query


class Object(object, metaclass=ObjectBase):
    """
    key: parse_key
    """

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

        self._update(kwargs, check_readonly=False, update_dirty_state=False)
        self._original_value_of_modified_content = {}

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return repr(self._content)

    # Content

    @property
    def dirty(self):
        """:type: bool"""
        return len(self._original_value_of_modified_content) != 0

    def get(self, key):
        return self._content[key] if key in self._content else None

    def set(self, key, value):
        self._set(key, value)

    def _set(self, key, value, check_readonly=True):
        if check_readonly:
            field = self._fields_parse.get(key, None)
            if field and field.readonly:
                raise KeyError('{} is a readonly field.'.format(key))

        if key not in self._original_value_of_modified_content:
            self._original_value_of_modified_content[key] = self.get(key)

        if value is not None:
            self._content[key] = value
        else:
            del self._content[key]

    # Parse SDK

    class_name = None

    @classmethod
    def from_parse(cls, raw_parse_dict):
        """
        :type raw_parse_dict: dict
        :rtype: Object
        """
        return cls(cls._parse_dict_to_python_value_dict(raw_parse_dict))

    @classmethod
    def _parse_dict_to_python_value_dict(cls, raw_parse_dict):
        return {key: cls._to_python_converter(key)(value) for key, value in raw_parse_dict.items()}

    # Fields

    def increment(self, field_parse_name, step=1):
        if self.object_id:
            arguments = {
                field_parse_name: {
                    '__op': 'Increment',
                    'amount': step,
                }
            }
            response = request_parse('put', self._remote_path(self.object_id), arguments=arguments)
            self._update(self._parse_dict_to_python_value_dict(response),
                         check_readonly=False, update_dirty_state=False)
        else:
            self.set(field_parse_name, self.get(field_parse_name)+step)

    @classmethod
    def _to_parse_converter(cls, field_name):
        return cls._fields_parse[field_name].to_parse \
            if field_name in cls._fields_parse else ParseConvertible.guess_to_parse

    @classmethod
    def _to_python_converter(cls, field_name):
        return cls._fields_parse[field_name].to_python \
            if field_name in cls._fields_parse else ParseConvertible.guess_to_python

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
        return cls.from_parse(request_parse('get', cls._remote_path(object_id)))

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
            for modified_key, original_value in self._original_value_of_modified_content.items():
                current_modified_value = self.get(modified_key)
                if original_value != current_modified_value:
                    payload[modified_key] = current_modified_value
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
        payload = {key: self._to_parse_converter(key)(value) for key, value in payload.items()}

        response = request_parse(verb, remote_path, arguments=payload)
        if self.object_id:
            # Updated - clean up
            self._original_value_of_modified_content = {}
        else:
            # New created - update info
            response['updatedAt'] = response['createdAt']

        self._content.update(self._parse_dict_to_python_value_dict(response))

    def delete(self):
        if not self.object_id:
            return
        request_parse('delete', self._remote_path(self.object_id))
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
        return self._content.__iter__()

    def items(self):
        """
        :rtype: collections.Iterable[(str, object)]
        """
        return self._content.items()

    def keys(self):
        """
        :rtype: collections.Iterable[str]
        """
        return self._content.keys()

    def values(self):
        """
        :rtype: collections.Iterable[object]
        """
        return self._content.values()

    def update(self, other=None, **kwargs):
        self._update(other=other, **kwargs)

    def _update(self, update_dict, check_readonly=True, update_dirty_state=True, **kwargs):
        """
        :type other: dict
        """
        for field_name, value in kwargs.items():
            field = self._fields.get(field_name, None)
            if field:
                key = field.parse_name
            else:
                key = field_name
            update_dict[key] = value

        if check_readonly:
            for field_name, field in self._fields_parse.items():
                if field.readonly and field.parse_name in update_dict:
                    raise KeyError('{} is a readonly field.'.format(field.parse_name))

        if update_dirty_state:
            for key, value in update_dict.items():
                self._set(key, value, check_readonly=check_readonly)
        else:
            return self._content.update(update_dict)

    @property
    def as_dict(self):
        """
        :rtype: dict
        """
        return deepcopy(self._content)
