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
from copy import copy
from pyparse.request import request


class ParseQuery(object):

    def __init__(self, object_class=None, class_name=None):
        assert object_class or class_name, 'You must assign at least one of ObjectClass and ClassName'

        self._object_class = object_class
        self._class_name = class_name or object_class.get_class_name()
        self._contents = []
        self._arguments = {}
        self._evaluated = False

    @property
    def evaluated(self):
        return self._evaluated

    # Object func

    def __getitem__(self, key):
        if isinstance(key, slice) and not key.step:
            return self.offset(key.start).limit(key.stop - key.start)
        else:
            if not self.evaluated:
                self.fetch()
            return self._contents[key]

    def __getslice__(self, i, j):  # Python 2
        return self.__getitem__(slice(i, j))

    # Queries

    def all(self):
        """
        :return:
        :rtype: ParseQuery
        """
        assert not self._evaluated, 'A {} object is immutable after evaluated'.format(self.__class__.__name__)
        return self

    def filter(self, **kwargs):
        """
        :return:
        :rtype: ParseQuery
        """
        assert not self._evaluated, 'A {} object is immutable after evaluated'.format(self.__class__.__name__)
        return self

    def order_by(self, *args):
        """
        :return:
        :rtype: ParseQuery
        """
        assert not self._evaluated, 'A {} object is immutable after evaluated'.format(self.__class__.__name__)

        order_list = self._arguments.get('order', None)
        if order_list is None:
            order_list = []
            self._arguments['order'] = order_list
        order_list += args
        return self

    def limit(self, limit):
        """
        :return:
        :rtype: ParseQuery
        """
        assert not self._evaluated, 'A {} object is immutable after evaluated'.format(self.__class__.__name__)
        assert isinstance(limit, int) and 1 <= limit <= 1000, 'limit should be an integer between 1 and 1,000'
        self._arguments['limit'] = limit
        return self

    def offset(self, offset):
        """
        :return:
        :rtype: ParseQuery
        """
        assert not self._evaluated, 'A {} object is immutable after evaluated'.format(self.__class__.__name__)
        assert isinstance(offset, int) and offset > 0, 'offset should be a positive integer'
        self._arguments['skip'] = offset
        return self

    # Requests

    def _get_arguments(self, **extra):
        arguments = copy(self._arguments)

        if 'order' in arguments:
            arguments['order'] = ','.join(arguments['order'])

        arguments.update(extra)
        return arguments

    @property
    def _request_path(self):
        return 'classes/{}'.format(self._class_name)

    # Evaluate

    def __len__(self):
        if not self.evaluated:
            self.fetch()
        return len(self._contents)

    def __iter__(self):
        """
        :return:
        :rtype: collections.Iterable
        """
        if not self.evaluated:
            self.fetch()
        for parse_object in self._contents:
            yield parse_object

    def fetch(self):
        assert not self._evaluated, 'A {} object is immutable after evaluated'.format(self.__class__.__name__)
        contents = request('get', self._request_path, arguments=self._get_arguments())['results']

        if self._object_class:
            self._contents = [self._object_class.from_parse(content) for content in contents]
        else:
            self._contents = contents

        return self

    # Annotation/Aggregation

    def count(self):
        """
        Get the number of objects satisfying this query
        :return: the number of all objects which satisfy this query
        :rtype: int
        """
        return request('get', self._request_path, arguments=self._get_arguments(count='1'))['count']
