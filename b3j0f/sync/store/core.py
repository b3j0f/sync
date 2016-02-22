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

from ..record.core import Record
from ..accessor.registry import AccessorRegistry

from six import reraise


class Store(Record):
    """Store records.

    A Store can be a database or a github account for example.

    Beceause it is mainly an interface, results are sorted by store in order
    to identify which real store corresponds to results."""

    class Error(Exception):
        """Handle Store errors."""

    def __init__(self, accessors=None, *args, **kwargs):

        super(Store, self).__init__(*args, **kwargs)

        self._accreg = AccessorRegistry(accessors=accessors)

    @property
    def rtypes(self):
        """Get all record types registered by accessors.

        :rtype: list"""

        result = []

        for accessor in self.accessors:
            result += accessor.__rtypes__

        return result

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

    def record2data(self, record, dirty=True):
        """Get a specific store data from a record.

        :param Record record: record to convert to a data.
        :param bool dirty: if True (default) get dirty values in record2data.
        """

        return self._execute(cmd='record2data', record=record, dirty=dirty)

    def data2record(self, rtype, data=None):
        """Create a record with input type and store data values.

        :param type rtype: record type.
        :param dict data: record data to use in a store context.
        :rtype: Record.
        :raises: Store.Error in case of error."""

        return self._execute(cmd='data2record', rtype=rtype, data=data)


    def _execute(self, cmd, **kwargs):
        """Get kwargs by accessor.

        :param str cmd: command name to execute on accessors.
        :param bool multi: flag for multi result or not.
        :return: accessor command result(s)."""

        result = []

        acckwargs = {}

        multi = 'records' in kwargs or 'rtypes' in kwargs

        if multi:
            if 'records' in kwargs:
                records = kwargs.pop('records')

                if records is not None:
                    for record in records:
                        accessor = self._accreg.get(record.__class__)
                        params = acckwargs.setdefault(accessor, {})
                        params.setdefault('records', []).append(record)

            if 'rtypes' in kwargs:
                rtypes = kwargs.pop('rtypes')

                if rtypes is None:
                    rtypes = self.rtypes

                for rtype in rtypes:
                    accessor = self._accreg.get(rtype)
                    params = acckwargs.setdefault(accessor, {})
                    params.setdefault('rtypes', []).append(rtype)

        else:
            if 'record' in kwargs:
                record = kwargs['record']
                accessor = self._accreg.get(record.__class__)
                acckwargs[accessor] = {'record': record}


            if 'rtype' in kwargs:
                rtype = kwargs['rtype']
                accessor = self._accreg.get(rtype)
                acckwargs[accessor] = {}

        rstorecmd = cmd if cmd == 'remove' else 'add'  # record store command

        for accessor in acckwargs:
            params = acckwargs[accessor]
            params.update(kwargs)

            try:
                accres = getattr(accessor, cmd)(store=self, **params)

            except Exception as ex:
                reraise(Store.Error, Store.Error(ex))

            else:
                if multi:
                    result += accres

                    for record in accres:
                        if isinstance(record, Record):
                            getattr(record.stores, rstorecmd)(self)

                else:
                    result = accres
                    if isinstance(accres, Record):
                        getattr(accres.stores, rstorecmd)(self)

        return result

    def add(self, records):
        """Add records and register this in stores of records.

        Register this store to record stores if record is added.

        :param list records: records to add. Must be same type.
        :return: added records.
        :rtype: list
        :raises: Store.Error in case of error."""

        return self._execute(cmd='add', records=records)

    def update(self, records, upsert=False, override=False):
        """Update records in this store and register this in stores of records.

        :param list records: records to update in this store. Must be same type.
        :param bool upsert: if True (False by default), add the record if not
            exist.
        :param bool override: if False (default), check before if records to
            update are different in this store.
        :return: updated records.
        :rtype: list
        :raises: Store.Error in case of error."""

        if not override:  # update records which are differents
            frecords = self.find(records=records)
            records = list(set(records) - set(frecords))

        return self._execute(cmd='update', records=records, upsert=upsert)

    def get(self, record):
        """Get input record from this store.

        The found record matches with input record identifier and not all field
        values. The identifier depends on the store.

        :param Record record: record to get from this store.
        :return: corresponding record.
        :rtype: Record
        :raises: Store.Error in case of error."""

        return self._execute(cmd='get', record=record)

    def __getitem__(self, key):

        return self.get(record=key)

    def count(self, rtypes=None, data=None):
        """Get number of data in a store.

        :param list rtype: record types. Default is self.rtypes
        :param dict data: data content to filter.
        :rtype: int."""

        return self._execute(cmd='count', rtypes=rtypes, data=data)

    def find(self, rtypes=None, records=None, data=None, limit=None, skip=None, sort=None):
        """Find records related to type and data and register this to result
        stores.

        :param list rtypes: record types to find. Default is self.rtypes.
        :param list records: records to find.
        :param dict data: record data to filter. Default None.
        :param int limit: maximal number of documents to retrieve.
        :param int skip: number of elements to avoid.
        :param list sort: data field name to sort.
        :return: records of input type and field values.
        :rtype: list
        :raises: Store.Error in case of error.
        """

        return self._execute(
            cmd='find',
            rtypes=rtypes, records=records, data=data,
            limit=limit, skip=skip, sort=sort
        )

    def remove(self, records=None, rtypes=None, data=None):
        """Remove input record from this.

        :param list records: records to remove.
        :param list rtypes: record types to remove.
        :param dict data: date value to filter.

        :raises: Store.Error in case of error."""

        result = self._execute(
            cmd='remove', records=records, rtypes=rtypes, data=data
        )

        return result

    def __delitem__(self, record):

        self.remove(records=[record])

        return self

    def __iadd__(self, records):
        """Add record(s).

        :param Record(s) records: records to add to this store.
        """

        if isinstance(records, Record):
            records = [records]

        self.add(records=records)

        return self

    def __ior__(self, records):
        """Update record(s) with upsert flag equals True.

        :param Record(s) records: records to update to this store.
        """

        if isinstance(records, Record):
            records = [records]

        self.update(records=records, upsert=True)

        return self

    def __isub__(self, records):
        """Remove record(s) to this store.

        :param Record(s) records: records to remove from this store.
        """

        if isinstance(records, Record):
            records = [records]

        self.remove(records=records)

        return self

    def __contains__(self, other):

        result = True

        try:
            result = self.get(other) is not None

        except Store.Error:
            result = False

        return result
