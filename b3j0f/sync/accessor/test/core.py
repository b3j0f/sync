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

"""accessor.core UTs"""

from unittest import main

from b3j0f.utils.ut import UTCase

from ..core import Accessor

from ...record.test.core import MyRecord


class MyAccessor(Accessor):

    __rtypes__ = []  #: specify record type accessor implementations.

    def create(self, store, rtype, fields):
        """Create a record related to store field values."""

        return rtype(**({} if fields is None else fields))

    def add(self, store, records):
        """Add records in a store"""

        for record in records:
            store.data[record.one] = record.copy()

    def update(self, store, records, upsert=False):
        """Update records in a store.

        :param Store store: store where update the records.
        :param bool upsert: if True (default False), add the record if not exist."""

        if not upsert:
            for record in records:
                if record.one not in store:
                    raise Exception()

        for record in records:
            store.data[record.one] = record.copy()

    def get(self, store, record):
        """Get a record from a store."""

        return store.data[record.one]

    def find(self, store, rtype, fields):
        """Find records from a store."""

        return list(store.data.values())

    def remove(self, store, records):
        """Remove records from a store."""

        for record in records:
            store.data.pop(record.one, None)


class MyStore(dict):

    @property
    def data(self):

        return self


class AccessorTest(UTCase):

    def setUp(self):

        self.store = MyStore()
        self.accessor = MyAccessor()
        self.record = MyRecord()

    def test_create(self):

        record = self.accessor.create(
            store=self.store, rtype=MyRecord, fields={}
        )

        self.assertEqual(record.one, MyRecord.one.default)

    def test_add(self):

        self.accessor.add(store=self.store, records=[self.record])

        self.assertEqual(self.store[self.record.one].one, self.record.one)

    def test_update(self):

        self.assertRaises(
            Exception,
            self.accessor.update, store=self.store, records=[self.record]
        )

        self.accessor.update(
            store=self.store, records=[self.record], upsert=True
        )

        self.assertEqual(self.store[self.record.one].two, self.record.two)

        self.record.two = - self.record.two
        self.assertNotEqual(self.store[self.record.one].two, self.record.two)
        self.accessor.update(store=self.store, records=[self.record])

        self.assertEqual(self.store[self.record.one].two, self.record.two)

    def test_get(self):

        self.accessor.add(store=self.store, records=[self.record])

        record = self.accessor.get(store=self.store, record=self.record)

        self.assertEqual(record, self.record)

    def test_find(self):

        records = self.accessor.find(
            store=self.store, rtype=MyRecord, fields={'one': 1}
        )

        self.assertFalse(records)

        self.accessor.add(store=self.store, records=[self.record])
        records = self.accessor.find(
            store=self.store, rtype=MyRecord, fields={'one': 1}
        )

        self.assertTrue(records)

    def test_remove(self):

        self.assertRaises(
            Exception,
            self.accessor.remove, store=self.store, records=[self.record]
        )

        self.accessor.add(store=self.store, records=[self.record])

        self.accessor.remove(store=self.store, records=[self.record])

        self.assertFalse(self.store)


if __name__ == '__main__':
    main()
