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

"""Data module.

Contains definition of the abstract resource data.
"""

from random import randint

from datetime import datetime

from b3j0f.sync.access import getidwpids
from b3j0f.utils.property import addproperties


__all__ = ['Data', 'datafields']


def _updatefield(data, field):
    """Update input data with input field name.

    :param Data data: data to update.
    :param str field: data field name to update.
    """
    if field not in data._updatedfields:
        data._updatedfields[field] = getattr(
            data, '_{0}'.format(field)
        )
        data.updated = datetime.now()  # update updated field


def _delfield(self, name):
    _updatefield(data=self, field=name)


def _setfield(self, value, name):
    """Set data field with input value.

    :param Data self: data instance.
    :param value: data field value to set.
    :param str prop: data field name.
    """

    _updatefield(data=self, field=name)


def datafields(*fields):
    """Decorator in charge of adding Data property fields with notification to
    creation accessor.

    :param list fields: field names to convert to accessor property.
    :param fget: fget function to apply to all properties.
    :param fset: fset function to apply to all properties.
    :param fdel: fdel function to apply to all properties.
    """

    return addproperties(names=fields, bfset=_setfield, bfdel=_delfield)


@datafields('_id', 'desc', 'created', 'updated')
class Data(object):
    """Store data.

    A Data is related to an accessor and contains following properties:

    - _id: unique data id in the accessor.
    - desc: data description.
    - created: date time creation (default now).
    - updated: date time updating (default now).
    """

    class Error(Exception):
        """Handle element errors."""

    def __init__(
            self,
            accessor, _id=None, desc=None, created=None, updated=None
    ):
        """
        :param Accessor accessor: creation accessor.
        :param str _id: data id. Generated in [1; 2^32-1] by default.
        :param str description: data description.
        :param datetime created: data date time creation.
        :param datetime updated: data date time updating.
        """

        super(Data, self).__init__()

        self._updatedfields = {}

        # set protected attributes
        setattr(self, '__id', str(randint(1, 2**32-1) if _id is None else _id))
        self._desc = desc
        self._created = datetime.now() if created is None else created
        self._updated = datetime.now() if updated is None else updated

        # set public attributes
        self.accessor = accessor

    def __hash__(self):

        return hash(getattr(self, '__id'))

    def __cmp__(self, other):

        return hash(self._id).__cmp__(hash(other._id))

    @property
    def isdirty(self):
        """
        :return: True iif data content has been modified after created by the
            accessor.
        :rtype: bool
        """

        return len(self._updatedfields) > 0

    @property
    def isstored(self):
        """
        :return: True iif this data exists in store.
        :rtype: bool
        """

        return self in self.accessor

    def rollback(self):
        """Rollback field values."""

        for name in self._updatedfields:
            field = self._updatedfields[name]
            setattr(self, name, field)

        self._updatedfields.clear()

    def save(self, sync=True):
        """Save this Data and synchronize this content with other stores if
        necessary.

        :param bool sync: if True (default) synchronize this data with all
            stores.
        :raises: Accessor.Error in case of saving error.
        """

        _id, pids = getidwpids(_id=self._id)
        old = self.accessor.get(_id=_id, pids=pids)

        if old is None:
            self.accessor.add(data=self, sync=sync)
        else:
            self.accessor.update(data=self, old=old, sync=sync)

        self._updatedfields.clear()  # finish to clear data

    def delete(self, sync=True):
        """Delete data in removing it from its store.

        :param bool sync: if True (default) synchronize the deletion with all
            stores.
        :raises: Accessor.Error in case of removing error.
        """

        self.accessor.remove(data=self, sync=sync)
