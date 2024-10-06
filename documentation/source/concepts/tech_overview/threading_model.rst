.. _curve _overview_threading:

Threading Model
===============

Curve builds on top of Envoy's single process with multiple threads curve itecture.

A single *primary* thread controls various sporadic coordination tasks while some number of *worker*
threads perform filtering, and forwarding.

Once a connection is accepted, the connection spends the rest of its lifetime bound to a single worker
thread. All the functionality around prompt handling from a downstream client is handled in a separate worker thread.
This allows the majority of Curve to be largely single threaded (embarrassingly parallel) with a small amount
of more complex code handling coordination between the worker threads.

Generally Curve is written to be 100% non-blocking.

.. tip::

   For most workloads we recommend configuring the number of worker threads to be equal to the number of
   hardware threads on the machine.
