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
from b3j0f.utils.iterable import ensureiterable
from b3j0f.conf import Configurable, Parameter, add_category, conf_paths

from .model import Data
from .access import Accessor, getidwpids

from inspect import isclass

__all__ = ['Store']


class _MetaStore(Configurable.__metaclass__):
    """Handle Store instantiation with autoconnection."""

    def __call__(cls, *args, **kwargs):

        result = super(_MetaStore, cls).__call__(*args, **kwargs)

        if result.autoconnect:  # connect the store if autoconnect
            result.connect()

        return result


@conf_paths('store.conf')
@add_category(
    'STORE',
    [
        Parameter('accessors', parser=Parameter.dict),
        Parameter('autoconnect', parser=Parameter.bool)
    ]
)
class Store(Configurable):
    """Abstract class in charge of accessing to datum."""

    class Error(Exception):
        """Handle store errors."""

    __metaclass__ = _MetaStore

    CATEGORY = 'STORE'  #: store category configuration name.

    def __init__(
            self, observers=None, autoconnect=True, accessors=None,
            *args, **kwargs
    ):
        """
        :param list observers: observers which listen to data
            creation/modification/deletion.
        :param bool autoconnect: if True, connect this at the end of this
            execution.
        :param dict accessors: Data accessors by name.
        """

        super(Store, self).__init__(*args, **kwargs)

        # set protected attributes
        self._accessors = {}

        # set public attributes
        self.observers = {} if observers is None else observers
        self.autoconnect = autoconnect
        self.accessors = accessors

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
        :raises: Store.Error if value is not a dict.
        """

        if value is None:

            self._accessors.clear()

        elif isinstance(value, dict):

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

        else:
            raise Store.Error(
                'Wrong value {0}. dict expected'.format(value)
            )

    def addobserver(self, observer, event=Accessor.ALL):
        """Add an observer related to input event.

        :param observer: observer to add.
        :param int event: listening observer event. Default is ALL.
        """

        def _addobserver(_event):

            if event & _event:
                self.observers.setdefault(_event, set()).add(observer)

        _addobserver(Accessor.ADD)  # add for ADD events
        _addobserver(Accessor.UPDATE)  # add for UPDATE events
        _addobserver(Accessor.REMOVE)  # add for REMOVE events

    def removeobserver(self, observer, event=Accessor.ALL):
        """Remove an observer related to input event.

        :param observer: observer to remove.
        :param int event: stop listening observer event.
        """

        def _removeobserver(_event):

            if event & _event:  # if _event matches
                observers = self.observers.get(_event)  # get observers
                if observers:  # if observers is not empty
                    observers.remove(observer)  # remove the observer
                    if not observers:  # if observers[event] is empty
                        del self.observers[_event]  # remove it from observers

        _removeobserver(Accessor.ADD)  # remove for ADD events
        _removeobserver(Accessor.UPDATE)  # remove for UPDATE events
        _removeobserver(Accessor.REMOVE)  # remove for REMOVE events

    def connect(self):
        """Connect to the remote data with self attributes."""

        raise NotImplementedError()

    def disconnect(self):
        """Disconnect from remote data."""

        raise NotImplementedError()

    @property
    def isconnected(self):
        """
        :return: True iif this is connected.
        :rtype: bool
        """

        return self._isconnected()

    def _isconnected(self):
        """Method to override in order to known if this is connected.

        :return: True iif this is connected.
        :rtype: bool
        """

        raise NotImplementedError()

    def notify(self, data, event):
        """Notify all observers about data creation/modification/deletion."""

        observers = self.observers.get(event)

        if observers:
            for observer in observers:  # notify all observers
                observer(data=data, event=event, store=self)

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

        selfdatum = set(self.find())

        if datum and selfdatum:
            for data in datum:

                if data not in selfdatum:
                    break

            else:
                result = True

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

        result = Store._otherdata(other=other)

        selfdatum = set(self.find())

        result &= selfdatum

        return result

    def __iadd__(self, other):
        """Add an other data(s) and notify observers."""

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

        result = Store._otherdata(other)

        selfdatum = set(self.find())

        result |= selfdatum

        return result

    def __ior__(self, other):
        """Update data(s) and notify observers.

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

        result = Store._otherdata(other)

        selfdatum = self.find()

        result -= selfdatum

        return result

    def __isub__(self, other):
        """Delete datum and notify observers."""

        datum = Store._otherdata(other)

        for data in datum:
            self.remove(data=data)

    def __iand__(self, other):
        """Delete datum which are not in other datum, return the
        intersection  and notify observers.

        :param Data(s) other: datum to keep.
        :return: kept datum.
        :rtype: list
        """

        datum = Store._otherdata(other)

        selfdatum = self.find()

        elementstoremove = [data for data in selfdatum if data not in datum]

        self -= elementstoremove

    def __getitem__(self, key):

        if isinstance(key, Data):
            key = key._id

        _id, pids = getidwpids(globalid=key)

        return self.get(_id=_id, pids=pids)

    def __setitem__(self, key, item):

        if isinstance(key, Data):
            old = key

        else:
            old = self[key]

        self.update(data=item, old=old)

    def __delitem__(self, key):

        if isinstance(key, Data):
            data = key

        else:
            data = self[key]

        self.remove(data=data)

    def _getaccessor(self, datatype):
        """Get an accessor by data type.

        :param type datatype: Data type covered by the accessor.
        :return: related data type accessor.
        :rtype: Accessor
        :raises: Store.Error if no related accessor exist.
        """

        result = None

        for accessor in self.accessors.values():
            if accessor.__datatype__ == datatype:
                result = accessor
                break
        else:
            raise Store.Error(
                'No accessor for {0} available'.format(datatype)
            )

        return result

    def _processdata(self, process, data=None, accessor=None, **kwargs):
        """Process input data with input accessor process function name and
            event notification in case of success. The process successes if its
            result is an Data.

        :param Data data: data to process.
        :param process: accessor processing function. Takes in parameter
            input data and returns an data if processing succeed.
        :param str accessor: accessor name to use. By default, find the best
            accessor able to process data.
        :param kwargs: additional processing parameters.
        :return: process data result.
        :rtype: Data
        :raises: Store.Error if a processing error occured.
        """

        result = None

        if accessor is None:
            accessor = self._getaccessor(datatype=type(data))

        elif isinstance(accessor, basestring):
            accessor = self._accessors[accessor]

        if data is not None:  # add data to kwargs if given
            kwargs['data'] = data

        _process = getattr(accessor, process)

        try:
            result = _process(**kwargs)

        except Accessor.Error as ex:  # embed error in store error
            raise Store.Error(ex)

        return result

    def get(self, _id, accessor=None, pids=None, globalid=None):
        """Get data by id and type.

        :param int _id: data id.
        :param str accessor: accessor name to use. By default, return the first
            data where _id exists in any accessor.
        :param str pids: parent data ids if exist.
        :param str globalid: global id.
        :return: data which corresponds to input _id and _type.
        :rtype: Data
        """

        result = None

        if globalid is not None:
            _id, pids = getidwpids(globalid=globalid)

        if accessor is None:  # get the first data which corresponds to params
            for accessor in self._accessors:
                result = self._processdata(
                    process='get', _id=_id, pids=pids, accessor=accessor
                )
                if result is not None:  # if result is not None, leave the loop
                    break

        else:
            result = self._processdata(  # get specific accessor data
                process='get', _id=_id, pids=pids, accessor=accessor
            )

        return result

    def getbyname(self, name, pnames=None, globalname=None, accessor=None):
        """Get the first data corresponding with name and pnames or globalname.

        :param str accessor: accessor name to use.
        :param str name: data name to retrieve.
        :param list pnames: list of parent data names.
        :param str globalname: data global name.
        :return: First Data which corresponds to input name and pnames.
        :rtype: Data
        """

        result = None

        if globalname is not None:
            name, pnames = getidwpids(globalid=globalname)

        if accessor is None:  # get the first data which corresponds to params
            for accessor in self._accessors:
                result = self._processdata(
                    process='getbyname', name=name, pnames=pnames,
                    accessor=accessor
                )
                if result is not None:  # if result is not None, leave the loop
                    break

        else:
            result = self._processdata(  # get specific accessor data
                process='getbyname', name=name, pnames=pnames,
                accessor=accessor
            )

        return result

    def find(
            self,
            ids=None, descs=None, created=None, updated=None, accessors=None,
            **kwargs
    ):
        """Get a list of datum matching with input parameters.

        :param list ids: data ids to retrieve. If None, get all
            datum.
        :param list descs: list of regex to find in data description.
        :param datetime created: starting creation time.
        :param datetime updated: starting updated time.
        :param dict kwargs: additional elemnt properties to select.
        :param list accessors: accessor names to use.
        :return: list of Elements.
        :rtype: list
        """

        result = []

        if accessors:
            accessors = ensureiterable(accessors, exclude=str)

        else:
            accessors = self._accessors.keys()

        # init kwargs
        if ids:
            kwargs['ids'] = ids
        if descs:
            kwargs['descs'] = ids
        if created:
            kwargs['created'] = created
        if updated:
            kwargs['updated'] = updated

        for accessor in accessors:
            accessor = self.accessors[accessor]

            elts = accessor.find(**kwargs)
            result += elts

        return result

    def create(self, accessor, **kwargs):
        """Create a Data related to dataname.

        :param str accessor: accessor name.
        :type accessor: str or Accessor.
        :param dict kwargs:
        """

        return self._processdata(accessor=accessor, process='create', **kwargs)

    def sdata2data(self, accessor, sdata):
        """Create a data from a stored data.

        :param dict sdata: data in the store data format.
        :return: Data conversion from a store data.
        :rtype: Data
        """

        return self._processdata(
            accessor=accessor, process='sdata2data', sdata=sdata
        )

    def add(self, data, accessor=None, notify=True):
        """Add input data.

        :param Data data: data to add.
        :param str accessor: accessor name to use. By default, find the best
            accessor able to process data.
        :param bool notify: if True (default), notify observers.
        :return: added data.
        :raises: Store.Error if data already exists or information are
            missing.
        """

        return self._processdata(
            data=data, notify=notify, process='add', accessor=accessor
        )

    def update(self, data, accessor=None, old=None, notify=True):
        """Update input data.

        :param Data data: data to update.
        :param Data old: old data value.
        :param bool notify: if True (default), notify observers.
        :param str accessor: accessor name to use. By default, find the best
            accessor able to process data.
        :return: updated data.
        :rtype: Data
        :raises: Store.Error if not upsert and data does not exist or
            critical information are not similars.
        """

        return self._processdata(
            data=data, old=old, notify=notify, process='update',
            accessor=accessor
        )

    def remove(self, data, notify=True, accessor=None):
        """Remove input data.

        :param Data data: data to delete.
        :param bool notify: if True (default), notify observers.
        :param str accessor: accessor name to use. By default, find the best
            accessor able to process data.
        :return: deleted data.
        :rtype: Data
        :raises: Store.Error if data does not exist.
        """

        return self._processdata(
            data=data, notify=notify, process='remove', accessor=accessor
        )
