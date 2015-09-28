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
from b3j0f.sync.access import Accessor
from b3j0f.sync.data import Data


class TestAccessor(Accessor):
    """Test Accessor implementation."""

    def __init__(self, **kwargs):

        super(TestAccessor, self).__init__(**kwargs)

        self.datum = {}  # set of datum by id

    def get(self, _id, pids=None):

        return self.datum.get(_id)

    def find(self, ids=None, desc=None, created=None, updated=None):

        result = []

        if ids is not None:
            result += [self.datum[_id] for _id in self.datum if _id in ids]
        else:
            result = self.datum.values()

        if desc is not None:
            result += [
                data for data in self.datum.values() if data.desc == desc
            ]

        if created is not None:
            result += [
                data for data in self.datum.values() if data.created >= created
            ]

        if updated is not None:
            result += [
                data for data in self.datum.values() if data.updated >= updated
            ]

        return result

    def _add(self, data):

        self.datum[data._id] = data

        return data

    def _update(self, data, old):

        self.datum[data._id] = data

        return data

    def _remove(self, data):

        del self.datum[data._id]

        return data


class AccessorTest(UTCase):
    """Test Accessor object."""

    def setUp(self):

        self.datum = {}  # data by event
        self.accessor = TestAccessor(resource=self, datatype=Data)
        self.data = Data(accessor=self.accessor)

    def notify(self, event, data):
        """Resource notification function."""

        self.datum.setdefault(event, []).append(data)  # add data at event key

    def test_get(self):
        """Test the get method."""

        accessordata = self.accessor.get(_id=self.data._id)
        self.assertIsNone(accessordata)  # check accessor is empty
        self.assertFalse(self.datum)  # check this is false

        self.accessor.add(data=self.data)  # add data
        # check datum notifiaction
        self.assertEqual(self.datum, {Accessor.ADD: [self.data]})

        accessordata = self.accessor.get(_id=self.data._id)
        self.assertEqual(self.data, accessordata)

    def test_find(self):
        """Test the find method."""

        accessordata = self.accessor.find()

        self.assertFalse(accessordata)

        self.accessor.add(data=self.data)

        accessordata = self.accessor.find()

        self.assertTrue(accessordata)

if __name__ == '__main__':
    main()
