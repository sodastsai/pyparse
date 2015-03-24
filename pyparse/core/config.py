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
from pyparse.request import request
from pyparse.utils.lang import SingletonBase
import six


@six.add_metaclass(SingletonBase)
class Config(object):

    def __init__(self):
        super(Config, self).__init__()
        self._content = {}

        self.fetch()

    def fetch(self):
        self._content.update(request('get', 'config')['params'])

    def __repr__(self):
        return repr(self._content)

    def __str__(self):
        return repr(self)

    def __getitem__(self, key):
        return self._content.get(key, None)

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

    @property
    def as_dict(self):
        return deepcopy(self._content)
