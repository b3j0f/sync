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

"""store.field UTs"""

from unittest import main

from b3j0f.utils.ut import UTCase

from ..field import Field


class FieldTest(UTCase):

    def test_type(self):

        field = Field(ftype=int)

        self.assertRaises(TypeError, field.getvalue, '')

        value = field.getvalue(value=None)

        self.assertIsNone(value)

        value = field.getvalue(value=0)

        self.assertEqual(value, 0)

    def test_default(self):

        field = Field(default=1)

        value = field.getvalue(value=None)

        self.assertEqual(value, 1)

        value = field.getvalue(value=2)

        self.assertEqual(value, 2)

    def test_default_type(self):

        field = Field(ftype=int, default=1)

        value = field.getvalue(value=None)

        self.assertEqual(1, value)

        self.assertRaises(TypeError, field.getvalue, '')

        value = field.getvalue(value=2)

        self.assertEqual(2, value)

    def test_wrong_default_type(self):

        self.assertRaises(TypeError, Field, ftype=int, default='')


if __name__ == '__main__':
    main()
