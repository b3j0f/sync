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

"""Accessor module."""

__all__ = ['getglobalid', 'getidwpids', 'Accessor']

separator_char = '::'  #: global id character separator.

from b3j0f.utils.version import basestring


def getglobalid(_id, pids=None):
    """Get the global id related to input _id and parent ids.

    Inverse of the getidwpids function.

    :param str _id: data id.
    :param list pids: parent data ids if data is embedded by other data.
    :return: final global data id. For example, if _id equals 'a' and pids
        equals ['bc, d'], the result is 'a::1::bc::3::c where 1 and 3
        corresponds to number of character ids (1 for 'a', 3 for 'a' and 'bc').
    :rtype: str
    """

    result = _id

    if pids is None:
        pids = []

    count = len(result)

    for index, pid in enumerate(pids):
        result = '{0}{1}{2}{1}{3}'.format(result, separator_char, count, pid)
        count = len(pid)

    return result


def _getcountvaluepid(count, currentid, lastid):
    """Get final count and value if pid is not a separation id.

    :param int count: number of character to check.
    :param str currentid: current read id.
    :param str lastid: last read id.
    :return: new count and currentid
    :rtype: tuple
    """

    count += len(separator_char)  # let's add separator_char len
    currentid = '{0}{1}{2}'.format(currentid, separator_char, lastid)

    return count, currentid


def _updatelocalidpids(localid, pids, currentid):
    """Update localid and pids with value.

    :return: localid.
    :rtype: str
    """

    if localid is None:  # set local id if None
        localid = currentid

    else:  # otherwise, add currentid to pids
        pids.append(currentid)

    return localid


def getidwpids(_id):
    """Get the local id with pids related to an id which can be composed of
    parent ids.

    Inverse of the getglobalid function.

    :param str _id: global id from where get a local id.
    :return: local data id and an array with data parent ids.
    :rtype: tuple
    """

    ids = _id.split(separator_char)  # split with separation char

    # result is localid and pids
    localid = None
    pids = []

    value = ids[0]  # current read id.
    count = 0  # count to check with separation character
    index = 1

    len_ids = len(ids)

    while index < len_ids:
        count += len(ids[index - 1])  # add number of read characters to count
        currentid = ids[index]  # read current id

        try:
            ipid = int(currentid)  # check if separation is founded

        except ValueError:
            count, value = _getcountvaluepid(count, value, currentid)

        else:  # elif separator is founded
            if ipid == count:
                localid = _updatelocalidpids(
                    localid=localid, pids=pids, currentid=value
                )
                count = 0
                index += 1
                value = ids[index] if index < len_ids else ''

            else:
                count, value = _getcountvaluepid(count, value, currentid)

        index += 1

    else:
        if value:
            localid = _updatelocalidpids(
                localid=localid, pids=pids, currentid=value
            )

    return localid, pids


