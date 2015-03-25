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
import datetime
import six


class ParseConvertible(object):

    def to_parse(self):
        raise NotImplementedError('Implement how this type convet to Parse\'s representation.')

    @classmethod
    def to_python(cls, parse_dict):
        raise NotImplementedError('Implement how this type convet from Parse\'s representation.')


class GeoPoint(ParseConvertible):
    """
    A class used to represent GeoPoint data
    """

    def __init__(self, latitude, longitude):
        """
        Create a GeoPoint data
        :param latitude: the latitude of this point
        :type latitude: float
        :param longitude: the longitude of this point
        :type longitude: float
        """
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return 'GeoPoint({0.latitude}, {0.longitude})'.format(self)

    def to_parse(self):
        return {
            '__type': 'GeoPoint',
            'latitude': self.latitude,
            'longitude': self.longitude,
        }

    @classmethod
    def to_python(cls, parse_dict):
        if parse_dict['__type'] != 'GeoPoint':
            raise TypeError('This is not a GeoPoint dict.')

        return cls(parse_dict['latitude'], parse_dict['longitude'])


def datetime_to_parse_str(datetime_obj):
    """
    :type datetime_obj: datetime.datetime
    :rtype: str
    """
    return datetime_obj.isoformat()[:-3]+'Z'


def datetime_to_parse_dict(datetime_obj):
    """
    :type datetime_obj: datetime.datetime
    :rtype: dict
    """
    return {
        '__type': 'Date',
        'iso': datetime_to_parse_str(datetime_obj),
    }


def datetime_str_to_python(parse_str):
    """
    :type parse_str: str
    :rtype: datetime.datetime
    """
    return datetime.datetime.strptime(parse_str, '%Y-%m-%dT%H:%M:%S.%fZ')


def datetime_dict_to_python(parse_dict):
    """
    :type parse_dict: dict
    :rtype: datetime.datetime
    """
    if parse_dict['__type'] != 'Date':
        raise TypeError('This is not a GeoPoint dict.')

    return datetime_str_to_python(parse_dict['iso'])


def guess_to_python(value):
    if isinstance(value, six.string_types):
        if ':' in value and 'T' in value and 'Z' in value and '-' in value:
            try:
                return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                pass
    elif isinstance(value, dict):
        value_type = value.get('__type', None)
        if value_type == 'GeoPoint':
            return GeoPoint.to_python(value)
        elif value_type == 'Date':
            return datetime_dict_to_python(value)

    return value


def guess_to_parse(value):
    if isinstance(value, datetime.datetime):
        # Since createdAt and updatedAt won't use this guess_to_parse, it's safe to return dict directly
        return datetime_to_parse_dict(value)
    elif isinstance(value, ParseConvertible):
        return value.to_parse()

    return value
