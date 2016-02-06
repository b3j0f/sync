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

from inspect import getmembers

from .field import FieldDescriptor


class MetaRecord(type):
    """Apply field descriptors on record field values."""

    def __call__(cls, *args, **kwargs):

        for name, member in getmembers(cls):

            if isinstance(member, FieldDescriptor):

                value = kwargs.get(name)

                value = member.getvalue(value=value, name=name)

                kwargs[name] = value

        result = type.__call__(cls, *args, **kwargs)

        return result


class Record(object):
    """Record object which embeds data values."""

    class Error(Exception):
        """Handle record errors."""

    __metaclass__ = MetaRecord

    __slots__ = ('stores', 'fields', '_oldfields')

    def __init__(self, *stores, **fields):
        """
        :param stores: stores to use in this record.
        :param fields: record field values.
        """

        super(Record, self).__init__()

        self.stores = set(stores)
        self._oldfields = {}
        self.fields = fields

        self.commit()

    def __setattr__(self, key, value):

        if key[0] != '_' or key in self.__slots__:
            super(Record, self).__setattr__(key, value)

        else:

            # apply field descriptor if exists
            fielddesc = getattr(self.__class__, key, None)
            if isinstance(fielddesc, FieldDescriptor):
                value = fielddesc.getvalue(value, name=key)

            oldvalue = self.fields.get(key)

            if oldvalue != value:

                self.fields[key] = value
                self._oldfields.setdefault(key, oldvalue)

    def __getattr__(self, key):
        """Try to redirect input attribute name to self values."""

        return self.fields[key]

    @property
    def isdirty(self):
        """True if values are updated from the last commit.

        :rtype: bool"""

        return self._oldfields

    def cancel(self):
        """Cancel modifications."""

        self.fields.update(self._oldfields)
        self._oldfields.clear()

    def commit(self, stores=None):
        """Apply new values on this stores.

        :param set stores: stores to add to this record stores."""

        if stores is not None:
            self.stores |= stores

        if not self.stores:
            raise Record.Error('No store to commit add/update {0}'.format(self))

        for store in self.stores:
            store.update(record=self, upsert=True)

        self._oldfields.clear()

    def delete(self, stores=None):
        """Delete this record in stores.

        :param list stores: stores where delete this record. This stores by
            default.
        """

        if stores is None:
            stores = self.stores

        for store in stores:
            store.delete(self)
