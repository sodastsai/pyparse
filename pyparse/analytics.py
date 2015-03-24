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
from pyparse.request import request
from pyparse.utils.date import to_parse_iso8601
from pyparse.utils.strings import snakify
import six


class Analytics(object):

    @classmethod
    def track(cls, event, at=None, **dimensions):
        """
        :param event:
        :type event: str
        :param at:
        :type at: datetime.datetime
        :param dimensions:
        :type dimensions: dict[str, object]
        """
        if len(dimensions) > 8:
            raise ValueError('Parse only support at most 8 dimensions per event')

        dimensions = {snakify(key): snakify(six.text_type(value)) for key, value in six.iteritems(dimensions)}
        event = snakify(event)

        arguments = {}
        if dimensions:
            arguments['dimensions'] = dimensions
        if at:
            arguments['at'] = {
                '__type': 'Date',
                'iso': to_parse_iso8601(at),
            }

        return request('post', 'events/{}'.format(event), arguments=arguments)

    @classmethod
    def app_opened(cls, at=None):
        return cls.track('AppOpened', at=at)
