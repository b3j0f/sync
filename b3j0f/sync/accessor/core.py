# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2014 Jonathan Labéjof <jonathan.labejof@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# --------------------------------------------------------------------

"""Accessor definition module."""

__all__ = ['Accessor']


class Accessor(object):
    """Apply record access rules on stores."""

    __rtypes__ = []  #: specify record type accessor implementations.

    def create(self, store, rtype, fields):
        """Create a record related to store field values."""

        raise NotImplementedError()

    def add(self, store, record):
        """Add input record in a store"""

        raise NotImplementedError()

    def update(self, store, record):
        """Update record in a store."""

        raise NotImplementedError()

    def get(self, store, record):
        """Get a record from a store."""

        raise NotImplementedError()

    def find(self, store, rtype, fields):
        """Find records from a store."""

        raise NotImplementedError()

    def remove(self, store, record):
        """Remove a record from a store."""

        raise NotImplementedError()