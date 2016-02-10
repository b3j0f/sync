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

__all__ = ['Synchronizer']

from .core import Store

from six import reraise


class Synchronizer(Store):
    """Manage synchronization of stores."""

    class Error(Exception):
        """handle synchronizer errors."""

    DEFAULT_COUNT = 5000  #: default synchronization count per step.

    def __init__(
            self, source=None, targets=None, count=DEFAULT_COUNT,
            *args, **kwargs
    ):
        """
        :param Store source: source store from where get data to sync.
        :param list targets: target stores to synchronize with the source.
        :param int count: number of data to sync per iteration.
        """

        super(Synchronizer, self).__init__(
            source=source, targets=targets, count=count, *args, **kwargs
        )

    def synchronize(
            self, rtype, fields=None, source=None, targets=None, count=None
    ):
        """Synchronize the source store with target stores.

        :param type rtype: record type to synchronize.
        :param dict fields: matching data content to retrieve from the source.
        :param Store source: store from where get data.
        :param list targets: stores from where put data.
        :param int count: number of data to synchronize iteratively.
        """

        if source is None:
            source = self.source

        if targets is None:
            targets = self.targets

        if count is None:
            count = self.count

        skip = 0

        while True:
            records = source.find(
                rtype=rtype, fields=fields, skip=skip, limit=count
            )
            if records:
                for target in targets:
                    try:
                        target.update(records=records, upsert=True)

                    except Exception as e:
                        reraise(Store.Error, Store.Error(e))

                skip += count

            else:
                break

    def _execute(self, func, source=False, store=None, *args, **kwargs):
        """
        :param str func: store func name to execute.
        :param bool many: if True, apply func on all stores. Otherwise, stop to
            apply func as soon as a storage has not raised an error.
        :param Store store: store where apply the func. Default is self source
            and targets.
        :param tuple args: func var arguments.
        :param dict kwargs: func keyword arguments.
        :return: func result if not many. Otherwise, an array of func results.
        """

        result = None

        stores = [self.source] if source else self.targets

        for store in stores:
            try:
                sresult = getattr(store, func)(*args, **kwargs)

            except Exception as e:
                pass

            else:
                if source:
                    result = sresult
                    break

                else:
                    result += sresult

        return result

    def create(self, rtype, fields=None):
        """Create a record from the source store.

        :param type rtype: records type to create from the store.
        :param dict fields: specific values to use such as the store data
            content."""

        return self._execute(
            func='create', source=True, rtype=rtype, fields=fields
        )

    def add(self, records):
        """Add records in a store.

        :param list records: records to add to the store."""

        return self._execute(func='add', records=records, source=False)

    def update(self, records, upsert=False):
        """Update records in a store.

        :param list records: records to update in the input store.
        :param bool upsert: if True (default False), add the record if not exist
        ."""

        return self._execute(
            func='update', upsert=upsert, records=records, source=False
        )

    def get(self, record):
        """Get a record from the sourcce store.

        :param Record record: record to get from the store.
        :rtype: Record"""

        return self._execute(func='get', record=record, source=True)

    def find(self, rtype, fields, limit=None, skip=None):
        """Find records from the source.

        :param int limit: maximal number of records to retrieve.
        :param int skip: number of elements to avoid.
        :rtype: list"""

        return self._execute(
            func='find', source=True,
            rtype=rtype, fields=fields, limit=limit, skip=skip
        )

    def remove(self, records=None, rtype=None, fields=None):
        """Remove records from target stores.

        :param list records: records to remove.
        :param type rtype: record type to remove.
        :param dict fields: data content to filter."""

        return self._execute(
            func='remove', source=False,
            records=records, rtype=rtype, fields=fields
        )
