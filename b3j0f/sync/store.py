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

"""Store module in charge of storing data."""

from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup
from b3j0f.conf import Configurable, Parameter, add_category
from b3j0f.sync.data import Data
from b3j0f.sync.access import Accessor

from inspect import isclass


class MetaStore(type):
    """Handle Store instantiation with autoconnection."""

    def __call__(cls, *args, **kwargs):

        result = super(MetaStore, cls).__call__(*args, **kwargs)

        if result.autoconnect:  # connect the store if autoconnect
            result.connect()

        return result


@add_category('STORE', Parameter('accessors', parser=Parameter.dict))
class Store(Configurable):
    """Abstract class in charge of reading development management project
    datum.

    First, you can connect to a dmt in a public way (without params), or in a
    private way with login, password, token or oauth token.
    """

    CATEGORY = 'STORE'  #: store category configuration name.

    class Error(Exception):
        """Handle store errors."""

    def __init__(
            self, handlers=None, autoconnect=True, accessors=None,
            *args, **kwargs
    ):
        """
        :param list handlers: handlers which listen to data
            creation/modification/deletion.
        :param bool autoconnect: if True, connect this at the end of this
            execution.
        :param dict accessors: Data accessors by name.
        """

        super(Store, self).__init__(*args, **kwargs)

        # set protected attributes
        self._accessors = accessors

        # set public attributes
        self.handlers = handlers
        self.autoconnect = autoconnect

    @property
    def accessors(self):
        """Get accessors.

        :rtype: dict
        """

        return self._accessors

    @accessors.setter
    def accessors(self, value):
        """Change of accessors by name.

        :param dict value: value of accessors. Values can be str or Accessor
            classes or even Accessor instances. In first two cases, final
            accessor values will tried to be resolved and instantiated with
            this such as the ``store`` paramater.
        """

        for name in value:
            accessor = value[name]
            if isinstance(accessor, basestring):
                accessor = lookup(accessor)(store=self)

            elif isclass(accessor):
                accessor = accessor(store=self)

            if isinstance(accessor, Accessor):
                self._accessors[name] = accessor

            else:
                raise Accessor.Error(
                    'Wrong accessor value at {0} in {1}.'.format(
                        name, value
                    )
                )

    def connect(self):
        """Connect to the remote data with self attributes."""

        raise NotImplementedError()

    def sync(self, data, event):
        """Notify all handlers about data creation/modification/deletion."""

        for handler in self.handlers:  # sync all handlers
            handler(data=data, event=event, store=self)

    @staticmethod
    def _otherdata(other):
        """Return a set of datum from other.

        :param other: other datum.
        :type other: Store or Data(s)
        :return: set of datum.
        :rtype: set
        """

        result = other

        if isinstance(other, Store):
            result = other.find()

        elif isinstance(other, Data):
            result = (other, )

        result = set(result)

        return result

    def __contains__(self, other):
        """True if this contains input data(s).

        :param Data(s) other: data(s) which might exist in this.
        :return: True iif input data(s) exist in this store.
        :rtype: bool
        """

        result = False

        datum = Store._otherdata(other=other)

        selfelements = set(self.find())

        result = len(selfelements & datum) == min(
            len(selfelements), len(datum)
        )

        return result

    def __iter__(self):
        """Iterator on all this datum."""

        datum = self.find()

        result = iter(datum)

        return result

    def __and__(self, other):
        """Return a list of datum which are both in this and in input
        data(s).

        :param Data(s) other:
        :return: list of datum contained in this and in input datum.
        :rtype: list
        """

        datum = Store._otherdata(other=other)

        selfelements = set(self.find())

        result = datum & selfelements

        return result

    def __iadd__(self, other):
        """Add an other data(s) and sync handlers."""

        datum = Store._otherdata(other=other)

        for data in datum:
            self.add(data=data)

    def __or__(self, other):
        """Return a list of datum which are in this store or in input
        data(s).

        :param Data(s) other:
        :return: list of datum contained in this or in input datum.
        :rtype: list
        """

        datum = Store._otherdata(other)

        selfelements = set(self.find())

        result = datum | selfelements

        return result

    def __ior__(self, other):
        """Update data(s) and sync handlers.

        :param Data(s) other: data(s) to update.
        """

        datum = Store._otherdata(other)

        for data in datum:
            self.update(data=data)

    def __sub__(self, other):
        """Return a list of datum which are in this store and not in
        input data(s).

        :param Data(s) other:
        :return: list of datum contained in this and not in input datum.
        :rtype: list
        """

        datum = Store._otherdata(other)

        selfelements = self.find()

        result = datum - selfelements

        return result

    def __isub__(self, other):
        """Delete datum and sync handlers."""

        datum = Store._otherdata(other)

        for data in datum:
            self.remove(data=data)

    def __iand__(self, other):
        """Delete datum which are not in other datum, return the
        intersection  and sync handlers.

        :param Data(s) other: datum to keep.
        :return: kept datum.
        :rtype: list
        """

        datum = Store._otherdata(other)

        selfelements = self.find()

        elementstoremove = [
            data for data in selfelements if data not in datum
        ]

        self -= elementstoremove

    def __setitem__(self, key, item):
        """Change of data and sync handlers.

        :param Data key: old data value.
        :param Data data: new data value.
        """

        self.updateelt(data=item, old=key)

    def _getaccessor(self, datatype):
        """Get an accessor by data type.

        :param type datatype: Data type covered by the accessor.
        :return: related data type accessor.
        :rtype: Accessor
        :raises: Store.Error if no related accessor exist.
        """

        result = None

        for accessor in self.accessors:
            if accessor.datatype == datatype:
                result = accessor
                break
        else:
            raise Store.Error(
                'No accessor for {0} available'.format(datatype)
            )

        return result

    def _processdata(self, data, processname, **kwargs):
        """Process input data with input accessor process function name and
            event notification in case of success. The process successes if its
            result is an Data.

        :param Data data: data to process.
        :param processname: accessor processing function. Takes in parameter
            input data and returns an data if processing succeed.
        :param kwargs: additional processing parameters.
        :return: process data result.
        :rtype: Data
        :raises: Store.Error if a processing error occured.
        """

        result = None

        try:
            accessor = self._getaccessor(datatype=type(data))
            process = getattr(accessor, processname)
            result = process(data=data, **kwargs)

        except Accessor.Error as ex:  # embed error in store error
            raise Store.Error(ex)

        return result

    def get(self, _id, datatype, pids=None):
        """Get data by id and type.

        :param int _id: data id.
        :param type datatype: data type. Subclass of Data.
        :param str pids: parent data ids if exist.
        :return: data which corresponds to input _id and _type.
        :rtype: Data
        """

        return self._getaccessor(datatype=datatype).get(_id=_id, pids=pids)

    def find(
            self,
            ids=None, descs=None, created=None, updated=None, datatypes=None,
            **kwargs
    ):
        """Get a list of datum matching with input parameters.

        :param list ids: data ids to retrieve. If None, get all
            datum.
        :param list descs: list of regex to find in data description.
        :param datetime created: starting creation time.
        :param datetime updated: starting updated time.
        :param dict kwargs: additional elemnt properties to select.
        :param type datatype: data classes to retrieve. Subclass of Data.
        :return: list of Elements.
        :rtype: list
        """

        result = []

        if not datatypes:
            datatypes = (
                accessor.datatype for accessor in self.accessors.values()
            )

        for datatype in datatypes:
            accessor = self._getaccessor(datatype=datatype)
            elts = accessor.find(
                ids=ids, descs=descs, created=created, updated=updated
            )
            result += elts

        return result

    def add(self, data, sync=True):
        """Add input data.

        :param Data data: data to add.
        :param bool sync: if True (default), sync handlers.
        :return: added data.
        :raises: Store.Error if data already exists or information are
            missing.
        """

        return self._processdata(data=data, sync=sync, processname='add')

    def update(self, data, old=None, sync=True):
        """Update input data.

        :param Data data: data to update.
        :param Data old: old data value.
        :param bool sync: if True (default), sync handlers.
        :return: updated data.
        :rtype: Data
        :raises: Store.Error if not upsert and data does not exist or
            critical information are not similars.
        """

        return self._processdata(
            data=data, old=old, sync=sync, processname='update'
        )

    def remove(self, data, sync=True):
        """Remove input data.

        :param Data data: data to delete.
        :param bool sync: if True (default), sync handlers.
        :return: deleted data.
        :rtype: Data
        :raises: Store.Error if data does not exist.
        """

        return self._processdata(
            data=data, sync=sync, processname='remove'
        )
