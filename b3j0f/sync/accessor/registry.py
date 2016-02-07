# -*- coding: utf-8 -*-

# --------------------------------------------------------------------
# The MIT License (MIT)
#
# Copyright (c) 2015 Jonathan Labéjof <jonathan.labejof@gmail.com>
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

"""b3j0f.sync package."""

__all__ = ['AccessorRegistry']

from .core import Accessor
from ..record import Record


class AccessorRegistry(dict):
    """In charge of register accessors."""

    def __init__(self, accessors, *args, **kwargs):

        super(AccessorRegistry, self).__init__(*args, **kwargs)

        self += accessors

    def register(self, accessor):
        """Register input accessor.

        :param Accessor accessor: accessor to register.
        """

        for rtype in accessor.__rtypes__:
            self[rtype] = accessor

    def unregister(self, accessor=None, rtype=None):
        """Unregister accessor or rtype.

        :param Accessor accessor: accessor to unregister.
        :param type rtype: record type to unregister.
        """

        if rtype is not None:
            del self[rtype]

        if accessor is not None:
            for rtype in accessor.__rtypes__:
                if rtype in self:
                    del self[rtype]

    def get(self, key, default=None):
        """Get the accessor able to process input record (type).

        :param key: record type.
        :type key: type or Record"""

        if isinstance(key, Record):
            key = key.__class__

        return super(AccessorRegistry, self).get(key, default)

    def __iadd__(self, other):
        """Register accessor(s).

        :param Accessor(s) other: accessors to register."""

        if isinstance(other, Accessor):
            other = [other]

        for accessor in other:
            self.register(accessor=accessor)

    def __isub__(self, other):
        """Unregister accessor(s).

        :param Accessor(s) other: accessors to unregister."""

        if isinstance(other, Accessor):
            other = [other]

        for accessor in other:
            self.unregister(accessor=accessor)
