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

from six import add_metaclass, string_types

from copy import deepcopy

from b3j0f.utils.iterable import hashiter

from .field import Field


class _MetaRecord(type):
    """Apply field descriptors on record field values and ensure records are
    commited at the end of their initialization."""

    def __call__(cls, *args, **kwargs):

        for name, member in getmembers(cls):

            if isinstance(member, Field):

                value = kwargs.get(name)

                value = member.getvalue(value=value, name=name)

                kwargs[name] = value

        result = type.__call__(cls, *args, **kwargs)

        result.commit()

        return result


@add_metaclass(_MetaRecord)
class Record(object):
    """Embed a data value such as a dictionary.

    Data values are all public attributes (given in the constructor such as the
    main kwargs parameter or setted at runtime).

    All those public attributes can be retrieved thanks to the raw method.

    Once a record is bound to a store, it is possible to sequentially modify
    data values, and commit change in the store with the commit method, or
    cancel changes with the change method.

    The property ``isdirty`` is True if the record is modified from its creation
    or last commit.

    The copy method is the implementation of the prototype design pattern."""

    class Error(Exception):
        """Handle record errors."""

    __slots__ = ('_stores', '_data', '_olddata')

    def __init__(self, _stores=None, **data):
        """
        :param Stores stores: stores to use in this record.
        :param data: record field values.
        """

        super(Record, self).__init__()

        self._data = data
        self._olddata = {}
        self._stores = set() if _stores is None else set(_stores)

    def __setattr__(self, key, value):

        inheritance = key[0] == '_'
        if not inheritance:
            superattr = getattr(self.__class__, key, None)
            inheritance = not(superattr is None or isinstance(superattr, Field))

        if inheritance:
            super(Record, self).__setattr__(key, value)

        else:
            # apply field descriptor if exists
            fielddesc = getattr(self.__class__, key, None)
            if isinstance(fielddesc, Field):
                value = fielddesc.getvalue(value, name=key)

            oldvalue = self._data.get(key)

            if oldvalue != value:

                self._data[key] = value
                self._olddata.setdefault(key, oldvalue)

    def __getattribute__(self, key):

        supergetattribute = super(Record, self).__getattribute__

        return supergetattribute('_data').get(key, supergetattribute(key))

    def __getattr__(self, key):
        """Try to redirect input attribute name to self values."""

        result = None

        try:
            result = self._data[key]

        except KeyError:
            raise AttributeError('No field {0}'.format(key))

        return result

    @property
    def isdirty(self):
        """True if values are updated from the last commit.

        :rtype: bool"""

        return not not self._olddata

    @property
    def stores(self):
        """get this stores."""

        return self._stores

    @stores.setter
    def stores(self, value):
        """Change of stores value.

        :param list stores: stores to use."""

        self._stores = value

    def cancel(self):
        """Cancel modifications."""

        self._data.update(self._olddata)
        for key in list(self._data):
            val = self._data[key]

            if val is None:
                del self._data[key]

        self._olddata.clear()

    def commit(self, stores=None):
        """Apply new values on stores.

        :param set stores: stores to add to this record stores. Default this
            stores."""

        if stores is None:
            stores = self._stores

        for store in list(stores):
            store.update(records=[self], upsert=True)

            self._stores.add(store)

        self._olddata.clear()

    def delete(self, stores=None):
        """Remove this record from stores.

        :param list stores: stores where to delete this record. This stores by
            default."""

        if stores is None:
            stores = self._stores

        for store in list(stores):
            try:
                store.remove(records=[self])

            except Exception:
                pass

            else:
                try:
                    self._stores.remove(store)

                except KeyError:
                    pass

    def __del__(self):

        self.delete()

    def copy(self, data=None, stores=None):
        """Copy this record with input data values.

        Stores are not copied.

        :param dict data: new data content to use.
        :param list stores: default stores to use.
        :rtype: Record"""

        _data = self._data

        if data is not None:
            _data.update(deepcopy(data))

        return self.__class__(_stores=stores, **deepcopy(_data))

    def __deepcopy__(self, memo):

        for key in list(memo):
            if not isinstance(key, string_types):
                del memo[key]

        return self.copy(data=memo)

    def raw(self, dirty=True, store=None, _raws=None):
        """Get raw data value.

        :param bool dirty: if True (default) get dirty values in raw.
        :param dict _raws: private parameter used to save rawed records in a
            recursive call.
        :param Store store: store from where get the raw if given.
        :return: specific store data if store is not None, otherwise a
            dictionary with public values."""

        result = None

        if store is None:
            result = deepcopy(self._data)

            if not dirty:
                result.update(deepcopy(self._olddata))

            for name in result.keys():  # convert inner records to raw
                value = result[name]
                if isinstance(value, Record):
                    if _raws is None:
                        _raws = {}
                    value = _raws[value] = _raws.setdefault(
                        value, value.raw(dirty=dirty, _raws=_raws)
                    )
                    result[name] = value

        else:
            result = store.record2data(dirty=dirty, record=self)

        return result

    def __eq__(self, other):

        return hash(self) == hash(other)

    def __ne__(self, other):

        return not self.__eq__(other)

    def __repr__(self):

        stores = [id(store) for store in self.stores]

        return '{0}[{1}](data: {2}, olddata: {3}, stores: {4})'.format(
            self.__class__.__name__,
            id(self), self._data, self._olddata, stores
        )

    def __hash__(self):

        result = hash(self.__class__) * hashiter(self.raw())

        return result
