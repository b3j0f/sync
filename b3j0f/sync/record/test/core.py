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

"""record.core UTs"""

from unittest import main

from b3j0f.utils.ut import UTCase

from ..core import Record
from ..field import Field

from random import random


class MyRecord(Record):

    one = Field(ftype=int, default=1)
    two = Field(default=2)

    def __init__(self, id=None, *args, **kwargs):

        if id is None:
            id = random()

        super(MyRecord, self).__init__(id=id, *args, **kwargs)

class MyStore(object):

    def __init__(self, *args, **kwargs):

        super(MyStore, self).__init__(*args, **kwargs)

        self.records = set()

    def remove(self, records, *args, **kwargs):

        self.records.remove(records[0])

    def update(self, records, *args, **kwargs):

        self.records.add(records[0].copy())


class RecordTest(UTCase):

    def setUp(self):

        self.myrecord = MyRecord()
        self.mystore = MyStore()

    def test_isdirty(self):

        self.assertFalse(self.myrecord.isdirty)

        self.myrecord.a = 1

        self.assertTrue(self.myrecord.isdirty)

        self.myrecord.cancel()

        self.assertFalse(self.myrecord.isdirty)

        self.myrecord.a = 1

        self.assertTrue(self.myrecord.isdirty)

        self.myrecord.commit()

        self.assertFalse(self.myrecord.isdirty)

    def test_one(self):

        self.assertEqual(self.myrecord.one, MyRecord.one.default)

        self.assertRaises(TypeError, setattr, self.myrecord, 'one', '')

        self.myrecord.one = 2

        self.assertEqual(self.myrecord.one, 2)

        self.myrecord.cancel()

        self.assertEqual(self.myrecord.one, 1)

    def test_two(self):

        self.assertEqual(self.myrecord.two, MyRecord.two.default)

        self.myrecord.two = ''

        self.assertEqual(self.myrecord.two, '')

        self.myrecord.cancel()

        self.assertEqual(self.myrecord.two, 2)

    def test_dynamic(self):

        self.myrecord.a = 1

        MyRecord.a = Field(ftype=str)

        self.assertRaises(TypeError, setattr, self.myrecord, 'a')

        del MyRecord.a

        self.myrecord.a = 1

    def test_commit(self):

        self.assertFalse(self.mystore.records)

        self.myrecord.commit(stores=[self.mystore])

        self.assertIn(self.myrecord, self.mystore.records)

        self.myrecord.a = 2

        self.assertNotIn(self.myrecord, self.mystore.records)

        self.myrecord.commit(stores=[self.mystore])

        self.assertIn(self.myrecord, self.mystore.records)
        self.assertEqual(len(self.mystore.records), 2)

    def test_delete(self):

        self.assertFalse(self.mystore.records)

        self.myrecord.commit(stores=[self.mystore])
        self.assertIn(self.myrecord, self.mystore.records)

        self.myrecord.delete(stores=[self.mystore])
        self.assertFalse(self.mystore.records)

        self.myrecord.commit(stores=[self.mystore])
        self.assertIn(self.myrecord, self.mystore.records)

    def test_copy(self):

        self.myrecord.stores.add(MyStore())

        copy = self.myrecord.copy()

        for name in copy._data:
            self.assertEqual(getattr(copy, name), getattr(self.myrecord, name))

        self.assertTrue(self.myrecord.stores)
        self.assertFalse(copy.stores)

        copy = self.myrecord.copy(stores=[MyStore()])

        self.assertTrue(copy.stores)

        copy = self.myrecord.copy(data={'test': 1})
        self.assertEqual(copy.test, 1)

    def test_raw(self):

        data = self.myrecord._data.copy()

        raw = self.myrecord.raw(dirty=False)

        self.assertEqual(raw, data)

        raw = self.myrecord.raw(dirty=True)

        self.assertEqual(raw, data)

        self.myrecord.two = 5

        raw = self.myrecord.raw(dirty=False)

        self.assertEqual(raw, data)

        raw = self.myrecord.raw(dirty=True)

        self.assertNotEqual(raw, data)
        self.assertEqual(raw['two'], 5)

    def test_eq(self):

        myrecord1 = MyRecord(id=1)
        myrecord2 = MyRecord(id=1)
        self.assertEqual(myrecord1, myrecord2)

        myrecord1.a = 2
        self.assertNotEqual(myrecord1, myrecord2)

        myrecord1.cancel()
        self.assertEqual(myrecord1, myrecord2)


if __name__ == '__main__':
    main()
