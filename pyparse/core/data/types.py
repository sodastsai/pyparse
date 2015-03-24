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
