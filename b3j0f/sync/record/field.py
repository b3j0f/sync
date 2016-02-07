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

"""Field definition module."""

__all__ = ['Field']


class Field(object):
    """Record field."""

    def __init__(
            self,
            ftype=object, default=None, description=None, identifier=False,
            *args, **kwargs
    ):
        """
        :param type ftype: field type. Default is object.
        :param default: default fieldd value.
        :param str description: field description.
        :param bool identifiers: boolean flag about identifier field. An
            identifier can be used to generate an index for example.
        """

        super(Field, self).__init__(*args, **kwargs)

        self.ftype = ftype
        self.default = None
        self.default = self.getvalue(default)
        self.description = description
        self.identifier = identifier

    def getvalue(self, value, name=None):
        """Get final value which corresponds to input value or default value if
        value is None.

        :param value: value to compare with this.
        :param str name: field name.
        :raises: TypeError if input value does not match this field type.
        """

        result = self.default if value is None else value

        if result is not None and not isinstance(result, self.ftype):
            raise TypeError(
                'Parameter {0}: {1} does not match {2}'.format(
                    name, value, self
                )
            )

        return result
