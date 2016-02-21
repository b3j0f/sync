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

from ..registry import StoreRegistry

from .core import MyStore

from ...accessor.test.registry import (
    MyAccessor0, MyAccessor12, MyRecord0, MyRecord1, MyRecord2
)


class StoreRegistryTest(UTCase):

    def setUp(self):

        self.count = 3
        self.accessors = [MyAccessor0(), MyAccessor12()]
        self.stores = list(
            MyStore(id=i, accessors=self.accessors) for i in range(self.count)
        )
        self.registry = StoreRegistry(stores=self.stores)

    def test_synchrone(self):

        record0 = MyRecord0(one=0)
        record2 = MyRecord2(one=2)

        self.stores[0].add(records=[record0])
        self.stores[-1].add(records=[record2])

        records = self.registry.find()
        self.assertEqual(
            records,
            {
                self.stores[0]: [record0],
                self.stores[1]: [],
                self.stores[2]: [record2],

            }
        )

        records = self.registry.find(rtypes=[MyRecord0])
        self.assertEqual(
            records,
            {
                self.stores[0]: [record0],
                self.stores[1]: [],
                self.stores[2]: [],

            }
        )

        self.registry.synchronize(
            sources=[self.stores[0]], targets=[self.stores[2]]
        )


        records0 = self.registry.find(rtypes=[MyRecord0])
        self.assertTrue(records0[self.stores[2]])

        records2 = self.registry.find(rtypes=[MyRecord2])
        self.assertFalse(records2[self.stores[0]])
        self.assertTrue(records2[self.stores[2]])

        self.registry.synchronize()

        records2 = self.registry.find(rtypes=[MyRecord2])
        self.assertTrue(records2[self.stores[0]])


if __name__ == '__main__':
    main()
