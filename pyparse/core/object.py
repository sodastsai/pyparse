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
import dateutil.parser
from pyparse.core.fields import Field, DateTimeField
from pyparse.request import request
from pyparse.utils import camelcase
import six
from pyparse.core.query import Query


# noinspection PyUnresolvedReferences
class ObjectDictMixin(object):

    def __getitem__(self, key):
        return self._content.get(key, None)

    def __setitem__(self, key, value):
        field = self._fields.get(key, None)
        if field and field.readonly:
            raise KeyError('{} is a readonly field.'.format(key))

        if value is not None:
            self._content[key] = value
        else:
            del self._content[key]

    def __delitem__(self, key):
        field = self._fields.get(key, None)
        if field and field.readonly:
            raise KeyError('{} is a readonly field.'.format(key))

        if key in self._content:
            del self._content[key]

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
        readonly_keys = set([key for key in kwargs if key in self._readonly_fields])
        if other:
            readonly_keys |= set([key for key in other if key in self._readonly_fields])
        if len(readonly_keys) != 0:
            raise KeyError('{} is a readonly field.'.format(', '.join(readonly_keys)))

        return self._content.update(other, **kwargs)

    @property
    def as_dict(self):
        """
        :rtype: dict
        """
        return deepcopy(self._content)


class ObjectBase(type):

    anonymous_classes = {}

    def __new__(mcs, class_name, bases, class_dict):
        # Find field objects out from class_dict
        fields = {}
        """:type: dict[str, Field]"""
        final_class_dict = {}
        for attr_name, attr_obj in six.iteritems(class_dict):
            if isinstance(attr_obj, Field):
                attr_obj._python_name = attr_name
                # noinspection PyProtectedMember
                attr_obj._parse_name = attr_obj._parse_name or camelcase(attr_name)
                fields[attr_name] = attr_obj
            else:
                final_class_dict[attr_name] = attr_obj
        final_class_dict['_fields'] = fields

        # Setup class name and property
        final_class_dict['class_name'] = final_class_dict.get('class_name', class_name)
        final_class_dict['is_anonymous_class'] = False

        # Add fields back as value property
        for field_name, field in six.iteritems(fields):
            final_class_dict[field_name] = property(fget=mcs._getter(field),
                                                    fset=mcs._setter(field) if not field.readonly else None,
                                                    fdel=mcs._deleter(field) if not field.readonly else None)
        # Create class
        return type.__new__(mcs, class_name, bases, final_class_dict)

    def __call__(cls, *args, class_name=None, **kwargs):
        klass = cls
        if class_name:
            klass = ObjectBase.anonymous_classes.get(class_name, None)
            if not klass:
                # Create the object class
                klass = ObjectBase(class_name, (Object,), {})
                klass.is_anonymous_class = True
                ObjectBase.anonymous_classes[class_name] = klass
        return super(ObjectBase, klass).__call__(*args, **kwargs)

    @staticmethod
    def _getter(field):
        def getter(self):
            return self._content.get(field.parse_name, None)
        return getter

    @staticmethod
    def _setter(field):
        def setter(self, value):
            self._content[field.parse_name] = value
        return setter

    @staticmethod
    def _deleter(field):
        def deleter(self):
            if field.parse_name in self._content:
                del self._content[field.parse_name]
        return deleter


@six.add_metaclass(ObjectBase)
class Object(ObjectDictMixin, object):

    # Field

    object_id = Field(readonly=True)
    created_at = DateTimeField(readonly=True)
    updated_at = DateTimeField(readonly=True)

    _fields = None
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

        # Populate from kwargs
        python_key_fields = {field.python_name: field for field in six.itervalues(self._fields)}
        """:type: dict[str, Field]"""
        for key, value in six.iteritems(kwargs):
            field = python_key_fields.get(key, None)
            if field:
                key = field.parse_name
            self._content[key] = value

    # Parse SDK

    class_name = None

    @classmethod
    def from_parse(cls, raw_parse_object):
        """
        :type raw_parse_object: dict
        :rtype: Object
        """
        instance = cls()

        for field_name, value in six.iteritems(raw_parse_object):
            # noinspection PyProtectedMember
            # Use field object to convert value
            if field_name in cls._fields:
                # noinspection PyProtectedMember
                field = cls._fields[field_name]
                value = field.to_python(value)
            # Try to convert value by guessing
            else:
                final_value = value
                # Try date
                if isinstance(value, six.string_types) \
                        and ':' in value and 'T' in value and 'Z' in value and '-' in value:
                    # noinspection PyBroadException
                    try:
                        final_value = dateutil.parser.parse(value)
                    except Exception:
                        pass

                value = final_value

            instance._content[field_name] = value

        return instance

    def to_parse(self):
        pass

    # Fetch and query

    @classmethod
    def _remote_path(cls, object_id):
        return 'classes/{}/{}'.format(cls.class_name, object_id)

    @classmethod
    def get(cls, object_id):
        """
        :param object_id:
        :type object_id: str
        :return:
        :rtype: Object
        """
        return cls(content=request('get', cls._remote_path(object_id)))

    @classmethod
    def query(cls):
        """
        :return:
        :rtype: Query
        """
        return Query(cls)
