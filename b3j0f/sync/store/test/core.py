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

"""store.core UTs"""

from unittest import main

from b3j0f.utils.ut import UTCase

from ..core import Store

from ...accessor.test.registry import (
    MyAccessor0, MyAccessor12, MyRecord0, MyRecord1, MyRecord2
)


class MyStore(Store):

    def __init__(self, *args, **kwargs):

        super(MyStore, self).__init__(*args, **kwargs)

        self._store = {}


class StoreTest(UTCase):

    def setUp(self):

        self.myaccessor0 = MyAccessor0()
        self.myaccessor12 = MyAccessor12()
        self.store = MyStore(accessors=[self.myaccessor0, self.myaccessor12])

    def test_accessors(self):

        self.assertTrue(self.store._accreg)

        self.store.accessors = []

        self.assertFalse(self.store._accreg)

        self.store.accessors = [self.myaccessor0, self.myaccessor12]

        self.assertTrue(self.store._accreg)

    def test_create(self):

        record = self.store.data2record(rtype=MyRecord1)

        self.assertEqual(record.one, MyRecord1.one.default)

        record = self.store.data2record(
            rtype=MyRecord1,
            data={'three': 3, 'two': MyRecord1.two.default * 2}
        )

        self.assertEqual(record.one, MyRecord1.one.default)
        self.assertEqual(record.two, MyRecord1.two.default * 2)
        self.assertEqual(record.three, 3)

        self.assertEqual(record.stores, set([self.store]))

    def test_add(self):

        records = [MyRecord1(**{'test': i}) for i in range(5)]

        for record in records:
            self.assertFalse(record.stores)
            self.assertNotIn(record, self.store)

        self.store.add(records=records)

        for record in records:
            self.assertTrue(record.stores)
            self.assertIn(self.store, record.stores)
            self.assertIn(record, self.store)

    def test_update(self):

        records = [MyRecord1(**{'test': i}) for i in range(5)]

        for record in records:
            self.assertFalse(record.stores)

        self.assertRaises(
            Store.Error, self.store.update, records=records, upsert=False
        )

        self.store.update(records=records, upsert=True)
        for record in records:
            self.assertTrue(record.stores)

        self.store.update(records=records, upsert=False)

    def test_get(self):

        record = MyRecord1()

        self.assertRaises(Store.Error, self.store.get, record=record)

        self.store.add(records=[record])

        record2 = self.store.get(record=record)

        self.assertEqual(record2, record)

        record2 = self.store[record]

        self.assertEqual(record2, record)

    def test_find(self):

        records = self.store.find(rtypes=[MyRecord1])
        self.assertFalse(records)

        records = [MyRecord1(two=1), MyRecord1(two=2)]

        self.store.add(records=records)

        records = self.store.find(rtypes=[MyRecord1])
        self.assertEqual(len(records), 2)

        records = self.store.find(data={'two': 2})
        self.assertEqual(len(records), 1)

    def test_remove(self):

        record = MyRecord1()

        self.assertRaises(Store.Error, self.store.get, record=record)

        self.store.add(records=[record])

        record2 = self.store.get(record=record)

        self.assertEqual(record2, record)

        self.store.remove(records=[record2])

        self.assertFalse(self.store._store)

        self.store += [record]

        del self.store[record]

        self.assertNotIn(record, self.store)

        self.store += record

        self.assertIn(record, self.store)

        self.store -= record

        self.assertNotIn(record, self.store)

        self.store += record

        self.assertIn(record, self.store)

        self.store -= record

        self.assertNotIn(record, self.store)

    def test_rtypes(self):

        rtypes = set(self.store.rtypes)

        self.assertEqual(rtypes, set((MyRecord0, MyRecord1, MyRecord2)))


if __name__ == '__main__':
    main()
