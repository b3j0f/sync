ChangeLog
=========

0.0.3 (2015/10/03)
------------------

- clean code and refactor most complex parts.
- rename store.handlers to store.observers and improve their management with event filtering. Data filtering will be implemented in the future version.
- add limitation about data names.

0.0.2 (2015/10/02)
------------------

- add save/delete/rollback methods to the Data class.
- add the method sdata2data in store and access modules in order to create a Data from a store data. Could be very useful in webhooks.
