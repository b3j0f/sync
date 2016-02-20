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

"""accessor.registry UTs"""

from unittest import main

from b3j0f.utils.ut import UTCase

from ..registry import AccessorRegistry
from .core import MyAccessor
from ...record.test.core import MyRecord


class MyRecord0(MyRecord):
    pass


class MyRecord1(MyRecord):
    pass


class MyRecord2(MyRecord):
    pass


class MyAccessor0(MyAccessor):

    __rtypes__ = [MyRecord0]


class MyAccessor12(MyAccessor):

    __rtypes__ = [MyRecord1, MyRecord2]


class AccessorRegistryTest(UTCase):

    def setUp(self):

        self.ar = AccessorRegistry()
        self.myaccessor0 = MyAccessor0()
        self.myaccessor12 = MyAccessor12()

    def test_register(self):

        accessor = self.ar.get(MyRecord0)
        self.assertIsNone(accessor)

        self.ar.register(accessors=[self.myaccessor0])

        accessor = self.ar.get(MyRecord0)
        self.assertIs(accessor, self.myaccessor0)

        accessor = self.ar.get(MyRecord0())
        self.assertIs(accessor, self.myaccessor0)

        self.ar.unregister(accessors=[accessor])

        accessor = self.ar.get(MyRecord0)
        self.assertIsNone(accessor)

        accessor = self.ar.get(MyRecord1)
        self.assertIsNone(accessor)

        accessor = self.ar.get(MyRecord2)
        self.assertIsNone(accessor)

        self.ar.register(accessors=[self.myaccessor12])

        accessor = self.ar.get(MyRecord1)
        self.assertIs(accessor, self.myaccessor12)

        accessor = self.ar.get(MyRecord2())
        self.assertIs(accessor, self.myaccessor12)

        self.ar.unregister(rtypes=[MyRecord1])

        accessor = self.ar.get(key=MyRecord1)
        self.assertIsNone(accessor)

        accessor = self.ar.get(key=MyRecord2)
        self.assertIs(accessor, self.myaccessor12)

        accessor = self.ar.get(key=MyRecord1, default=1)
        self.assertEqual(accessor, 1)

        accessor = self.ar.get(key=MyRecord2, default=1)
        self.assertIs(accessor, self.myaccessor12)

        self.ar.unregister(accessors=[self.myaccessor12])

        accessor = self.ar.get(key=MyRecord1)
        self.assertIsNone(accessor)

        accessor = self.ar.get(key=MyRecord2)
        self.assertIsNone(accessor)


if __name__ == '__main__':
    main()
