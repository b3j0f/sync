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

"""Test the access module."""

from unittest import main

from b3j0f.utils.ut import UTCase
from b3j0f.utils.path import getpath
from b3j0f.utils.version import range
from b3j0f.sync.store import Store
from b3j0f.sync.data import Data
from b3j0f.sync.access import Accessor
from b3j0f.sync.test.access import TestAccessor


class TestStore(Store):
    """Test Store implementation."""

    def __init__(self, **kwargs):

        super(TestStore, self).__init__(**kwargs)

        self.datum = {}  # set of datum by id

    def connect(self):

        self.connected = True

    def disconnect(self):

        self.connected = False

    def _isconnected(self):

        return self.connected


class StoreTest(UTCase):
    """Test Store object."""

    def setUp(self):

        self.accessorname = 'data'
        self.datum = {}  # data by event
        self.store = TestStore(handlers=[self.handler])
        self.accessor = TestAccessor(store=self.store)
        self.store.accessors = {self.accessorname: self.accessor}
        self.data = self.store.create(accessor=self.accessorname)

    def handler(self, event, data, **kwargs):
        """Store handler."""

        self.datum.setdefault(event, []).append(data)  # add data at event key


class AccessorsTest(StoreTest):
    """Test accessors setter."""

    def test_classname(self):
        """Test with accessor values such as class names."""

        accessorname = getpath(TestAccessor)

        count = 5

        accessors = {}

        for i in range(count):
            accessors['data{0}'.format(i)] = accessorname

        self.store.accessors = accessors

        for i in range(count):
            accessor = self.store.accessors['data{0}'.format(i)]
            self.assertTrue(isinstance(accessor, Accessor))
            self.assertIs(accessor.store, self.store)

    def test_instances(self):
        """Test with accessor such as class instances."""

        count = 5

        accessors = {}

        for i in range(count):
            accessors['data{0}'.format(i)] = TestAccessor(store=self.store)

        self.store.accessors = accessors

        for i in range(count):
            accessor = self.store.accessors['data{0}'.format(i)]
            self.assertTrue(isinstance(accessor, Accessor))
            self.assertIs(accessor.store, self.store)


class CRUDTest(StoreTest):

    def test_get(self):
        """Test the get method."""

        storedata = self.store.get(_id=self.data._id)
        self.assertIsNone(storedata)  # check store is empty
        self.assertFalse(self.datum)  # check this is false

        self.store.add(data=self.data)  # add data
        # check datum notifiaction
        self.assertEqual(self.datum, {Accessor.ADD: [self.data]})

        storedata = self.store.get(_id=self.data._id)
        self.assertEqual(self.data, storedata)

    def test_find(self):
        """Test the find method."""

        storedatum = self.store.find()

        self.assertFalse(storedatum)

        self.store.add(data=self.data)

        storedatum = self.store.find()

        self.assertTrue(storedatum)

    def test_cud(self):
        """Test the create/add/update/delete methods."""

        self.assertTrue(isinstance(self.data, Data))
        self.assertIs(self.data.accessor, self.accessor)
        self.assertIs(self.accessor.store, self.store)

        self.assertNotIn(self.data, self.store)
        self.assertFalse(self.data.isstored)

        self.data.save()

        self.assertTrue(self.data.isstored)
        self.assertIn(self.data, self.store)

        self.data.desc = ''

        self.data.save()
        self.assertTrue(self.data.isstored)

        self.data.desc = 'test'
        self.assertTrue(self.data.isdirty)
        self.store.update(data=self.data)
        self.assertTrue(self.data.isdirty)

        data = self.store[self.data._id]
        self.assertEqual(data.desc, 'test')

        data.delete()
        self.assertNotIn(data, self.store)


if __name__ == '__main__':
    main()
