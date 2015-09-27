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

"""Resource module in charge of storing data."""

from b3j0f.utils.version import basestring
from b3j0f.utils.path import lookup
from b3j0f.conf import Configurable, Parameter, add_category
from b3j0f.sync.elt import Element
from b3j0f.sync.access import Accessor

from inspect import isclass


class MetaResource(type):
    """Handle Resource instantiation with autoconnection."""

    def __call__(cls, *args, **kwargs):

        result = super(MetaResource, cls).__call__(*args, **kwargs)

        if result.autoconnect:  # connect the resource if autoconnect
            result.connect()

        return result


@add_category('RESOURCE', Parameter('accessors', parser=Parameter.dict))
class Resource(Configurable):
    """Abstract class in charge of reading development management project
    elements.

    First, you can connect to a dmt in a public way (without params), or in a
    private way with login, password, token or oauth token.
    """

    CATEGORY = 'RESOURCE'  #: resource category configuration name.

    ADD = 1  #: add item handler event id.
    UPDATE = 2  #: update item handler event id.
    REMOVE = 4  #: remove item handler event id.

    ALL = ADD | UPDATE | REMOVE  #: all event ids.

    class Error(Exception):
        """Handle resource errors."""

    def __init__(
            self, handlers=None, autoconnect=True, accessors=None,
            *args, **kwargs
    ):
        """
        :param list handlers: handlers which listen to element
            creation/modification/deletion.
        :param bool autoconnect: if True, connect this at the end of this
            execution.
        :param dict accessors: Element accessors by name.
        """

        super(Resource, self).__init__(*args, **kwargs)

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
            this such as the ``resource`` paramater.
        """

        for name in value:
            accessor = value[name]
            if isinstance(accessor, basestring):
                accessor = lookup(accessor)(resource=self)

            elif isclass(accessor):
                accessor = accessor(resource=self)

            if isinstance(accessor, Accessor):
                self._accessors[name] = accessor

            else:
                raise Accessor.Error(
                    'Wrong accessor value at {0} in {1}.'.format(
                        name, value
                    )
                )

    def connect(self):
        """Connect to the remote element with self attributes."""

        raise NotImplementedError()

    def notify(self, elt, event):
        """Notify all handlers about element creation/modification/deletion."""

        for handler in self.handlers:  # notify all handlers
            handler(elt=elt, event=event, resource=self)

    @staticmethod
    def _otherelts(other):
        """Return a set of elements from other.

        :param other: other elements.
        :type other: Resource or Element(s)
        :return: set of elements.
        :rtype: set
        """

        result = other

        if isinstance(other, Resource):
            result = other.findelts()

        elif isinstance(other, Element):
            result = (other, )

        result = set(result)

        return result

    def __contains__(self, other):
        """True if this contains input element(s).

        :param Element(s) other: element(s) which might exist in this.
        :return: True iif input element(s) exist in this resource.
        :rtype: bool
        """

        result = False

        elements = Resource._otherelts(other=other)

        selfelements = set(self.findelts())

        result = len(selfelements & elements) == min(
            len(selfelements), len(elements)
        )

        return result

    def __iter__(self):
        """Iterator on all this elements."""

        elements = self.findelts()

        result = iter(elements)

        return result

    def __and__(self, other):
        """Return a list of elements which are both in this and in input
        element(s).

        :param Element(s) other:
        :return: list of elements contained in this and in input elements.
        :rtype: list
        """

        elements = Resource._otherelts(other=other)

        selfelements = set(self.findelts())

        result = elements & selfelements

        return result

    def __iadd__(self, other):
        """Add an other element(s) and notify handlers."""

        elements = Resource._otherelts(other=other)

        for elt in elements:
            self.addelt(elt=elt)

    def __or__(self, other):
        """Return a list of elements which are in this resource or in input
        element(s).

        :param Element(s) other:
        :return: list of elements contained in this or in input elements.
        :rtype: list
        """

        elements = Resource._otherelts(other)

        selfelements = set(self.findelts())

        result = elements | selfelements

        return result

    def __ior__(self, other):
        """Update element(s) and notify handlers.

        :param Element(s) other: element(s) to update.
        """

        elements = Resource._otherelts(other)

        for element in elements:
            self.updateelt(elt=element)

    def __sub__(self, other):
        """Return a list of elements which are in this resource and not in
        input element(s).

        :param Element(s) other:
        :return: list of elements contained in this and not in input elements.
        :rtype: list
        """

        elements = Resource._otherelts(other)

        selfelements = self.findelts()

        result = elements - selfelements

        return result

    def __isub__(self, other):
        """Delete elements and notify handlers."""

        elements = Resource._otherelts(other)

        for element in elements:
            self.remelt(elt=element)

    def __iand__(self, other):
        """Delete elements which are not in other elements, return the
        intersection  and notify handlers.

        :param Element(s) other: elements to keep.
        :return: kept elements.
        :rtype: list
        """

        elements = Resource._otherelts(other)

        selfelements = self.findelts()

        elementstoremove = [
            element for element in selfelements if element not in elements
        ]

        self -= elementstoremove

    def __setitem__(self, key, item):
        """Change of element and notify handlers.

        :param Element key: old element value.
        :param Element item: new element value.
        """

        self.updateelt(elt=item, old=key)

    def _getaccessor(self, elttype):
        """Get an accessor by element type.

        :param type elttype: Element type covered by the accessor.
        :return: related element type accessor.
        :rtype: Accessor
        :raises: Resource.Error if no related accessor exist.
        """

        result = None

        for accessor in self.accessors:
            if accessor.elttype == elttype:
                result = accessor
                break
        else:
            raise Resource.Error(
                'No accessor for {0} available'.format(elttype)
            )

        return result

    def _processelt(self, elt, processname, **kwargs):
        """Process input element with input accessor process function name and
            event notification in case of success. The process successes if its
            result is an Element.

        :param Element elt: element to process.
        :param processname: accessor processing function. Takes in parameter
            input element and returns an element if processing succeed.
        :param kwargs: additional processing parameters.
        :return: process element result.
        :rtype: Element
        :raises: Resource.Error if a processing error occured.
        """

        result = None

        try:
            accessor = self._getaccessor(elttype=type(elt))
            process = getattr(accessor, processname)
            result = process(elt=elt, **kwargs)

        except Accessor.Error as ex:  # embed error in resource error
            raise Resource.Error(ex)

        return result

    def getelt(self, _id, elttype, pids=None):
        """Get item by id and type.

        :param int _id: item id.
        :param type elttype: item type. Subclass of Element.
        :param str pids: parent element ids if exist.
        :return: element which corresponds to input _id and _type.
        :rtype: Element
        """

        return self._getaccessor(elttype=elttype).get(_id=_id, pids=pids)

    def findelts(
            self,
            names=None, descs=None, created=None, updated=None, elttypes=None,
            **kwargs
    ):
        """Get a list of elements matching with input parameters.

        :param list names: element names to retrieve. If None, get all
            elements.
        :param list descs: list of regex to find in element description.
        :param datetime created: starting creation time.
        :param datetime updated: starting updated time.
        :param dict kwargs: additional elemnt properties to select.
        :param type elttype: element classes to retrieve. Subclass of Element.
        :return: list of Elements.
        :rtype: list
        """

        result = []

        if not elttypes:
            elttypes = (
                accessor.elttype for accessor in self.accessors.values()
            )

        for elttype in elttypes:
            accessor = self._getaccessor(elttype=elttype)
            elts = accessor.find(
                names=names, descs=descs, created=created, updated=updated
            )
            result += elts

        return result

    def addelt(self, elt, notify=True):
        """Add input element.

        :param Element elt: element to add.
        :param bool notify: if True (default), notify handlers.
        :return: added element.
        :raises: Resource.Error if element already exists or information are
            missing.
        """

        return self._processelt(elt=elt, notify=notify, processname='add')

    def updateelt(self, elt, old=None, notify=True):
        """Update input element.

        :param Element elt: element to update.
        :param Element old: old element value.
        :param bool notify: if True (default), notify handlers.
        :return: updated element.
        :rtype: Element
        :raises: Resource.Error if not upsert and element does not exist or
            critical information are not similars.
        """

        return self._processelt(
            elt=elt, old=old, notify=notify, processname='udpate'
        )

    def remelt(self, elt, notify=True):
        """Remove input element.

        :param Element elt: element to delete.
        :param bool notify: if True (default), notify handlers.
        :return: deleted element.
        :rtype: Element
        :raises: Resource.Error if element does not exist.
        """

        return self._processelt(elt=elt, notify=notify, processname='delete')