class Accessor(object):
    """Data accessor.

    Provides method to access to store datum which are type of the static
    __datatype__ class.
    """

    __datatype__ = None  #: static handled data type

    ADD = 1  #: add event value.
    UPDATE = 2  #: update event value.
    REMOVE = 4  #: remove event value.

    ALL = ADD | UPDATE | REMOVE  #: all event value.

    class Error(Exception):
        """Handle Accessor error."""

    def __init__(self, store):

        super(Accessor, self).__init__()

        self.store = store

    def __getitem__(self, key):

        if not isinstance(key, basestring):
            key = key._id

        _id, pids = getidwpids(key)

        result = self.get(_id=_id, pids=pids)

        if result is None:
            raise KeyError(key)

        return result

    def __setitem__(self, key, value):

        old = key

        if isinstance(old, basestring):
            _id, pids = getidwpids(old)
            old = self.get(_id=_id, pids=pids)

        self.update(data=value, old=old)

    def __delitem__(self, key):

        data = key

        if isinstance(data, basestring):
            _id, pids = getidwpids(data)
            data = self.get(_id=_id, pids=pids)

        self.remove(data=data)

    def __iter__(self):

        return iter(self.find())

    def __iadd__(self, other):

        self.add(data=other)

    def __ior__(self, other):

        self.update(data=other)

    def __isub__(self, other):

        self.remove(data=other)

    def __contains__(self, other):

        _id, pids = getidwpids(other._id)

        return self.get(_id=_id, pids=pids)

    def get(self, _id, pids=None, globalid=None):
        """Get a data from _id, parent ids or globalid.

        :param str _id: data id to retrieve.
        :param list pids: list of parent data ids.
        :param str globalid: data global id.
        :return: Data which corresponds to input _id and pids.
        :rtype: Data
        """

        raise NotImplementedError()

    def getbyname(self, name, pnames=None, globalname=None):
        """Get the first data corresponding with name and pnames or globalname.

        :param str name: data name to retrieve.
        :param list pnames: list of parent data names.
        :param str globalname: data global name.
        :return: First Data which corresponds to input name and pnames.
        :rtype: Data
        """

        raise NotImplementedError()

    def find(
            self, name=None, ids=None, descs=None, created=None, updated=None,
            **kwargs
    ):
        """Find datum which match input parameters.

        :param str name: data name to find.
        :param list ids: data names to retrieve.
        :param list descs: list of regex to find in data description.
        :param datetime created: minimum data creation date time.
        :param datetime updated: minimum data updating date time.
        :param dict kwargs: additional search parameters.
        :return: datum which corresponds to input parameters.
        :rtype: list
        """

        raise NotImplementedError()

    def _process(self, data, process, notify, event, **kwargs):
        """Process input process data CUD method and notify in case of
        success.

        :param Data data: data to process.
        :param process: function to call with data and kwargs such as
            parameters.
        :param bool notify: processing notification.
        :param dict kwargs: processing additional parameters.
        :return: processing result.
        :rtype: Data
        :raises: Accessor.Error if process failed.
        """
        result = None

        try:
            result = process(data=data, **kwargs)
        except Accessor.Error:
            pass
        else:
            if notify:
                self.store.notify(data=data, event=event)

        return result

    def create(self, **kwargs):
        """Create a data with input kwargs such as data attributes.

        :return: data of type self datatype.
        :rtype: Data
        """

        result = self.__datatype__(accessor=self, **kwargs)

        return result

    def add(self, data, notify=True):
        """Add a data from this store.

        :param Data data: data to add.
        :param bool notify: if True (default) notify the store if data is
            added.
        :raises: Accessor.Error if data already exists.
        """

        return self._process(
            data=data, process=self._add, notify=notify, event=Accessor.ADD
        )

    def _add(self, data):
        """Method to override in order to specialize data creation.

        :param Data data: data to add to this store.
        :return addd data.
        :rtype: Data
        """

        raise NotImplementedError()

    def update(self, data, old=None, notify=True):
        """Update a data from this store.

        :param Data data: data to update.
        :param Data old: old data value.
        :param bool notify: if True (default) notify the store if data is
            updated.
        :return: updated data.
        :rtype: Data
        :raises: Accessor.Error if data does not exist or is not updatable.
        """

        if data.accessor != self:  # resolve local data id and pids
            data = self.getbyname(name=data.name, pnames=data.pnames)

        return self._process(
            data=data, process=self._update, notify=notify, old=old,
            event=Accessor.UPDATE
        )

    def _update(self, data, old):
        """Method to override in order to specialize data updating.

        :param Data data: data to update from this store.
        :param Data old: old data value.
        :return: updated data.
        :rtype: Data
        :raises: Accessor.Error if data does not exist or is not updatable.
        """

        raise NotImplementedError()

    def remove(self, data, notify=True):
        """Remove input data form this store.

        :param Data data: data to remove.
        :param bool notify: if True (default) notify the notify if data is
            removed.
        :return: removed data.
        :rtype: Data
        :raises: Accessor.Error if data does not exist or is not deletable.
        """

        if data.accessor != self:  # resolve local data id and pids
            data = self.getbyname(name=data.name, pnames=data.pnames)

        self._process(
            data=data, process=self._remove, notify=notify,
            event=Accessor.REMOVE
        )

    def _remove(self, data):
        """Method to override in order to specialize data removing.

        :param Data data: data to remove from this store.
        :return: removed data.
        :rtype: Data
        :raises: Accessor.Error if data does not exist or is not deletable.
        """

        raise NotImplementedError()
