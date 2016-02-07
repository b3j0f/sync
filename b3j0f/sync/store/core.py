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

from ..record.core import Record
from ..accessor.registry import AccessorRegistry


class Store(object):
    """Store records.

    A Store can be a database or a github account for example."""

    def __init__(self, accessors, *args, **kwargs):

        super(Store, self).__init__(*args, **kwargs)

        self.accreg = AccessorRegistry(accessors)

    @property
    def accessors(self):
        """Get accessors."""

        return self.accreg

    @accessors.setter
    def accessors(self, value):
        """Change of accessors."""

        self.accreg.clear()
        self.accreg += value

    def create(self, rtype, fields):
        """Create a record with input type and field values.

        :param type rtype: record type.
        :param dict fields: record fields to use in a store context."""

        result = self.accreg.get(rtype).create(
            store=self, rtype=rtype, fields=fields
        )
        self.add(record=result)

        return result

    def add(self, record):
        """Add a record and register this in record stores.

        Register this store to record stores if record is added.

        :param Record record: record to add.
        """

        self.accreg.get(record).add(record=record, store=self)
        record.stores.add(self)

    def update(self, record, upsert=False):
        """Update a record in this store and register this in record stores.

        :param Record record: record to update in this store.
        :param bool upsert: if True (False by default), add the record if not
            exist"""

        accessor = self.accreg.get(record)

        if accessor is not None:
            try:
                accessor.update(record=record, store=self)

            except Exception:
                if upsert:
                    accessor.add(record=record, store=self)

                else:
                    raise

            record.stores.add(self)

    def get(self, record):
        """Get input record from this store.

        The found record matches with input record identifier and not all field
        values. The identifier depends on the store.

        :param Record record: record to get from this store.
        :return: corresponding record.
        :rtype: record"""

        result = self.accreg.get(record).get(record=record, store=self)
        result.stores.add(self)

        return result

    def __getitem__(self, key):

        return self.get(record=key)

    def find(self, rtype, **fields):
        """Find records related to type and fields and register this to result
        stores.

        :param type rtype: record type to find.
        :param dict fields: record fields to filter.
        :return: record of input type and field values.
        :rtype: list
        """

        result = self.accreg.get(rtype).find(
            store=self, rtype=rtype, fields=fields
        )

        for record in result:
            record.stores.add(self)

        return result

    def remove(self, record):
        """Remove input record and unregister this store from record stores.

        :param Record record: record to remove.
        """

        self.accreg.get(record).remove(store=self, record=record)
        record.stores.remove(self)

    def __delitem__(self, record):

        self.remove(record=record)

    def __iadd__(self, records):
        """Add record(s).

        :param Record(s) records: records to add to this store.
        """

        if isinstance(records, Record):
            records = [records]

        for record in records:
            self.add(record=record)

    def __ior__(self, records):
        """Update record(s) with upsert flag equals True.

        :param Record(s) records: records to update to this store.
        """

        if isinstance(records, Record):
            records = [records]

        for record in records:

            self.update(record=record, upsert=True)

    def __isub__(self, records):
        """Remove record(s) to this store.

        :param Record(s) records: records to remove from this store.
        """

        if isinstance(records, Record):
            records = [records]

        for record in records:
            self.remove(record=record)
