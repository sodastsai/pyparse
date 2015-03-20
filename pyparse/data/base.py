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


class FieldsMixin(object):

    fields = set()
    """:type: set[str]"""
    _readonly_fields = set()
    """:type: set[str]"""

    @property
    def _fields(self):
        """
        :rtype: set[str]
        """
        return self.fields | self._readonly_fields

    @property
    def _writable_fields(self):
        """
        :rtype: set[str]
        """
        return self.fields


class DictFieldsMixin(FieldsMixin):

    _content = {}

    def __getitem__(self, key):
        return self._content.get(key, None)

    def __setitem__(self, key, value):
        if key in self._readonly_fields:
            raise KeyError('{} is a readonly field.'.format(key))

        if value is not None:
            self._content[key] = value
        else:
            del self._content[key]

    def __delitem__(self, key):
        if key in self._readonly_fields:
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


class AttrFieldsMixin(FieldsMixin):

    _content = {}

    def __getattr__(self, attr):
        if attr in self._fields:
            return self._content.get(attr, None)
        else:
            object.__getattribute__(self, attr)

    def __setattr__(self, attr, value):
        if attr in self._writable_fields:
            self._content[attr] = value
        elif attr in self._readonly_fields:
            raise KeyError('{} is a readonly field.'.format(attr))
        else:
            object.__setattr__(self, attr, value)

    def __delattr__(self, attr):
        if attr in self._writable_fields:
            del self._content[attr]
        elif attr in self._readonly_fields:
            raise KeyError('{} is a readonly field.'.format(attr))
        else:
            object.__delattr__(self, attr)
