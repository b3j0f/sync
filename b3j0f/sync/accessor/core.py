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

from ..record.core import Record


class Accessor(Record):
    """Apply record access rules on stores."""

    __rtypes__ = []  #: specify record type accessor implementations.

    def create(self, store, rtype, data=None):
        """Create a record related to store field values.

        :param Store store: store from which create a new record.
        :param type rtype: records type to create from the store.
        :param dict data: specific values to use such as the store data
            content."""

        raise NotImplementedError()

    def add(self, store, records):
        """Add records in a store.

        :param Store store: store from which add input records.
        :param list records: records to add to the store.
        :return: added records.
        :rtype: list"""

        raise NotImplementedError()

    def update(self, store, records, upsert=False):
        """Update records in a store.

        :param Store store: store where update the records.
        :param list records: records to update in the input store.
        :param bool upsert: if True (default False), add the record if not exist
        .
        :return: updated records.
        :rtype: list
        """

        raise NotImplementedError()

    def get(self, store, record):
        """Get a record from a store.

        :param Store store: store from which get a record.
        :param Record record: record to get from the store.
        :rtype: Record"""

        raise NotImplementedError()

    def count(self, store, rtype, data=None):
        """Get number of data in a store.

        :param Store store: store from where get number of data.
        :param type rtype: record type.
        :param dict data: data content to filter.
        :rtype: int."""

        raise NotImplementedError()

    def find(self, store, rtype, data=None, limit=None, skip=None):
        """Find records from a store.

        :param Store store: store from where find data.
        :param type rtype: record type to retrieve.
        :param dict data: data content to filter.
        :param int limit: maximal number of records to retrieve.
        :param int skip: number of elements to avoid.
        :return: records of input type and field values.
        :rtype: list"""

        raise NotImplementedError()

    def remove(self, store, records=None, rtype=None, data=None):
        """Remove records from a store.

        :param Store store: store from where remove records.
        :param list records: records to remove.
        :param type rtype: record type to remove.
        :param dict data: data content to filter."""

        raise NotImplementedError()
