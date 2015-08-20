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

import re


_underscore_prefix_letter_pattern = re.compile(r'_([a-z])')
_uppercase_letter_pattern = re.compile(r'([A-Z])')
_space_pattern = re.compile(r'\s+')


def camelcase(snakecase_string, capitalize_head=False):
    """
    >>> camelcase('abc_def')
    'abcDef'

    >>> camelcase('abc_def', True)
    'AbcDef'
    >>> # Random test generator
    >>> import string, random
    >>> test_str = ''
    >>> test_ans = ''
    >>> rand_char = ''
    >>> upper = False
    >>> # Make first char upper or lowercase
    >>> if random.choice([True, False]):
    ...     rand_char = random.choice(string.ascii_uppercase)
    ...     test_str = rand_char.lower()
    ...     test_ans = rand_char
    ...     upper = True
    ... else:
    ...     rand_char = random.choice(string.ascii_lowercase)
    ...     test_str = rand_char.lower()
    ...     test_ans = rand_char
    ...     upper = False
    >>> # Generate rest of string
    >>> for x in range(1, 10):
    ...     rand_char = random.choice(string.ascii_lowercase)
    ...     if random.choice([True, False]):
    ...         test_str += '_'
    ...         test_str += rand_char
    ...         test_ans += rand_char.upper()
    ...     else:
    ...         test_str += rand_char
    ...         test_ans += rand_char
    >>> camelcase(test_str, upper) == test_ans
    True

    :type snakecase_string: str
    :rtype: str
    """
    result = _underscore_prefix_letter_pattern.sub(lambda x: x.group(1).upper(), snakecase_string)
    if capitalize_head:
        result = result[0].upper() + result[1:]
    return result


def snakecase(camelcase_string):
    """
    >>> snakecase('abc')
    'abc'
    >>> snakecase('abcDef')
    'abc_def'


    >>> # Random test generator
    >>> import string, random
    >>> rand_char = random.choice(string.ascii_lowercase)
    >>> test_ans = rand_char
    >>> test_str = rand_char
    >>> # Generate rest of string
    >>> for x in range(1, 10):
    ...
    ...     rand_char = random.choice(string.ascii_lowercase)
    ...     if random.choice([True, False]):
    ...         test_ans += '_'
    ...         test_ans += rand_char
    ...         test_str += rand_char.upper()
    ...     else:
    ...         test_ans += rand_char
    ...         test_str += rand_char
    >>> snakecase(test_str) == test_ans
    True

    :type camelcase_string: str
    :rtype: str
    """
    return _uppercase_letter_pattern.sub(lambda x: ('_' if x.start() else '') + x.group(0), camelcase_string).lower()


def snakify(string, lowercase=True):
    """
    >>> import string, random
    >>> test_str = ''
    >>> test_ans = ''
    >>> rand_char = ''
    >>> for x in range(1, 10):
    ...     rand_char = random.choice(string.ascii_letters)
    ...     test_ans += rand_char
    ...     test_str += rand_char
    >>> for pos in range(len(test_str) - 1):
    ...     if random.choice([True, False]) and pos != 0 and test_str [pos - 1] != ' ':
    ...         test_str = test_str[:pos] + ' ' + test_str[pos:]
    ...         test_ans = test_ans[:pos] + '_' + test_ans[pos:]
    >>> lower = random.choice([True, False])
    >>> if lower:
    ...     test_ans = test_ans.lower()
    >>> snakify(test_str, lower) == test_ans
    True

    :type string: str
    :rtype: str
    """
    snakecase_str = _space_pattern.sub('_', string)
    if lowercase:
        snakecase_str = snakecase_str.lower()
    return snakecase_str
