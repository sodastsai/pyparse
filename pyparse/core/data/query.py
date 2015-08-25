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

from copy import copy
import json

from pyparse.core.data.types import ParseConvertible
from pyparse.core.data.object import ObjectBase
from pyparse.request import request_parse


class Query(object):

    def __init__(self, object_class=None, class_name=None):
        assert bool(object_class) ^ bool(class_name), 'You must assign either ObjectClass or ClassName.'

        self._object_class = object_class or ObjectBase.anonymous_class(class_name)
        # noinspection PyProtectedMember
        self._class_name = class_name or object_class.class_name or object_class.__name__

        self._arguments = {}
        self._order_list = []
        self._where_dict = {}

        # self._evaluated = False
        self._contents = None
        """:type: list[pyparse.core.data.object.Object] | None"""

    @property
    def evaluated(self):
        return self._contents is not None

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'Query: ' + repr(self.get_arguments())

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
        :rtype: Query
        """
        assert not self.evaluated, 'A {} object is immutable after evaluated'.format(self.__class__.__name__)
        return self

    _filter_operators = ('lt', 'lte', 'gt', 'gte', 'ne', 'in', 'nin', 'exists', 'select', 'dont_select', 'all', 'exact',
                         'near_sphere', 'max_distance_in_miles', 'max_distance_in_kilometers',
                         'max_distance_in_radians')

    def filter(self, **kwargs):
        """
        :return:
        :rtype: Query
        """
        assert not self.evaluated, 'A {} object is immutable after evaluated'.format(self.__class__.__name__)

        for key, value in kwargs.items():
            # Find keypaths and operators
            key_paths = key.split('__')
            if key_paths[-1] in self._filter_operators:
                *key_paths, operator = key_paths
            else:
                operator = 'exact'

            if len(key_paths) == 1:
                key = key_paths[0]

                # Check field for finding value transformer (to parse)
                # noinspection PyProtectedMember
                field = self._object_class._fields_python.get(key, None)
                if field:
                    key = field.parse_name
                    value_to_parse = field.to_parse
                else:
                    value_to_parse = ParseConvertible.guess_to_parse

                # Transform values
                if isinstance(value, (list, tuple)):
                    value = list(map(value_to_parse, value))
                else:
                    value = value_to_parse(value)

                # Update arguments dict
                if operator == 'exact':
                    self._where_dict[key] = value
                else:
                    key_query = self._where_dict.get(key, None)
                    if key_query is None:
                        key_query = {}
                        self._where_dict[key] = key_query
                    key_query['${}'.format(operator)] = value
            else:
                # TODO: relational?
                pass

        return self

    def order_by(self, *args):
        """
        :return:
        :rtype: Query
        """
        assert not self.evaluated, 'A {} object is immutable after evaluated'.format(self.__class__.__name__)
        self._order_list += args
        return self

    def limit(self, limit):
        """
        :return:
        :rtype: Query
        """
        assert not self.evaluated, 'A {} object is immutable after evaluated'.format(self.__class__.__name__)
        assert isinstance(limit, int) and 1 <= limit <= 1000, 'limit should be an integer between 1 and 1,000'
        self._arguments['limit'] = limit
        return self

    def offset(self, offset):
        """
        :return:
        :rtype: Query
        """
        assert not self.evaluated, 'A {} object is immutable after evaluated'.format(self.__class__.__name__)
        assert isinstance(offset, int) and offset > 0, 'offset should be a positive integer'
        self._arguments['skip'] = offset
        return self

    # Requests

    def get_arguments(self, **extra):
        """
        :rtype: dict
        """
        arguments = copy(self._arguments)

        if self._order_list:
            arguments['order'] = ','.join(self._order_list)
        if self._where_dict:
            arguments['where'] = json.dumps(self._where_dict, separators=(',', ':'))

        arguments.update(extra)
        return arguments

    @property
    def request_path(self):
        return 'classes/{}'.format(self._class_name)

    # Evaluate

    def __len__(self):
        return len(self.contents)

    def __iter__(self):
        """
        :rtype: collections.Iterable[pyparse.core.data.object.Object]
        """
        return self.contents.__iter__()

    @property
    def contents(self):
        """
        :rtype: list[pyparse.core.data.object.Object]
        """
        if not self.evaluated:
            self.fetch()

        return self._contents

    def fetch(self):
        assert not self.evaluated, 'A {} object is immutable after evaluated'.format(self.__class__.__name__)
        contents = request_parse('get', self.request_path, arguments=self.get_arguments())['results']

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
        return request_parse('get', self.request_path, arguments=self.get_arguments(count='1'))['count']
