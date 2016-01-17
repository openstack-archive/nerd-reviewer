#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import abc

import six


@six.add_metaclass(abc.ABCMeta)
class Reviewer(object):

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        """Name of this reviewer (if any)."""
        return self._name

    @abc.abstractmethod
    def review(self, a_review):
        """Review some incoming review and return its analysis."""

    @abc.abstractproperty
    def description(self):
        """Useful description of this reviewer (personality, type...)."""

    @abc.abstractproperty
    def personality(self):
        """Current personality profile of this reviewer"""
