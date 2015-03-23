#!/usr/bin/env python

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
from setuptools import setup, find_packages

setup(name='pyparse',
      version='0.0.1',
      description='Parse.com SDK for Python',
      author='sodastsai',
      author_email='sodas@tickleapp.com',
      license='Apache License Version 2.0',
      url='https://github.com/tickleapp/pyparse',
      long_description='''PyParse - Parse.com SDK for Python''',
      packages=find_packages(),
      install_requires=[
          'six>=1.8.0',
          'requests>=2.6.0',
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX :: Linux',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries',
          'Topic :: Utilities',
          'Topic :: Internet :: WWW/HTTP',
      ])
