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

from .record import Record


class Store(object):
    """Store records.

    A Store can be a database or a github account for example."""

    def __init__(self, accessors, *args, **kwargs):

        super(Store, self).__init__(*args, **kwargs)

        self.accessorset = _AccessorSet(accessors=accessors)

    def create(self, rtype, **fields):
        """Create a record with input type and field values.

        :param type rtype: record type.
        :param dict fields: record fields to use in a store context."""

        result = self.accessorset.create(store=self, rtype=rtype, **fields)
        self.add(record=result)

        return result

    def add(self, record):
        """Add a record and register this in record stores.

        Register this store to record stores if record is added.

        :param Record record: record to add.
        """

        self.accessorset.add(record=record, store=self)
        record.stores.add(self)

    def update(self, record, upsert=False):
        """Update a record in this store and register this in record stores.

        :param Record record: record to update in this store.
        :param bool upsert: if True (False by default), add the record if not
            exist"""

        try:
            self.accessorset.update(record=record, store=self)

        except Exception:
            if upsert:
                self.accessorset.add(record=record, store=self)

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

        result = self.accessorset.get(record=record, store=self)
        result.stores.add(self)

        return result

    def find(self, rtype, **fields):
        """Find records related to type and fields and register this to result
        stores.

        :param type rtype: record type to find.
        :param dict fields: record fields to filter.
        :return: record of input type and field values.
        :rtype: list
        """

        result = self.accessorset.find(store=self, rtype=rtype, **fields)

        for record in result:
            record.stores.add(self)

        return result

    def remove(self, record):
        """Remove input record and unregister this store from record stores.

        :param Record record: record to remove.
        """

        self.accessorset.remove(store=self, record=record)
        record.stores.remove(self)

    def __iadd__(self, records):
        """Add record(s).

        :param Record(s) records: records to add to this store.
        """

        if isinstance(records, Record):
            records = [records]

        for record in records:

            self.create(record.__class__, **record.fields)

    def __ior__(self, records):
        """Update record(s) with upsert flag equals True.

        :param Record(s) records: records to update to this store.
        """

        if isinstance(records, Record):
            records = [records]

        for record in records:

            self.update(record, upsert=True)

    def __isub__(self, records):
        """Remove record(s) to this store.

        :param Record(s) records: records to remove from this store.
        """

        if isinstance(records, Record):
            records = [records]

        for record in records:
            self.remove(record=record)


class _AccessorSet(object):
    """In charge of delegating store record processing to accessors."""

    __slots__ = ('accessorsbytype')

    def __init__(self, accessors, *args, **kwargs):

        super(_AccessorSet, self).__init__(*args, **kwargs)

        self.accessorsbytype = {}

        for accessor in accessors:
            self.accessorsbytype[accessor.__rtype__] = accessor

    def create(self, store, rtype, **fields):
        """Create a records with input rtype and specific field values."""

        return self.accessorsbytype[rtype].create(store=store, **fields)

    def add(self, store, record):
        """Delegate record addition to a dedicated store.

        :param Store store: store able to process input record."""

        self.accessorsbytype[record.__class__].add(store=store, record=record)

    def get(self, store, record):
        """Get a record.

        :param Store store: store able to process input record."""

        return self.accessorsbytype[record.__class__].get(
            store=store, record=record
        )

    def find(self, store, rtype, **kwargs):
        """
        :param Store store: store able to process input record.
        """

        return self.accessorsbytype[rtype].find(store=store, **kwargs)

    def update(self, store, record):
        """
        :param Store store: store able to process input record.
        """

        self.accessorsbytype[record.__class__].update(
            store=store, record=record
        )

    def remove(self, store, record):
        """
        :param Store store: store able to process input record.
        """

        self.accessorsbytype[record.__class__].remove(
            store=store, record=record
        )

    def __iadd__(self, accessor):

        self.accessorsbytype[accessor.__rtype__] = accessor

    def __isub__(self, accessor):

        del self.accessorsbytype[accessor.__rtype__]
