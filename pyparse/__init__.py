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

import os

from pyparse.utils.lang import SingletonBase


class ParsePy(object, metaclass=SingletonBase):

    def __init__(self):
        self._application_id = None
        """:type: str"""
        self._rest_api_key = None
        """:type: str"""
        self._master_key = None
        """:type: str"""

    @property
    def application_id(self):
        """Get the application id used to call Parse REST API

        >>> import os
        >>> from pyparse import pyparse
        >>> os.environ['PARSE_APPLICATION_ID'] = 'TEST_ID'
        >>> pyparse.application_id == 'TEST_ID'
        True
        >>> del os.environ['PARSE_APPLICATION_ID']

        :return: the application id string
        :rtype: str
        """
        return self._application_id or os.environ.get('PARSE_APPLICATION_ID', None)

    @property
    def rest_api_key(self):
        """Get the rest api key used to call Parse REST API

        >>> import os
        >>> from pyparse import pyparse
        >>> os.environ['PARSE_REST_API_KEY'] = 'TEST_API_KEY'
        >>> pyparse.rest_api_key == 'TEST_API_KEY'
        True
        >>> del os.environ['PARSE_REST_API_KEY']

        :return: the rest api key string
        :rtype: str
        """
        return self._rest_api_key or os.environ.get('PARSE_REST_API_KEY', None)

    @property
    def master_key(self):
        """Get the master key used to call Parse REST API

        >>> import os
        >>> from pyparse import pyparse
        >>> os.environ['PARSE_MASTER_KEY'] = 'TEST_MASTER_KEY'
        >>> pyparse.master_key == 'TEST_MASTER_KEY'
        True
        >>> del os.environ['PARSE_MASTER_KEY']

        :return: the master key string
        :rtype: str
        """
        return self._master_key or os.environ.get('PARSE_MASTER_KEY', None)

    def setup(self, application_id=None, rest_api_key=None, master_key=None):
        """Setup PyParse with specified application id and rest api key

        >>> from pyparse import pyparse
        >>> pyparse.setup('TEST_APP_ID', 'TEST_API_KEY')
        >>> pyparse.application_id == 'TEST_APP_ID'
        True
        >>> pyparse.rest_api_key == 'TEST_API_KEY'
        True
        >>> pyparse.master_key is None
        True
        >>> pyparse.setup('TEST_APP_ID2', 'TEST_API_KEY2', 'TEST_MASTER_KEY')
        >>> pyparse.application_id == 'TEST_APP_ID2'
        True
        >>> pyparse.rest_api_key == 'TEST_API_KEY2'
        True
        >>> pyparse.master_key == 'TEST_MASTER_KEY'
        True

        :param application_id: the application id to be called
        :type application_id: str
        :param rest_api_key: the rest api key to be used
        :type rest_api_key: str
        :param master_key: the master key to be used
        :type master_key: str
        """
        assert application_id, 'application id should not be empty'
        assert rest_api_key, 'rest api key should not be empty'
        self._application_id = application_id
        self._rest_api_key = rest_api_key
        self._master_key = master_key


pyparse = ParsePy()
