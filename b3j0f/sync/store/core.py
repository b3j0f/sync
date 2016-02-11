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

"""Store definition module."""

__all__ = ['Store']

from collections import Iterable

from ..record.core import Record
from ..accessor.registry import AccessorRegistry

from six import reraise


class Store(Record):
    """Store records.

    A Store can be a database or a github account for example."""

    class Error(Exception):
        """Handle Store errors."""

    def __init__(self, accessors=None, *args, **kwargs):

        super(Store, self).__init__(*args, **kwargs)

        self._accreg = AccessorRegistry(accessors=accessors)

    @property
    def accessors(self):
        """Get accessors.

        :rtype: list"""

        return list(self._accreg.values())

    @accessors.setter
    def accessors(self, value):
        """Change of accessors.

        :param list value: accessors to register in this store."""

        self._accreg.clear()
        self._accreg.register(accessors=value)

    def _getaccessor(self, aparam):
        """Get the right accessor able to process input record.

        :param aparam: record(s) to process with the output accessor.
        :type aparam: Record, type or list
        :raises: Store.Error if no accessor is available."""

        record = (
            aparam[0]
            if (isinstance(aparam, Iterable) and aparam)
            else aparam
        )

        result = self._accreg.get(record)

        if result is None:
            raise Store.Error('No store found to process {0}'.format(record))

        return result

    def _execute(self, func, record=None, records=None, rtype=None, **kwargs):
        """Execute input func name to the right accessor choosen with input
        aparam.

        :param str func: accessor func name.
        :param aparam: accessor selector.
        :param dict kwargs: function keyword arguments.
        :return: func result.
        """

        if records is not None:
            aparam = kwargs['records'] = records

        elif record is not None:
            aparam = kwargs['record'] = record

        else:
            aparam = kwargs['rtype'] = rtype

        accessor = self._getaccessor(aparam)

        try:
            result = getattr(accessor, func)(store=self, **kwargs)

        except Exception as e:
            reraise(Store.Error, Store.Error(e))

        else:
            if isinstance(result, Iterable):
                for record in result:
                    if self not in record.stores:
                        record.stores.append(self)

            elif isinstance(result, Record):
                if self not in result.stores:
                    result.stores.append(self)

        return result

    def create(self, rtype, data=None):
        """Create a record with input type and field values.

        :param type rtype: record type.
        :param dict data: record data to use in a store context.
        :rtype: Record.
        :raises: Store.Error in case of error."""

        result = self._execute(func='create', rtype=rtype, data=data)

        self.add(records=[result])

        return result

    def add(self, records):
        """Add records and register this in stores of records.

        Register this store to record stores if record is added.

        :param list records: records to add. Must be same type.
        :return: added records.
        :rtype: list
        :raises: Store.Error in case of error."""

        result = self._execute(func='add', records=records)

        return result

    def update(self, records, upsert=False):
        """Update records in this store and register this in stores of records.

        :param list records: records to update in this store. Must be same type.
        :param bool upsert: if True (False by default), add the record if not
            exist.
        :return: updated records.
        :rtype: list
        :raises: Store.Error in case of error."""

        result = self._execute(func='update', records=records, upsert=upsert)

        return result

    def get(self, record):
        """Get input record from this store.

        The found record matches with input record identifier and not all field
        values. The identifier depends on the store.

        :param Record record: record to get from this store.
        :return: corresponding record.
        :rtype: Record
        :raises: Store.Error in case of error."""

        result = self._execute(func='get', record=record)

        return result

    def __getitem__(self, key):

        return self.get(record=key)

    def count(self, rtype, data=None):
        """Get number of data in a store.

        :param type rtype: record type.
        :param dict data: data content to filter.
        :rtype: int."""

        return self._execute(func='count', rtype=rtype, data=data)

    def find(self, rtype, data=None, limit=None, skip=None):
        """Find records related to type and data and register this to result
        stores.

        :param type rtype: record type to find.
        :param dict data: record data to filter. Default None.
        :param int limit: maximal number of documents to retrieve.
        :param int skip: number of elements to avoid.
        :return: records of input type and field values.
        :rtype: list
        :raises: Store.Error in case of error.
        """

        result = self._execute(
            func='find', rtype=rtype, data=data, limit=limit, skip=skip
        )

        return result

    def remove(self, records, rtype=None, data=None):
        """Remove input record and unregister this store from record stores.

        :param list records: records to remove.
        :param type rtype: record type to remove.
        :param dict data: data content to filter.
        :raises: Store.Error in case of error.
        """

        result = self._execute(
            func='remove', rtype=rtype, records=records, data=data
        )

        for record in records:
            while self in record.stores:
                record.stores.remove(self)

        return result

    def __delitem__(self, record):

        self.remove(records=[record])

    def __iadd__(self, records):
        """Add record(s).

        :param Record(s) records: records to add to this store.
        """

        if isinstance(records, Record):
            records = [records]

        self.add(records=records)

    def __ior__(self, records):
        """Update record(s) with upsert flag equals True.

        :param Record(s) records: records to update to this store.
        """

        if isinstance(records, Record):
            records = [records]

        self.update(records=records, upsert=True)

    def __isub__(self, records):
        """Remove record(s) to this store.

        :param Record(s) records: records to remove from this store.
        """

        if isinstance(records, Record):
            records = [records]

        self.remove(records=records)
