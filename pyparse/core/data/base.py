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
from functools import partial
import os
import six
from pyparse.core.data.fields import Field, NumberField
from pyparse.utils.strings import camelcase

_parse_object__module__ = __package__ + '.' + os.path.splitext('object.py')[0]


class ObjectBase(type):

    anonymous_classes = {}

    def __new__(mcs, class_name, bases, class_dict):
        # Find field objects out from class_dict
        fields = {}
        """:type: dict[str, Field]"""
        fields_parse = {}
        """:type: dict[str, Field]"""
        final_class_dict = {}
        for attr_name, attr_obj in six.iteritems(class_dict):
            if isinstance(attr_obj, Field):
                attr_obj._python_name = attr_name
                # noinspection PyProtectedMember
                attr_obj._parse_name = attr_obj._parse_name or camelcase(attr_name)

                fields[attr_obj.python_name] = attr_obj
                fields_parse[attr_obj.parse_name] = attr_obj
            else:
                final_class_dict[attr_name] = attr_obj
        final_class_dict['_fields'] = fields
        final_class_dict['_fields_parse'] = fields_parse

        # Update fields from bases

        if class_dict.get('__module__', None) != _parse_object__module__ and class_name != 'Object':
            from pyparse.core import Object
            for base in bases:
                if issubclass(base, Object):
                    # noinspection PyProtectedMember
                    final_class_dict['_fields'].update(base._fields)
                    # noinspection PyProtectedMember
                    final_class_dict['_fields_parse'].update(base._fields_parse)

        # Setup class name and property
        final_class_dict['class_name'] = final_class_dict.get('class_name', class_name)
        final_class_dict['is_anonymous_class'] = False

        # Add fields back as value property
        for field_name, field in six.iteritems(fields):
            final_class_dict[field_name] = property(
                fget=mcs._getter(field),
                fset=mcs._setter(field) if not field.readonly else None
            )
        # Create class
        return type.__new__(mcs, class_name, bases, final_class_dict)

    @staticmethod
    def _getter(field):
        def getter(self):
            return self.get(field.parse_name)
        return getter

    @staticmethod
    def _setter(field):
        def setter(self, value):
            return self.set(field.parse_name, value)
        return setter

    @classmethod
    def anonymous_class(mcs, class_name):
        klass = mcs.anonymous_classes.get(class_name, None)
        if not klass:
            from pyparse.core import Object

            klass = mcs(class_name, (Object,), {'__module__': _parse_object__module__ + '.anonymous'})
            klass.is_anonymous_class = True
            mcs.anonymous_classes[class_name] = klass
        return klass

    def __call__(cls, *args, class_name=None, **kwargs):
        klass = super(ObjectBase, cls if not class_name else cls.anonymous_class(class_name)).__call__(*args, **kwargs)

        # noinspection PyProtectedMember
        fields = klass._fields
        """:type: dict[str, Field]"""

        # Setup incrementable fields
        for field_name, field in six.iteritems(fields):
            if isinstance(field, NumberField):
                setattr(klass, 'increment_{}'.format(field_name), partial(klass.increment, field.parse_name))

        return klass
