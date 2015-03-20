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


class ParseObject(object):

    class_name = None
    """:type: str"""
    columns = ()
    """:type: tuple[str]"""
    _internal_columns = (
        'object_id',
    )
    """:type: tuple[str]"""

    @classmethod
    def get_class_name(cls):
        """
        :rtype: str
        """
        return cls.class_name or cls.__name__

    # Object and Property

    def __init__(self, **kwargs):
        self._content = kwargs
        """:type: dict"""

    @property
    def as_dict(self):
        """
        :rtype: dict
        """
        return dict(self._content)

    # Attribute interface

    @property
    def _readable_colums(self):
        return self.columns + self._internal_columns

    @property
    def _writable_colums(self):
        return self.columns

    def __getattr__(self, attr):
        if attr in self._readable_colums:
            return self._content.get(attr, None)
        else:
            object.__getattribute__(self, attr)

    def __setattr__(self, attr, value):
        if attr in self._writable_colums:
            self._content[attr] = value
        else:
            object.__setattr__(self, attr, value)

    def __delattr__(self, attr):
        if attr in self._writable_colums:
            del self._content[attr]
        else:
            object.__delattr__(self, attr)

    # Dict interface

    def __setitem__(self, key, value):
        if value is not None:
            self._content[key] = value
        else:
            del self._content[key]

    def __getitem__(self, key):
        return self._content.get(key, None)

    def __delitem__(self, key):
        if key in self._content:
            del self._content[key]

    def __contains__(self, key):
        return key in self._content

    def __iter__(self):
        for key in self._content:
            yield key

    def items(self):
        for kv_pair in six.iteritems(self._content):
            yield kv_pair

    def values(self):
        for value in six.itervalues(self._content):
            yield value

    def update(self, other, **kwargs):
        return self._content.update(other, **kwargs)
