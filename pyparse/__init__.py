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
import os


class _ParsePy(object):

    def __init__(self):
        self._application_id = None
        """:type: str"""
        self._rest_api_key = None
        """:type: str"""
        self.fields_using_snakecase = False
        """:type: bool"""

    @property
    def application_id(self):
        """Get the application id used to call Parse REST API
        :return: the application id string
        :rtype: str
        """
        return self._application_id or os.environ.get('PARSE_APPLICATION_ID', None)

    @property
    def rest_api_key(self):
        """Get the rest api key used to call Parse REST API
        :return: the rest api key string
        :rtype: str
        """
        return self._rest_api_key or os.environ.get('PARSE_REST_API_KEY', None)

    def setup(self, application_id=None, rest_api_key=None):
        """Setup PyParse with specified application id and rest api key
        :param application_id: the application id to be call
        :type application_id: str
        :param rest_api_key: the rest api key to be used
        :type rest_api_key: str
        """
        assert application_id, 'application id should not be empty'
        assert rest_api_key, 'rest api key should not be empty'
        self._application_id = application_id
        self._rest_api_key = rest_api_key


pyparse = _ParsePy()
