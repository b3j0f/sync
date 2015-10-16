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
    name='STORE',
    content=[
        Parameter('accessors', parser=Parameter.array),
        Parameter('autoconnect', parser=Parameter.bool)
    ]
)
class Store(Configurable):
    """Abstract class in charge of accessing to datum.

    A Store uses Accessors in order to access to data by types.
    """

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
        :param list accessors: Data accessors.
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

        :rtype: list
        """

        return tuple(self._accessors.values())

    @accessors.setter
    def accessors(self, value):
        """Change of accessors.

        :param list value: values of accessors. Each Value can be str or
            Accessor classe or even Accessor instance. In first two cases,
            final accessor values will tried to be resolved and instantiated
            with this such as the ``store`` paramater.
        :type value: str(s), type(s) or Accessor(s)
        :raises: Store.Error if value is not a dict.
        """

        self._accessors.clear()

        if value is not None:

            for index, accessor in enumerate(value):

                if isinstance(accessor, basestring):
                    accessor = lookup(accessor)

                if isclass(accessor):
                    accessor = accessor(store=self)

                if isinstance(accessor, Accessor):
                    # save accessor by datatype
                    self._accessors[accessor.__datatype__] = accessor

                else:
                    wrong_values = 'Wrong accessor value at {0} in {1}'
                    expected = 'str, Accessor class or instance expected'
                    error_msg = '{0}. {1}.'.format(wrong_values, expected)

                    raise Accessor.Error(error_msg.format(index, value))

    def addobserver(self, observer, event=Accessor.ALL, datatype=None):
        """Add an observer related to input event.

        :param observer: observer to add.
        :param int event: listening observer event. Default is ALL.
        :param type datatype: related datatype. sub class of Data.
        """

        def _addobserver(flag):
            """Local function which add observer by event flag."""
            if event & flag:
                observersperdatatype = self.observers.setdefault(flag, {})
                observers = observersperdatatype.setdefault(datatype, set())
                observers.add(observer)

        _addobserver(flag=Accessor.ADD)  # add for ADD events
        _addobserver(flag=Accessor.UPDATE)  # add for UPDATE events
        _addobserver(flag=Accessor.REMOVE)  # add for REMOVE events

    def removeobserver(self, observer, event=Accessor.ALL, datatype=None):
        """Remove an observer related to input event.

        :param observer: observer to remove.
        :param int event: stop listening observer event.
        :param type datatype: related datatype. sub class of Data.
        """

        def _removeobserver(flag):
            """Local function which remove an observer by a global event."""

            if event & flag:  # if flag matches
                observersperdatatype = self.observers.get(flag)

                if observersperdatatype:

                    if datatype is None:
                        datatypes = list(observersperdatatype.keys())

                    else:
                        datatypes = [datatype]

                    for _datatype in datatypes:
                        observers = observersperdatatype[_datatype]
                        observers.remove(observer)
                        if not observers:
                            del observersperdatatype[_datatype]

                        if not observersperdatatype:
                            del self.observers[flag]

        _removeobserver(flag=Accessor.ADD)  # remove for ADD events
        _removeobserver(flag=Accessor.UPDATE)  # remove for UPDATE events
        _removeobserver(flag=Accessor.REMOVE)  # remove for REMOVE events

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
        """Notify all observers about data creation/modification/deletion.

        :param Data data: accessed data to notify.
        :param int event: event id notification.
        """

        datatype = type(data)

        observersperdatatype = self.observers.get(event)

        observers = observersperdatatype.get(datatype, [])  # get observers

        if None in observersperdatatype:
            observers += observersperdatatype[None]

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

        otherdata = Store._otherdata(other=other)

        if otherdata:
            result = True
            for data in otherdata:
                if not self.getbyname(name=data.name, pnames=data.pnames):
                    result = False
                    break

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

    def _processdata(self, process, data=None, datatype=None, **kwargs):
        """Process input data with a specific accessor process function and
            event notification in case of success. The process successes if its
            result is an Data.

        The accessor corresponds to input datatype if data is None, or
        type(data) if data is given, or else the first accessor which gives

        :param Data data: data to process.
        :param process: accessor processing function. Takes in parameter
            input data and returns an data if processing succeed.
        :param datatype: related data type (fullname) to use.
        :param kwargs: additional processing parameters.
        :return: process data result.
        :rtype: Data
        :raises: Store.Error if a processing error occured.
        """

        result = None

        accessors = []  # accessors which will be processed in a best effort

        if data is None:
            if datatype is None:
                accessors = self._accessors.values()

            else:
                if isinstance(datatype, basestring):
                    datatype = lookup(datatype)

                if not issubclass(datatype, Data):
                    raise Store.Error('Wrong data type {0}.'.format(datatype))

                accessor = self._accessors.get(datatype)
                if accessor is not None:
                    accessors = [accessor]

        else:
            datatype = type(data)
            kwargs['data'] = data  # add data to kwargs if given
            accessors = [self._accessors.get(datatype)]

        if process == 'find':
            results = []

        if accessors:  # do processing only if an accessor is available
            for accessor in accessors:

                _process = getattr(accessor, process)

                try:
                    result = _process(**kwargs)

                    # embed error in store error if best effort
                except Accessor.Error as ex:
                    if process != 'find':
                        raise Store.Error(ex)

                else:
                    if result is not None:
                        if process == 'find':
                            results += result

                        else:
                            break

        if process == 'find':
            result = results

        return result

    def get(self, _id, datatype=None, pids=None, globalid=None):
        """Get data by id and type.

        :param int _id: data id.
        :param datatype: datatype to use. By default, return the first
            data where _id exists in any accessor.
        :type datatype: str or type.
        :param str pids: parent data ids if exist.
        :param str globalid: global id.
        :return: data which corresponds to input _id and _type.
        :rtype: Data
        """

        result = None

        if globalid is not None:
            _id, pids = getidwpids(globalid=globalid)

        result = self._processdata(
            process='get', _id=_id, pids=pids, datatype=datatype
        )

        return result

    def getbyname(self, name, pnames=None, globalname=None, datatype=None):
        """Get the first data corresponding with name and pnames or globalname.

        :param datatype: datatype to use. By default, return the first
            data where name and pnames exist in any accessor.
        :type datatype: str or type.
        :param str name: data name to retrieve.
        :param list pnames: list of parent data names.
        :param str globalname: data global name.
        :return: First Data which corresponds to input name and pnames.
        :rtype: Data
        """

        result = self._processdata(
            process='getbyname', name=name, pnames=pnames,
            globalname=globalname, datatype=datatype
        )

        return result

    def find(self, datatype=None, **kwargs):
        """Get a list of datum matching with input parameters.

        :param datatype: final data types to find.
        :type datatype: str or type
        :param dict kwargs: additional elemnt properties to select.
        :return: list of Elements.
        :rtype: list
        """

        result = []

        result = self._processdata(
            process='find', datatype=datatype, **kwargs
        )

        return result

    def create(self, datatype, **kwargs):
        """Create a Data related to dataname.

        :param datatype: datatype to retrieve.
        :type datatype: str or type.
        :param dict kwargs:
        """

        result = self._processdata(
            datatype=datatype, process='create', **kwargs
        )

        return result

    def sdata2data(self, datatype, sdata):
        """Create a data from a stored data.

        :param datatype: final datatype.
        :type datatype: str or type
        :param dict sdata: data in the store data format.
        :return: Data conversion from a store data.
        :rtype: Data
        """

        return self._processdata(
            datatype=datatype, process='sdata2data', sdata=sdata
        )

    def add(self, data, notify=True):
        """Add input data.

        :param Data data: data to add.
        :param bool notify: if True (default), notify observers.
        :return: added data.
        :raises: Store.Error if data already exists or information are
            missing.
        """

        return self._processdata(data=data, notify=notify, process='add')

    def update(self, data, old=None, notify=True):
        """Update input data.

        :param Data data: data to update.
        :param Data old: old data value. Must be of the same type of data.
        :param bool notify: if True (default), notify observers.
        :return: updated data.
        :rtype: Data
        :raises: Store.Error if not upsert and data does not exist or
            critical information are not similars.
        """

        return self._processdata(
            data=data, old=old, notify=notify, process='update'
        )

    def remove(self, data, notify=True):
        """Remove input data.

        :param Data data: data to delete.
        :param bool notify: if True (default), notify observers.
        :return: deleted data.
        :rtype: Data
        :raises: Store.Error if data does not exist.
        """

        return self._processdata(data=data, notify=notify, process='remove')
