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

separator_char = '::'  #: global id character separator.


def getglobalid(_id, pids=None):
    """Get the global id related to input _id and parent ids.

    Inverse of the getlocalid function.

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

    for index, pid in enumerate(pids):
        result = '{0}{1}{2}{1}{3}'.format(
            result, separator_char, len(result) - 4 * index, pid
        )

    return result


def _getcountvaluepid(count, currentid, lastid):
    """Get final count and value if pid is not a separation id.

    :param int count: number of character to check.
    :param str currentid: current read id.
    :param str lastid: last read id.
    :return: new count and currentid
    :rtype: tuple
    """

    count += count
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

    for index in range(1, len(ids)):  # path ids
        count += len(ids[index - 1])  # add number of read characters to count
        currentid = ids[index]  # read current id

        try:
            ipid = int(currentid)  # check if separation is founded

        except ValueError:
            count, value = _getcountvaluepid(count, value, currentid)

        else:  # elif separator is founded
            if ipid == count:
                _updatelocalidpids(localid=localid, pids=pids, currentid=value)
                value = ''

            else:
                count, value = _getcountvaluepid(count, value, currentid)

    else:
        if value:
            _updatelocalidpids(localid=localid, pids=pids, currentid=value)

    return localid, pids


class Accessor(object):
    """Data accessor.

    Provides method to access to resource datum.
    """

    ADD = 1  #: add event value.
    UPDATE = 2  #: update event value.
    REMOVE = 4  #: remove event value.

    ALL = ADD + UPDATE + REMOVE

    class Error(Exception):
        """Handle Accessor error."""

    def __init__(self, resource, datatype):

        super(Accessor, self).__init__()

        self.resource = resource
        self.datatype = datatype

    def __getitem__(self, key):

        _id, pids = getidwpids(key)

        result = self.get(_id=_id, pids=pids)

        if result is None:
            raise KeyError(key)

        return result

    def __setitem__(self, key, value):

        self.update(data=value, old=key)

    def __delitem__(self, key):

        self.remove(data=key)

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

        return self.get(_id=_id, pids=pids) is not None

    def get(self, _id, pids=None):
        """Get a data from _id and parent ids.

        :param str _id: data id to retrieve.
        :param list pids: list of parent data ids.
        :return: Data which corresponds to input _id and pids.
        :rtype: Data
        """

        raise NotImplementedError()

    def find(self, ids=None, desc=None, created=None, updated=None, **kwargs):
        """Find datum which match input parameters.

        :param list ids: data names to retrieve.
        :param str desc: data description entries.
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
                self.resource.notify(data=data, event=event)

        return result

    def create(self, **kwargs):
        """Create a data with input kwargs such as data attributes.

        :return: data of type self datatype.
        :rtype: Data
        """

        result = self.datatype(accessor=self, **kwargs)

        return result

    def add(self, data, notify=True):
        """Add a data from this resource.

        :param Data data: data to add.
        :param bool notify: if True (default) notify the resource if data is
            addd.
        :raises: Accessor.Error if data already exists.
        """

        return self._process(
            data=data, process=self._add, notify=notify, event=Accessor.ADD
        )

    def _add(self, data):
        """Method to override in order to specialize data creation.

        :param Data data: data to add to this resource.
        :return addd data.
        :rtype: Data
        """

        raise NotImplementedError()

    def update(self, data, old=None, notify=True):
        """Update a data from this resource.

        :param Data data: data to update.
        :param Data old: old data value.
        :param bool notify: if True (default) notify the resource if data is
            updated.
        :return: updated data.
        :rtype: Data
        :raises: Accessor.Error if data does not exist or is not updatable.
        """

        return self._process(
            data=data, process=self._update, notify=notify, old=old,
            event=Accessor.UPDATE
        )

    def _update(self, data, old):
        """Method to override in order to specialize data updating.

        :param Data data: data to update from this resource.
        :param Data old: old data value.
        :return: updated data.
        :rtype: Data
        :raises: Accessor.Error if data does not exist or is not updatable.
        """

        raise NotImplementedError()

    def remove(self, data, notify=True):
        """Remove input data form this resource.

        :param Data data: data to remove.
        :param bool notify: if True (default) notify the resource if data is
            removed.
        :return: removed data.
        :rtype: Data
        :raises: Accessor.Error if data does not exist or is not deletable.
        """

        self._process(
            data=data, process=self._remove, notify=notify,
            event=Accessor.REMOVE
        )

    def _remove(self, data):
        """Method to override in order to specialize data removing.

        :param Data data: data to remove from this resource.
        :return: removed data.
        :rtype: Data
        :raises: Accessor.Error if data does not exist or is not deletable.
        """

        raise NotImplementedError()
