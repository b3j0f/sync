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

"""Element module."""

from random import randint


class Element(object):
    """Development management tool item."""

    class Error(Exception):
        """Handle element errors."""

    def __init__(
            self, name,
            _id=None, desc=None, created=None, updated=None
    ):
        """
        :param str name: item name.
        :param int id: item id. Generated in [1; 2^32-1] by default.
        :param int rid: resource id.
        :param str url: item url.
        :param str owner: item owner.
        :param str description: item description.
        :param datetime created: item date time creation.
        :param datetime updated: item date time updating.
        """

        super(Element, self).__init__()

        self._id = randint(1, 2**32-1) if _id is None else _id
        self.name = name
        self.desc = desc
        self.created = created
        self.updated = updated

    def __hash__(self):

        return self._id

    def __cmp__(self, other):

        return self._id.__cmp__(other)
