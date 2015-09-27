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

from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup
from b3j0f.utils.iterable import ensureiterable
from b3j0f.conf import ConfigurableRegistry, Parameter, add_category
from b3j0f.sync.resource import Resource
from b3j0f.sync.elt import Element


@add_category('SYNC', [Parameter('resources'), Parameter('tosync')])
class Synchronizer(ConfigurableRegistry):
    """In charge of synchronizing development management tools.

    The synchronization is done with a set of Resources and a set of SyncConf
    objects.

    Is is possible to specify which types of elements or which element property
    to synchronize thanks to the ``tosync`` attribute.
    If you want to specify an exclusive list of element types to synchronize,
    specify them in the list by name.
    """

    def __init__(self, resources, tosync):
        """
        :param DMT(s) resources: DMT(S) to synchronize.
        :param list tosync: element types to synchronize.
        """

        # init protected attributes
        self._resources = None
        self._tosync = None

        # set attributes
        self.resources = resources
        self.tosync = tosync

    @property
    def resources(self):
        """Get self resources.

        :return: list of resources.
        :rtype: list
        """

        return self._resources

    @resources.setter
    def resources(self, value):
        """Change of resources to use.

        :param list value: list of resources to use.
        """

        if self._resources is not None:

            for resource in self._resources:
                resource.removehandler(
                    handler=self._eltcudtrigger, event=Resource.ALL
                )

        self._resources = value

        for resource in value:
            resource.addhandler(
                handler=self._eltcudtrigger, event=Resource.ALL
            )

    @property
    def tosync(self):
        """Get self tosync array.

        :return: list of element type names, or dictionaries with keys
        """

        return self._tosync

    @tosync.setter
    def tosync(self, value):
        """Change of tosync value.
        """

        self._tosync = value

    def _eltcudtrigger(self, elt, resource, event, old=None):
        """Called when input element is created/updated/deleted from the input
        resource.

        :param Element elt: created/updated/deleted element.
        :param Resource resource: owner element.
        """

        for selfresource in self.resources:

            if resource.url != selfresource.url:

                if event & Resource.ADD:
                    try:
                        selfresource.addelt(elt=elt, notify=False)
                    except Resource.Error:
                        try:
                            selfresource.updateelt(
                                elt=elt, old=old, notify=False
                            )
                        except Resource.Error:
                            pass

                elif event & Resource.UPDATE:
                    try:
                        selfresource.updateelt(elt=elt, notify=False)
                    except Resource.Error:
                        try:
                            selfresource.addelt(elt=elt, notify=False)
                        except Resource.Error:
                            pass

                elif event & Resource.REMOVE:
                    try:
                        selfresource.remelt(elt=elt, notify=False)
                    except Resource.Error:
                        pass

    def notify(self):
        """Synchronize all resources."""

        for resource in self.resources:

            for otherresource in self.resources:

                if resource != otherresource:

                    try:
                        resource += otherresource  # add elements
                    except Resource.Error:
                        try:
                            resource |= otherresource  # update elements
                        except Resource.Error:
                            pass


class SyncConf(object):
    """Synchronization object which specifies element types and properties to
    notify.
    """

    class Error(Exception):
        """Handle SyncConf errors."""

    __slots__ = ('cls', 'props')

    def __init__(self, cls=Element, props=None):
        """
        :param cls: matching element class(es). Must be a sub class of Element.
            Otherwise, it must matches with the class name.
        :type cls: type or tuple
        :param list props: element props to notify. property (regex) name(s).
        """

        self.cls = cls
        self.props = () if props is None else ensureiterable(
            props, exclude=str
        )

    def match(self, elt):
        """True if this configuration matches with the input element.

        :param Element elt: elt to match configuration.
        :return: True iif this matches the element.
        :rtype: bool
        """

        result = isinstance(elt, self.cls)

        if result:
            for prop in self.props:
                result = hasattr(elt, prop)
                if not result:
                    break

        return result

    @staticmethod
    def parser(value):
        """SyncConf parser.

        :param str value: SyncConf value to parse.
        """

        result = None

        if value[0] in ('"', '{'):
            val = Parameter.json(value)

        else:
            val = Parameter.array(value)

        if isinstance(val, basestring):  # only class name is given
            cls = lookup(val)
            result = SyncConf(cls=cls)

        elif isinstance(val, dict):  # only one class name and props are given
            cls = lookup(val['cls'])
            props = val['props']
            result = SyncConf(cls=cls, props=props)

        else:
            raise SyncConf.Error(
                'Wrong type {0}. str or dict expected'.format(value)
            )

        return result
