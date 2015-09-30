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

"""Synchronizer module."""

from b3j0f.conf import (
    ConfigurableRegistry, Parameter, add_category, conf_paths
)

from .store import Store
from .access import Accessor

__all__ = ['Synchronizer']


@conf_paths('sync.conf')
@add_category('SYNC', [Parameter('stores')])
class Synchronizer(ConfigurableRegistry):
    """In charge of synchronizing Stores.
    """

    def __init__(self, stores):
        """
        :param Store(s) stores: Stores to synchronize.
        """

        # init protected attributes
        self._stores = None
        # synchronizing stores
        self._synchonizingstores = set()

        # set attributes
        self.stores = stores

    @property
    def stores(self):
        """Get self stores.

        :return: list of stores.
        :rtype: list
        """

        return self._stores

    @stores.setter
    def stores(self, value):
        """Change of stores to use.

        :param list value: list of stores to use.
        """

        if self._stores is not None:

            for store in self._stores:
                store.observers.append(observer=self._trigger)

        self._stores = value

        for store in value:
            store.addobserver(observer=self._trigger)

    def _trigger(self, data, store, event, old=None):
        """Called when input element is created/updated/deleted from the input
        store.

        :param Data data: created/updated/deleted element.
        :param Store store: owner element.
        :param int event: data notified event.
        :param Data old: old data value.
        """

        stores = [selfstore for selfstore in self.stores if selfstore != store]

        for selfstore in stores:

            if event & Accessor.ADD:
                try:
                    selfstore.add(data=data, sync=False)
                except Store.Error:
                    try:
                        selfstore.update(data=data, old=old, sync=False)
                    except Store.Error:
                        pass

            elif event & Accessor.UPDATE:
                try:
                    selfstore.update(data=data, old=old, sync=False)
                except Store.Error:
                    try:
                        selfstore.add(data=data, sync=False)
                    except Store.Error:
                        pass

            elif event & Accessor.REMOVE:
                try:
                    selfstore.remelt(data=data, sync=False)
                except Store.Error:
                    pass

    def sync(self, data=None, store=None):
        """Synchronize stores.

        :param Data(s) data: data to synchronize.
        :param Store(s) store: store to synchronize. Default
        """

        events = Accessor.ADD | Accessor.UPDATE

        for store in self.stores:

            for data in store:

                self._trigger(data=data, store=store, event=events)
