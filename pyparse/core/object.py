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
import dateutil.parser
from pyparse.core.fields import Field, DateTimeField
import six
from pyparse.core.query import Query


class ObjectBase(type):

    def __new__(mcs, class_name, bases, class_dict):
        # Find fields out from class_dict
        fields = {}
        """:type: dict[str, Field]"""
        final_class_dict = {}
        for attr_name, attr_obj in six.iteritems(class_dict):
            if isinstance(attr_obj, Field):
                fields[attr_name] = attr_obj
                attr_obj._python_name = attr_name
            else:
                final_class_dict[attr_name] = attr_obj
        final_class_dict['_fields'] = fields

        # Create class
        klass = type.__new__(mcs, class_name, bases, final_class_dict)

        # Add fields back
        for field_name, field in six.iteritems(fields):
            setattr(klass, field_name, property(fget=mcs._getter(field_name),
                                                fset=mcs._setter(field_name) if not field.readonly else None,
                                                fdel=mcs._deleter(field_name) if not field.readonly else None))

        return klass

    @staticmethod
    def _getter(key):
        def getter(self):
            return self._content.get(key, None)
        return getter

    @staticmethod
    def _setter(key):
        def setter(self, value):
            self._content[key] = value
        return setter

    @staticmethod
    def _deleter(key):
        def deleter(self):
            del self._content[key]
        return deleter


@six.add_metaclass(ObjectBase)
class Object(object):

    # Field

    object_id = Field('objectId', readonly=True)
    created_at = DateTimeField('createdAt', readonly=True)
    updated_at = DateTimeField('updatedAt', readonly=True)

    # Parse Class

    class_name = None
    """:type: str"""

    @classmethod
    def get_class_name(cls):
        """
        :rtype: str
        """
        return cls.class_name or cls.__name__

    # Object

    def __init__(self, **kwargs):
        self._content = kwargs

    # Dict interface

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
        return dict(self._content)

    # Parse dict

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
                if isinstance(value, six.string_types) \
                        and ':' in value and 'T' in value and 'Z' in value and '-' in value:
                    # noinspection PyBroadException
                    try:
                        value = dateutil.parser.parse(value)
                    except Exception:
                        value = value

            instance._content[field_name] = value

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
        :rtype: Object
        """

    @classmethod
    def query(cls):
        """
        :return:
        :rtype: Query
        """
        return Query(cls)
