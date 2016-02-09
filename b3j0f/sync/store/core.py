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

"""Store definition module."""

__all__ = ['Store']

from collections import Iterable

from ..record.core import Record
from ..accessor.registry import AccessorRegistry

from six import reraise


class Store(Record):
    """Store records.

    A Store can be a database or a github account for example."""

    class Error(Exception):
        """Handle Store errors."""

    def __init__(self, accessors=None, *args, **kwargs):

        super(Store, self).__init__(*args, **kwargs)

        self._accreg = AccessorRegistry(accessors=accessors)

    @property
    def accessors(self):
        """Get accessors.

        :rtype: list"""

        return list(self._accreg.values())

    @accessors.setter
    def accessors(self, value):
        """Change of accessors.

        :param list value: accessors to register in this store."""

        self._accreg.clear()
        self._accreg.register(accessors=value)

    def _getaccessor(self, records):
        """Get the right accessor able to process input record.

        :param records: record(s) to process with the output accessor.
        :type records: Record, type or list
        :raises: Store.Error if no accessor is available."""

        record = (
            records[0]
            if (isinstance(records, Iterable) and records)
            else records
        )

        result = self._accreg.get(record)

        if result is None:
            raise Store.Error('No store found to process {0}'.format(record))

        return result

    def create(self, rtype, fields=None):
        """Create a record with input type and field values.

        :param type rtype: record type.
        :param dict fields: record fields to use in a store context.
        :rtype: Record.
        :raises: Store.Error in case of error."""

        try:
            result = self._getaccessor(rtype).create(
                store=self, rtype=rtype, fields=fields
            )
        except Exception as e:
            reraise(Store.Error, Store.Error(e))

        else:
            try:
                self.add(records=[result])

            except Exception as e:
                reraise(Store.Error, Store.Error(e))

        return result

    def add(self, records):
        """Add records and register this in stores of records.

        Register this store to record stores if record is added.

        :param list records: records to add. Must be same type.
        :raises: Store.Error in case of error."""

        accessor = self._getaccessor(records)

        try:
            accessor.add(store=self, records=records)

        except Exception as e:
            reraise(Store.Error, Store.Error(e))

        else:
            for record in records:
                record.stores += [self]

    def update(self, records, upsert=False):
        """Update records in this store and register this in stores of records.

        :param list records: records to update in this store. Must be same type.
        :param bool upsert: if True (False by default), add the record if not
            exist.
        :raises: Store.Error in case of error."""

        accessor = self._getaccessor(records)

        try:
            accessor.update(store=self, records=records)

        except Exception as e:
            if upsert:
                accessor.add(store=self, records=records)

            else:
                reraise(Store.Error, Store.Error(e))

        for record in records:
            record.stores += [self]

    def get(self, record):
        """Get input record from this store.

        The found record matches with input record identifier and not all field
        values. The identifier depends on the store.

        :param Record record: record to get from this store.
        :return: corresponding record.
        :rtype: Record
        :raises: Store.Error in case of error."""

        accessor = self._getaccessor(record)

        try:
            result = accessor.get(store=self, record=record)

        except Exception as e:
            reraise(Store.Error, Store.Error(e))

        else:
            result.stores += [self]

        return result

    def __getitem__(self, key):

        return self.get(record=key)

    def find(self, rtype, fields=None):
        """Find records related to type and fields and register this to result
        stores.

        :param type rtype: record type to find.
        :param dict fields: record fields to filter. Default None.
        :return: record of input type and field values.
        :rtype: list
        :raises: Store.Error in case of error.
        """

        accessor = self._getaccessor(rtype)

        try:
            result = accessor.find(store=self, rtype=rtype, fields=fields)

        except Exception as e:
            reraise(Store.Error, Store.Error(e))

        else:
            for record in result:
                record.stores += [self]

        return result

    def remove(self, records):
        """Remove input record and unregister this store from record stores.

        :param Record record: record to remove. Records must be the same type.
        :raises: Store.Error in case of error.
        """

        accessor = self._getaccessor(records)

        try:
            accessor.remove(store=self, records=records)

        except Exception as e:
            reraise(Store.Error, Store.Error(e))

        else:
            for record in records:
                while self in record.stores:
                    record.stores.remove(self)

    def __delitem__(self, record):

        self.remove(records=[record])

    def __iadd__(self, records):
        """Add record(s).

        :param Record(s) records: records to add to this store.
        """

        if isinstance(records, Record):
            records = [records]

        self.add(records=records)

    def __ior__(self, records):
        """Update record(s) with upsert flag equals True.

        :param Record(s) records: records to update to this store.
        """

        if isinstance(records, Record):
            records = [records]

        self.update(records=records, upsert=True)

    def __isub__(self, records):
        """Remove record(s) to this store.

        :param Record(s) records: records to remove from this store.
        """

        if isinstance(records, Record):
            records = [records]

        self.remove(records=records)
