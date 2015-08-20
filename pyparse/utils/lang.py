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


class SingletonBase(type):
    """
    This metaclass helps you to create a class which always returns a singleton instance
    (i.e. there would be only one instance (shared) of this class)

    >>> class ClassA(object, metaclass=SingletonBase):
    ...     pass
    ...
    >>> class ClassB(object, metaclass=SingletonBase):
    ...     pass
    ...
    >>> class ClassC(object):
    ...     pass
    ...
    >>> a1 = ClassA()
    >>> a2 = ClassA()
    >>> b1 = ClassB()
    >>> b2 = ClassB()
    >>> c1 = ClassC()
    >>> c2 = ClassC()
    >>> a1 is a2
    True
    >>> b1 is b2
    True
    >>> c1 is c2
    False
    >>> a1 is b1
    False

    """

    def __init__(cls, *args, **kwargs):
        super(SingletonBase, cls).__init__(*args, **kwargs)
        cls._singleton_instance = None

    def __call__(cls, *args, **kwargs):
        if not cls._singleton_instance:
            cls._singleton_instance = super(SingletonBase, cls).__call__(*args, **kwargs)
        return cls._singleton_instance
