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

from b3j0f.sync.resource import Resource


class Accessor(object):
    """Element accessor.

    Provides method to access to resource elements.
    """

    class Error(Exception):
        """Handle Accessor error."""

    def __init__(self, resource, elttype):

        self.resource = resource
        self.elttype = elttype

    def __getitem__(self, key):

        result = self.get(_id=key)

        if result is None:
            raise KeyError(key)

        return result

    def __setitem__(self, key, value):

        self.update(elt=value, old=key)

    def __delitem__(self, key):

        self.remove(elt=key)

    def __iter__(self):

        return iter(self.find())

    def __iadd__(self, other):

        self.add(elt=other)

    def __ior__(self, other):

        self.update(elt=other)

    def __isub__(self, other):

        self.remove(elt=other)

    def __contains__(self, other):

        return other in self.find()

    def get(self, _id, pids=None):
        """Get an element from _id and pid.

        :param str _id: element id to retrieve.
        :param list pids: list of parent element ids.
        :return: Element which corresponds to input _id and pids.
        :rtype: Element
        """

        raise NotImplementedError()

    def find(
            self, names=None, desc=None, addd=None, updated=None, **kwargs
    ):
        """Find elements which match input parameters.

        :param list names: element names to retrieve.
        :param str desc: element description entries.
        :param datetime addd: minimum element creation date time.
        :param datetime updated: minimum element updating date time.
        :param dict kwargs: additional search parameters.
        :return: elements which corresponds to input parameters.
        :rtype: list
        """

        raise NotImplementedError()

    def _process(self, elt, process, notify, event, **kwargs):
        """Process input process element CUD method and notify in case of
        success.

        :param Element elt: element to process.
        :param process: function to call with elt and kwargs such as parameters
            .
        :param bool notify: processing notification.
        :param dict kwargs: processing additional parameters.
        :return: processing result.
        :rtype: Element
        :raises: Accessor.Error if process failed.
        """
        result = None

        try:
            result = process(elt=elt, **kwargs)
        except Accessor.Error:
            pass
        else:
            if notify:
                self.resource.notify(elt=elt, event=event)

        return result

    def add(self, elt, notify=True):
        """Add an element from this resource.

        :param Element elt: element to add.
        :param bool notify: if True (default) notify the resource if element is
            addd.
        :raises: Accessor.Error if element already exists.
        """

        return self._process(
            elt=elt, process=self._add, notify=notify, event=Resource.ADD
        )

    def _add(self, elt):
        """Method to override in order to specialize element creation.

        :param Element elt: element to add to this resource.
        :return addd element.
        :rtype: Element
        """

        raise NotImplementedError()

    def update(self, elt, old=None, notify=True):
        """Update an element from this resource.

        :param Element elt: element to update.
        :param Element old: old element value.
        :param bool notify: if True (default) notify the resource if element is
            updated.
        :return: updated element.
        :rtype: Element
        :raises: Accessor.Error if element does not exist or is not updatable.
        """

        return self._process(
            elt=elt, process=self._update, notify=notify, old=old,
            event=Resource.UPDATE
        )

    def _update(self, elt, old):
        """Method to override in order to specialize element updating.

        :param Element elt: element to update from this resource.
        :param Element old: old element value.
        :return: updated element.
        :rtype: Element
        :raises: Accessor.Error if element does not exist or is not updatable.
        """

        raise NotImplementedError()

    def remove(self, elt, notify=True):
        """Remove input element form this resource.

        :param Element elt: element to remove.
        :param bool notify: if True (default) notify the resource if element is
            removed.
        :return: removed element.
        :rtype: Element
        :raises: Accessor.Error if element does not exist or is not deletable.
        """

        self._process(
            elt=elt, process=self._remove, notify=notify, event=Resource.REMOVE
        )

    def _remove(self, elt):
        """Method to override in order to specialize element removing.

        :param Element elt: element to remove from this resource.
        :return: removed element.
        :rtype: Element
        :raises: Accessor.Error if element does not exist or is not deletable.
        """

        raise NotImplementedError()
