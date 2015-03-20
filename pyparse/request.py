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
from . import pyparse
from copy import copy
import json
import requests
from pyparse.error import ParseInternalServerError, ParseError


class ParseRequest(object):

    SCHEME = 'https'
    HOST = 'api.parse.com'
    VERSION = '1'

    @classmethod
    def generate_url(cls, path):
        """Generate URL used to request for object/collections

        To get url of object with object id <objectId> and class named <className>,
        just call ```ParseRequest.generate_url('classes/<className>/<objectId>')```

        Reference: https://www.parse.com/docs/rest#general-quick

        :param path: the path of object/collection
        :type path: str
        :return: a url string representing the object/collection at Parse's server
        :rtype: str
        """
        if path.startswith('/'):
            path = path[1:]
        return '{scheme}://{host}/{version}/{path}'.format(
            scheme=cls.SCHEME,
            host=cls.HOST,
            version=cls.VERSION,
            path=path,
        )

    @staticmethod
    def authentication_headers():
        """Get the header with authenticate credentials used to call Parse REST API
        :return: a dict contains authentication header fields and corresponding values
        :rtype: dict
        """
        application_id = pyparse.application_id
        rest_api_key = pyparse.rest_api_key
        assert application_id, 'application id should not be empty'
        assert rest_api_key, 'rest api key should not be empty'

        return {
            'X-Parse-Application-Id': application_id,
            'X-Parse-REST-API-Key': rest_api_key,
        }

    # Object

    def __init__(self, path, arguments=None, headers=None):
        self._path = path
        """:type: str"""
        self._arguments = arguments
        """:type: dict"""
        self._headers = headers or {}
        """:type: dict"""

    @property
    def url(self):
        return self.generate_url(self._path)

    @property
    def arguments(self, use_json=False):
        if use_json and self._arguments:
            return json.dumps(self._arguments, separators=(',', ':'))
        return self._arguments

    @property
    def headers(self, post=False):
        header = copy(self._headers)
        header.update(self.authentication_headers())

        if post:
            header.update({'Content-Type': 'application/json'})

        return header

    # Request and response

    @staticmethod
    def _request(verb, url, *args, **kwargs):
        """
        :rtype: dict
        """
        assert verb in ('get', 'post', 'put', 'delete'), 'verb only accepts get, post, put, and delete'

        response = getattr(requests, verb)(url, *args, **kwargs)
        """:type: requests.models.Response"""

        response_dict = response.json()
        if response.status_code >= 500:
            raise ParseInternalServerError(response_dict['code'], response_dict['error'])
        elif response.status_code >= 400:
            raise ParseError(response_dict['code'], response_dict['error'])
        else:
            return response_dict

    # HTTP Verbs

    def get(self):
        """
        :rtype: dict
        """
        return self._request('get', self.url, params=self.arguments, headers=self.headers)

    def post(self):
        """
        :rtype: dict
        """
        return self._request('post', self.url, data=self.arguments(use_json=True), headers=self.headers(post=True))

    def put(self):
        """
        :rtype: dict
        """
        return self._request('put', self.url, data=self.arguments(use_json=True), headers=self.headers(post=True))

    def delete(self):
        """
        :rtype: dict
        """
        return self._request('delete', self.url, params=self.arguments, headers=self.headers)


def request(verb, path, arguments=None, headers=None):
    """Request with Parse REST API
    :param verb: HTTP verb used for this request. (should be get, post, put, or delete)
    :type: str
    :param path: the path of a Parse object or collection
    :type: str
    :param arguments: arguments used to request with a Parse object or collection
    :type: dict
    :param headers: headers used to request with a Parse object or collection
    :type: dict
    :return: the response of this request
    :rtype: dict
    """
    assert verb in ('get', 'post', 'put', 'delete'), 'verb only accepts get, post, put, and delete'
    return getattr(ParseRequest(path=path, arguments=arguments, headers=headers), verb)()
