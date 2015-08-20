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

from pyparse.request import request
from pyparse.utils.lang import SingletonBase


class Config(object, metaclass=SingletonBase):

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
        return self._content.__iter__()

    def items(self):
        """
        :rtype: collections.Iterable[(str, object)]
        """
        return self._content.items()

    def values(self):
        """
        :rtype: collections.Iterable[object]
        """
        return self._content.values()

    @property
    def as_dict(self):
        return deepcopy(self._content)
