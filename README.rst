====================
Synchronizing system
====================

This system is dedicated to help to synchronize data of resources.

The global architecture is composed of four classes:

- Synchronizer: class which is linked to several resources in order to propagate data CRUD operations on these lasts.
- Resource: class which represents a set of data, and uses one Accessor per data type in order to access to self data.
- Accessor: class which permits to access to resource data.
- Element: data content interface which is the an abstraction used to exchange data information among resources.
