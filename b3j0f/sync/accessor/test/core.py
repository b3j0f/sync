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
    """Accessor test implementation."""

    __rtypes__ = []  #: specify record type accessor implementations.

    def record2data(self, store, record, dirty=False):

        return record.raw(dirty=dirty)

    def data2record(self, store, rtype, data=None):

        return rtype(**{} if data is None else data)

    def add(self, store, records):

        for record in records:
            store._store[record.one] = record.copy()

        return records

    def update(self, store, records, upsert=False):

        if not upsert:
            for record in records:
                if record.one not in store._store:
                    raise Exception()

        for record in records:
            copy = record.copy()
            store._store[record.one] = copy

        return records

    def get(self, store, record):

        return store._store[record.one]

    def find(self, store, rtypes, data=None, limit=None, skip=None, sort=None):

        result = list(
            record for record in store._store.values()
            if isinstance(record, tuple(rtypes))
        )

        if data is not None:
            result, records = [], result
            for record in records:
                raw = record.raw()
                for key in data:
                    if key in raw and data[key] == raw[key]:
                        result.append(record)

        if skip is not None:
            result = result[skip:]

        if limit is not None:
            result = result[:limit]

        return result

    def count(self, store, rtypes, data=None):

        return len(self.find(store, rtypes, data))

    def remove(self, store, rtypes, records=None, data=None):

        result = []

        if records is None:

            for key in list(store._store):
                val = store._store[key]
                if isinstance(val, tuple(rtypes)):
                    result.append(store._store.pop(key))

        else:
            result = records
            for record in records:
                del store._store[record.one]

        return result


class MyStore(dict):
    """Store test implementation."""

    @property
    def _store(self):
        """quick access to private data."""

        return self


class AccessorTest(UTCase):
    """Test Accessor."""

    def setUp(self):

        self.store = MyStore()
        self.accessor = MyAccessor()
        self.record = MyRecord()
        self.rtypes = [MyRecord]

    def test_create(self):

        record = self.accessor.data2record(
            store=self.store, rtype=MyRecord, data={}
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
            store=self.store, rtypes=[MyRecord], data={'one': 1}
        )

        self.assertFalse(records)

        self.accessor.add(store=self.store, records=[self.record])
        records = self.accessor.find(
            store=self.store, rtypes=[MyRecord], data={'one': 1}
        )

        self.assertTrue(records)

    def test_remove(self):

        self.assertRaises(
            Exception,
            self.accessor.remove, store=self.store, records=[self.record],
            rtypes=self.rtypes
        )

        self.accessor.add(store=self.store, records=[self.record])

        self.accessor.remove(
            store=self.store, rtypes=self.rtypes, records=[self.record]
        )

        self.assertFalse(self.store)


if __name__ == '__main__':
    main()
