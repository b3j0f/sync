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

    class Error(Exception):
        """Handle accessor errors."""

    __rtypes__ = []  #: specify record type accessor implementations.

    def record2data(self, store, record, dirty=True):
        """Get a specific store data from a record.

        :param Store store: store from where get input record.
        :param Record record: record to convert to a data.
        :param bool dirty: if True (default) get dirty values in raw."""

        raise NotImplementedError()

    def data2record(self, store, rtype, data=None):
        """Create a record related to specific store data.

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

    def count(self, store, rtypes, data=None):
        """Get number of data in a store.

        :param Store store: store from where get number of data.
        :param list rtypes: record types.
        :param dict data: data content to filter.
        :rtype: int."""

        raise NotImplementedError()

    def find(
        self, store, rtypes, records=None, data=None,
        limit=None, skip=None, sort=None
    ):
        """Find records from a store.

        :param Store store: store from where find data.
        :param list rtypes: record types to retrieve. Default is self.rtypes.
        :param list records: records to find.
        :param dict data: data content to filter.
        :param int limit: maximal number of records to retrieve.
        :param int skip: number of elements to avoid.
        :param list sort: list of field name to sort by value.
        :return: records of input type and field values.
        :rtype: list"""

        raise NotImplementedError()

    def remove(self, store, rtypes, records=None, data=None):
        """Remove records from a store.

        :param Store store: store from which remove records.
        :param list records: records to remove. Default is all records.
        :param list rtype: record types to remove. Default is self.rtypes.
        :param dict filter: data content to filter."""

        raise NotImplementedError()
