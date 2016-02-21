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

"""Accessor definition module."""

__all__ = ['StoreRegistry']

from ..record.core import Record

from .core import Store

from six import reraise


class StoreRegistry(Record):
    """Manage stores.

    This class is used for synchronizing stores or for executing methods of CRUD
    on several stores.
    """

    class Error(Exception):
        """handle synchronizer errors."""

    DEFAULT_COUNT = 5000  #: default synchronization count per step.

    def __init__(self, stores=None, count=DEFAULT_COUNT, *args, **kwargs):
        """
        :param list stores: stores to synchronize.
        :param int count: number of data to sync per iteration.
        """

        super(StoreRegistry, self).__init__(
            stores=stores, count=count, *args, **kwargs
        )

    def synchronize(
            self,
            rtypes=None, data=None, sources=None, targets=None, count=None
    ):
        """Synchronize the source store with target stores.

        :param list rtypes: record types to synchronize.
        :param dict data: matching data content to retrieve from the sources.
        :param list sources: stores from where get data. Default self stores.
        :param list targets: stores from where put data. Default self stores.
        :param int count: number of data to synchronize iteratively.
        """

        if sources is None:
            sources = self.stores

        if rtypes is None:
            rtypes = set()
            for source in sources:
                rtypes |= set(source.rtypes)

            rtypes = list(rtypes)

        if targets is None:
            targets = self.stores

        if count is None:
            count = self.count

        for source in sources:

            skip = 0

            while True:
                records = source.find(
                    rtypes=rtypes, data=data, skip=skip, limit=count
                )

                if records:
                    for target in targets:
                        try:
                            target.update(records=records, upsert=True)

                        except Store.Error as ex:
                            reraise(
                                StoreRegistry.Error, StoreRegistry.Error(ex)
                            )

                    skip += count

                else:
                    break

    def _execute(self, func, stores=None, *args, **kwargs):
        """
        :param str func: store func name to execute.
        :param list stores: stores where apply the func. Default is self source
            and targets.
        :param tuple args: func var arguments.
        :param dict kwargs: func keyword arguments.
        :return: func result if not many. Otherwise, an array of func results.
        """

        result = {}

        if stores is None:
            stores = self.stores

        for store in stores:
            try:
                result[store] = getattr(store, func)(*args, **kwargs)

            except Store.Error:
                continue

        return result

    def add(self, records, stores=None):
        """Add records in a store.

        :param list records: records to add to the store.
        :param list stores: specific stores to use.
        :return: added records by store.
        :rtype: dict"""

        return self._execute(func='add', records=records, stores=stores)

    def update(self, records, upsert=False, stores=None):
        """Update records in a store.

        :param list records: records to update in the input store.
        :param bool upsert: if True (default False), add record if not exist.
        :param list stores: specific stores to use.
        :return: updated records by store.
        :rtype: dict"""

        return self._execute(
            func='update', upsert=upsert, records=records, stores=stores
        )

    def get(self, record, stores=None):
        """Get a record from stores.

        :param Record record: record to get from the store.
        :param list stores: specific stores to use.
        :return: record by store.
        :rtype: dict"""

        return self._execute(func='get', record=record, stores=stores)

    def find(
            self, stores=None,
            rtypes=None, data=None, limit=None, skip=None, sort=None,
    ):
        """Find records from stores.

        :param int limit: maximal number of records to retrieve.
        :param int skip: number of elements to avoid.
        :param list sort: data field name to sort.
        :param list rtypes: record types to find. Default is all.
        :param list stores: specific stores to use.
        :return: records by store.
        :rtype: dict"""

        return self._execute(
            func='find', stores=stores,
            rtypes=rtypes, data=data, limit=limit, skip=skip, sort=sort
        )

    def remove(self, records=None, rtypes=None, data=None, stores=None):
        """Remove records from target stores.

        :param list records: records to remove.
        :param list rtypes: record types to remove.
        :param dict data: data content to filter.
        :param list stores: specific stores to use.
        :return: removed records by store.
        :rtype: dict
        """

        return self._execute(
            func='remove',
            records=records, rtypes=rtypes, data=data, stores=stores
        )
