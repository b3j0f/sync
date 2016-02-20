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

        self.count = 5
        self.myaccessors = [MyAccessor0(), MyAccessor12()]
        self.mystores = list(
            MyStore(accessors=self.myaccessors) for _ in range(self.count)
        )
        self.registry = StoreRegistry(stores=self.mystores)

    def test_synchrone(self):

        record0 = MyRecord0()
        record1 = MyRecord1()
        record2 = MyRecord2()

        self.mystores[0].add(records=[record0])
        self.mystores[1].add(records=[record1])
        self.mystores[2].add(records=[record2])

        records0 = self.mystores[-1].find(rtype=MyRecord0)
        self.assertFalse(records0)
        print('OK')
        self.registry.synchronize(
            sources=[self.mystores[0]], targets=[self.mystores[-1]]
        )

        records0 = self.mystores[-1].find(rtype=MyRecord0)
        self.assertTrue(records0)


if __name__ == '__main__':
    main()
