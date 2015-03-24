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


class SingletonBase(type):

    def __init__(cls, *args, **kwargs):
        super(SingletonBase, cls).__init__(*args, **kwargs)
        cls._singleton_instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._singleton_instance:
            cls._singleton_instance = super(SingletonBase, cls).__call__(*args, **kwargs)
        return cls._singleton_instance
