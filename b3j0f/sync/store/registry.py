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

"""Store registry module."""

__all__ = ['StoreRegistry']

from .core import Store


class StoreRegistry(Store):
    """Store registry."""

    __rtypes__ = []  #: specify record type accessor implementations.

    def __init__(self, stores, *args, **kwargs):

        super(StoreRegistry, self).__init__(*args, **kwargs)

        self.stores = stores

    def create(self, rtype, fields):
        """Create a record related to store data field values."""

        result = None

        for store in self.stores:
            try:
                result = store.create(rtype=rtype, fields=fields)

            except Exception:
                pass

            else:
                break

        return result

    def add(self, records):
        """Add input record(s) in a store"""

        for store in self.stores:
            try:
                store.add(records=records)

            except Exception:
                pass

    def update(self, records, upsert=False):
        """Update a record(s) in a store."""

        for store in self.stores:
            try:
                store.update(records=records, upsert=upsert)

            except Exception:
                pass

    def get(self, record):
        """Get a record from a store."""

        result = None

        for store in self.stores:
            try:
                result = store.get(record)

            except Exception:
                pass

            else:
                break

        return result

    def find(self, rtype, fields):
        """Find records from a store."""

        result = []

        for store in self.stores:
            result += store.find(rtype=rtype, fields=fields)

        return result

    def remove(self, records):
        """Remove records from a store."""

        for store in self.stores:
            try:
                store.remove(records=records)

            except Exception:
                pass
