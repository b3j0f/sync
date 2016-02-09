Description
===========

This library is dedicated to ease synchronization of data between resources (database, etc.) at a high level of abstraction.

.. image:: https://img.shields.io/pypi/l/b3j0f.sync.svg
   :target: https://pypi.python.org/pypi/b3j0f.sync/
   :alt: License

.. image:: https://img.shields.io/pypi/status/b3j0f.sync.svg
   :target: https://pypi.python.org/pypi/b3j0f.sync/
   :alt: Development Status

.. image:: https://img.shields.io/pypi/v/b3j0f.sync.svg
   :target: https://pypi.python.org/pypi/b3j0f.sync/
   :alt: Latest release

.. image:: https://img.shields.io/pypi/pyversions/b3j0f.sync.svg
   :target: https://pypi.python.org/pypi/b3j0f.sync/
   :alt: Supported Python versions

.. image:: https://img.shields.io/pypi/implementation/b3j0f.sync.svg
   :target: https://pypi.python.org/pypi/b3j0f.sync/
   :alt: Supported Python implementations

.. image:: https://img.shields.io/pypi/wheel/b3j0f.sync.svg
   :target: https://travis-ci.org/b3j0f/sync
   :alt: Download format

.. image:: https://travis-ci.org/b3j0f/sync.svg?branch=master
   :target: https://travis-ci.org/b3j0f/sync
   :alt: Build status

.. image:: https://coveralls.io/repos/b3j0f/sync/badge.png
   :target: https://coveralls.io/r/b3j0f/sync
   :alt: Code test coverage

.. image:: https://img.shields.io/pypi/dm/b3j0f.sync.svg
   :target: https://pypi.python.org/pypi/b3j0f.sync/
   :alt: Downloads

.. image:: https://readthedocs.org/projects/b3j0fsync/badge/?version=master
   :target: https://readthedocs.org/projects/b3j0fsync/?badge=master
   :alt: Documentation Status

.. image:: https://landscape.io/github/b3j0f/sync/master/landscape.svg?style=flat
   :target: https://landscape.io/github/b3j0f/sync/master
   :alt: Code Health

Links
=====

- `Homepage`_
- `PyPI`_
- `Documentation`_

Installation
============

pip install b3j0f.sync

Features
========

The global architecture is composed of four classes::

   - Record: pivot data to persist in heterogeneous stores. Keep a transparent reference to stores in order to ensure easy synchronization and consistency among stores.
   - Store: set of data with CRUD operations. CRUD operations are delegated to specific Accessors. To specialize to a database, CMDB, project management system, etc. depending on your needs.
   - Accessor: implementation of record CRUD operations in a store.
   - FieldDescriptor: specify record field type and default value.

If you want to ensure synchronization of data between three

If you want to use this library to your own needs, you have to extend abstract classes with implementation of 6 CRUD methods for the Accessor.

The system does not use semantical mechanisms, therefore, the system is in a **best effort** mode instead to be exhaustive.

Examples
--------

- `b3j0f.dmts`_: development management tool synchronizer.

Perspectives
============

- wait feedbacks during 6 months before passing it to a stable version.
- Cython implementation.

Donation
========

.. image:: https://cdn.rawgit.com/gratipay/gratipay-badge/2.3.0/dist/gratipay.png
   :target: https://gratipay.com/b3j0f/
   :alt: I'm grateful for gifts, but don't have a specific funding goal.

.. _Homepage: https://github.com/b3j0f/sync
.. _Documentation: http://b3j0fsync.readthedocs.org/en/master/
.. _PyPI: https://pypi.python.org/pypi/b3j0f.sync/
