Overseer
========

Collection of POX component for implementing Bandwidth/Latency-aware OpenFlow Controller

Requirements
------------

* NetworkX

Components
----------

* overseer - primary component, handle routing
* topology - handle network topology data structure creation and maintainace, powered by NetworkX

Usage
-----

Clone this repository into POX's ext directory and launch included sample launcher with the following command

    $ ./pox.py overseer.samples.overseer_launcher
