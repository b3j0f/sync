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

"""Record definition module."""

__all__ = ['Record']

from inspect import getmembers

from .field import Field

from six import add_metaclass


class _MetaRecord(type):
    """Apply field descriptors on record field values."""

    def __call__(cls, *args, **kwargs):

        for name, member in getmembers(cls):

            if isinstance(member, Field):

                value = kwargs.get(name)

                value = member.getvalue(value=value, name=name)

                kwargs[name] = value

        result = type.__call__(cls, *args, **kwargs)

        return result


@add_metaclass(_MetaRecord)
class Record(object, metaclass=_MetaRecord):
    """Record object which embeds data values."""

    class Error(Exception):
        """Handle record errors."""

    __slots__ = ('_stores', '_fields', '_oldfields')

    def __init__(self, _stores=None, **fields):
        """
        :param Stores stores: stores to use in this record.
        :param fields: record field values.
        """

        super(Record, self).__init__()

        self._stores = set([] if _stores is None else _stores)
        self._oldfields = {}
        self._fields = fields

        self.commit()

    def __setattr__(self, key, value):

        if key[0] == '_' or key in self.__slots__:
            super(Record, self).__setattr__(key, value)

        else:
            # apply field descriptor if exists
            fielddesc = getattr(self.__class__, key, None)
            if isinstance(fielddesc, Field):
                value = fielddesc.getvalue(value, name=key)

            oldvalue = self._fields.get(key)

            if oldvalue != value:

                self._fields[key] = value
                self._oldfields.setdefault(key, oldvalue)

    def __getattribute__(self, key):

        return object.__getattribute__(self, '_fields').get(
            key, object.__getattribute__(self, key)
        )

    def __getattr__(self, key):
        """Try to redirect input attribute name to self values."""

        result = None

        try:
            result = self._fields[key]

        except KeyError:
            raise Record.Error('No field {0}'.format(key))

        return result

    @property
    def isdirty(self):
        """True if values are updated from the last commit.

        :rtype: bool"""

        return not not self._oldfields

    def cancel(self):
        """Cancel modifications."""

        self._fields.update(self._oldfields)
        self._oldfields.clear()

    def commit(self, stores=None):
        """Apply new values on this stores.

        :param set stores: stores to add to this record stores."""

        if stores is not None:
            self._stores |= stores

        for store in self._stores:
            store.update(record=self, upsert=True)

        self._oldfields.clear()

    def delete(self, stores=None):
        """Delete this record in stores.

        :param list stores: stores where delete this record. This stores by
            default.
        """

        if stores is None:
            self._stores |= stores

        for store in stores:
            store.delete(self)
