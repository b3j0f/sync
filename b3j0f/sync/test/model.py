#!/usr/bin/env python
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2015 Jonathan Labéjof <jonathan.labejof@gmail.com>
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

"""Test the data module."""

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.utils.version import range
from b3j0f.sync.model import Data


class DataTest(UTCase):
    """Test Data object."""

    def setUp(self):

        self.count = 5000
        self.data = Data(accessor=self)

        self.datum = set(Data(accessor=self) for _ in range(self.count))

    def get(*args, **kwargs):
        """Emulate the accessor.get method."""

    def add(*args, **kwargs):
        """Emulate the accessor.add method."""

    def remove(*args, **kwargs):
        """Emulate the accessor.remove method."""

    def test_unique_id(self):
        """Test if several data has different _id."""

        datum_id = set([data._id for data in self.datum])

        self.assertEqual(len(datum_id), self.count)

    def test_hash(self):
        """Test the hash function."""

        self.assertNotIn(self.data, self.datum)

        self.datum.add(self.data)

        self.assertIn(self.data, self.datum)

        self.datum.remove(self.data)

        self.assertNotIn(self.data, self.datum)

    def test_equality(self):
        """Test data equality."""

        data = Data(accessor=self)

        self.assertNotEqual(self.data, data)

        self.data._id = data._id

        self.assertEqual(self.data, data)

    def test_datetime(self):
        """Test if creation/updating date are now."""

        self.assertIsNotNone(self.data.created)
        self.assertIsNotNone(self.data.updated)

    def test_isdirty_rollback_save(self):
        """Test isdirty/rollback/save methods."""

        self.assertFalse(self.data.isdirty)

        self.data.desc = ''
        self.assertTrue(self.data.isdirty)

        self.data.rollback()
        self.assertFalse(self.data.isdirty)

        self.data.desc = ''
        self.assertTrue(self.data.isdirty)

        self.data.save()
        self.assertFalse(self.data.isdirty)

        self.data.delete()
        self.assertFalse(self.data.isdirty)


if __name__ == '__main__':
    main()
