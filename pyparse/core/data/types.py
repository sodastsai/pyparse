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

_registered_parse_convertible_types = {}


class ParseConvertibleType(type):

    def __init__(cls, class_name, bases, class_dict):
        super(ParseConvertibleType, cls).__init__(class_name, bases, class_dict)

        if class_name != 'ParseConvertible':
            parse_type_name_func = getattr(cls, 'parse_type_name', None)
            if parse_type_name_func:
                _registered_parse_convertible_types[parse_type_name_func()] = cls


@six.add_metaclass(ParseConvertibleType)
class ParseConvertible(object):

    def to_parse(self):
        raise NotImplementedError('Implement how this type convet to Parse\'s representation.')

    @classmethod
    def to_python(cls, parse_dict):
        raise NotImplementedError('Implement how this type convet from Parse\'s representation.')

    @classmethod
    def parse_type_name(cls):
        raise NotImplementedError('Should return the __type value.')

    @staticmethod
    def guess_to_python(value):
        if isinstance(value, dict):
            try:
                klass = _registered_parse_convertible_types[value['__type']]
            except KeyError:
                pass
            else:
                return klass.to_python(value)
        return value

    @staticmethod
    def guess_to_parse(value):
        if isinstance(value, datetime.datetime):
            # Since createdAt and updatedAt won't use this guess_to_parse, it's safe to return dict directly
            return datetime_to_parse_dict(value)
        elif isinstance(value, ParseConvertible):
            return value.to_parse()

        return value


# == GeoPoint ==========================================================================================================

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
            '__type': self.parse_type_name(),
            'latitude': self.latitude,
            'longitude': self.longitude,
        }

    @classmethod
    def to_python(cls, parse_dict):
        if parse_dict['__type'] != cls.parse_type_name():
            raise TypeError('This is not a GeoPoint dict.')

        return cls(parse_dict['latitude'], parse_dict['longitude'])

    @classmethod
    def parse_type_name(cls):
        return 'GeoPoint'


# == datetime ==========================================================================================================

class UTC(datetime.tzinfo):

    @staticmethod
    def utcoffset(*args, **kwargs):
        return datetime.timedelta(0)

    @staticmethod
    def tzname(*args, **kwargs):
        return "UTC"

    @staticmethod
    def dst(*args, **kwargs):
        return datetime.timedelta(0)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return self.tzname()


class LocalTimezone(datetime.tzinfo):

    @staticmethod
    def utcoffset(*args, **kwargs):
        timedelta = datetime.datetime.now() - datetime.datetime.utcnow()
        return datetime.timedelta(minutes=round(timedelta.total_seconds()/60))

    @staticmethod
    def tzname(*args, **kwargs):
        return "<Local>"

    @staticmethod
    def dst(*args, **kwargs):
        return datetime.timedelta(0)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return self.tzname()


def datetime_to_parse_str(datetime_obj):
    """
    :type datetime_obj: datetime.datetime
    :rtype: str
    """
    if not datetime_obj.tzinfo:
        datetime_obj = datetime_obj.replace(tzinfo=LocalTimezone())
    return datetime_obj.astimezone(UTC()).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]+'Z'


def datetime_str_to_python(parse_str):
    """
    :type parse_str: str
    :rtype: datetime.datetime
    """
    return datetime.datetime.strptime(parse_str, '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=UTC())


def datetime_to_parse_dict(datetime_obj):
    """
    :type datetime_obj: datetime.datetime
    :rtype: dict
    """
    return {
        '__type': 'Date',
        'iso': datetime_to_parse_str(datetime_obj),
    }


def datetime_dict_to_python(parse_dict):
    """
    :type parse_dict: dict
    :rtype: datetime.datetime
    """
    if parse_dict['__type'] != 'Date':
        raise TypeError('This is not a Datetime dict.')

    return datetime_str_to_python(parse_dict['iso'])


class _DatetimeParseConverible(ParseConvertible):

    @classmethod
    def to_python(cls, parse_dict):
        return datetime_dict_to_python(parse_dict)

    @classmethod
    def parse_type_name(cls):
        return 'Date'

    def to_parse(self):
        # This class is just a wrapper for `guess_to_python`
        return None
