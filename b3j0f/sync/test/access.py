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
from b3j0f.utils.version import basestring
from b3j0f.sync.access import Accessor, getglobalid, getidwpids, separator_char
from b3j0f.sync.model import Data


class TestAccessor(Accessor):
    """Test Accessor implementation."""

    def __init__(self, datatype=Data, **kwargs):

        super(TestAccessor, self).__init__(datatype=datatype, **kwargs)

        self.datum = {}  # set of datum by id

    def get(self, _id, pids=None):

        return self.datum.get(_id)

    def find(self, ids=None, descs=None, created=None, updated=None):

        result = []

        if ids is not None:
            result += [self.datum[_id] for _id in self.datum if _id in ids]
        else:
            result = self.datum.values()

        if descs is not None:
            result += [
                data for data in self.datum.values() if data.desc in descs
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
        self.accessor = TestAccessor(store=self, datatype=Data)
        self.data = self.accessor.create()

    def notify(self, event, data):
        """Store notification function."""

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

    def test_cud(self):
        """Test the create/add/update/delete methods."""

        self.assertTrue(isinstance(self.data, Data))
        self.assertIs(self.data.accessor, self.accessor)

        self.assertNotIn(self.data, self.accessor)
        self.assertFalse(self.data.isstored)

        self.data.save()

        self.assertTrue(self.data.isstored)
        self.assertIn(self.data, self.accessor)

        self.data.desc = ''

        self.data.save()
        self.assertTrue(self.data.isstored)

        self.data.desc = 'test'
        self.assertTrue(self.data.isdirty)
        self.accessor.update(data=self.data)
        self.assertTrue(self.data.isdirty)

        data = self.accessor[self.data._id]
        self.assertEqual(data.desc, 'test')

        data.delete()
        self.assertNotIn(data, self.accessor)


class TestGetIdwPids(UTCase):
    """Test the getidwpids function."""

    def test_id(self):
        """Test with a simple id."""

        test_id = 'test'
        _id, pids = getidwpids(_id=test_id)

        self.assertEqual(_id, test_id)
        self.assertFalse(pids)

    def test_id_w_sep(self):
        """Test with an _id and wrong separator char."""

        test_id = 'test{0}'.format(separator_char)

        _id, pids = getidwpids(_id=test_id)

        self.assertEqual(_id, test_id)
        self.assertFalse(pids)

    def test_id_ko_ok_ko_ok_ko(self):
        """Test with an _id followed by a wrong separator char, then a right,
        and a wrong, and a right and a wrong.
        """

        test_id = 'test{0}10{0}8{0}rt{0}2{0}fgt{0}fr{0}'.format(
            separator_char
        )

        _id, pids = getidwpids(_id=test_id)

        self.assertEqual(_id, 'test{0}10'.format(separator_char))
        self.assertEqual(pids, ['rt', 'fgt{0}fr{0}'.format(separator_char)])

    def test_reverse(self):
        """Test in reversing getglobalid parameters."""

        test_id = 'test{0}10{0}8{0}rt{0}2{0}fgt{0}fr{0}'.format(
            separator_char
        )

        _id, pids = getidwpids(_id=test_id)
        globalid = getglobalid(_id=_id, pids=pids)

        self.assertEqual(test_id, globalid)


class TestGetGlobalId(UTCase):
    """Test the getglobalid function."""

    def test_id(self):
        """Test with simple _id."""

        test_id = 'test'
        globalid = getglobalid(_id=test_id)

        self.assertEqual(test_id, globalid)

    def test_id_pids(self):
        """Test with _id and pids."""

        test_id = 'test'
        pids = [test_id[:-1], test_id]

        globalid = getglobalid(_id=test_id, pids=pids)

        idtotest = '{0}{1}{4}{1}{2}{1}{5}{1}{3}'.format(
            test_id, separator_char, pids[0], pids[1],
            len(test_id), len(pids[0])
        )
        self.assertEqual(globalid, idtotest)


if __name__ == '__main__':
    main()
