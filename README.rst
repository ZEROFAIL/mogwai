mogwai
======

.. image:: https://badges.gitter.im/ZEROFAIL/mogwai.svg
   :alt: Join the chat at https://gitter.im/ZEROFAIL/mogwai
   :target: https://gitter.im/ZEROFAIL/mogwai?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

.. image:: https://travis-ci.org/ZEROFAIL/mogwai.svg?branch=tinkerpop3
    :target: https://travis-ci.org/ZEROFAIL/mogwai

.. image:: https://coveralls.io/repos/github/ZEROFAIL/mogwai/badge.svg?branch=tinkerpop3 
    :target: https://coveralls.io/github/ZEROFAIL/mogwai?branch=tinkerpop3



mogwai is an object-graph mapper (OGM) designed specifically for use with Tinkerpop3 graph databases.
Originally focused on TitanDB (0.5.x and below) (http://thinkaurelius.github.io/titan/) via RexPro (mogwai versions pre-1.x), the current
focus is now supporting TinkerPop3 based graph databases (ex. Titan 1.x)
Mogwai supports easily integrating Gremlin graph-traversals with vertex and edge models. For those
already familiar with Blueprints (https://github.com/tinkerpop/blueprints/wiki) there is is a
simple example.


Documentation
=============

mogwai documentation can be found at http://mogwai.readthedocs.org/

Installation
============

``$ pip install mogwai``

Testing
=======

To get mogwai unit tests running you'll need a tinkerpop graph installation gremlin server configured with a mogwai graph::

    <graph>
        <graph-name>mogwai</graph-name>
        <graph-type>com.thinkaurelius.titan.tinkerpop.rexster.TitanGraphConfiguration</graph-type>
        <graph-read-only>false</graph-read-only>
        <graph-location>/tmp/mogwai</graph-location>
        <properties>
              <storage.backend>local</storage.backend>
              <storage.directory>/tmp/mogwai</storage.directory>
              <buffer-size>100</buffer-size>
        </properties>

        <extensions>
          <allows>
            <allow>tp:gremlin</allow>
          </allows>
        </extensions>
    </graph>



Pull Requests
=============

General Tips for getting your pull request merged:
  - All Tests must pass
  - Coverage shouldn't decrease
  - Clean up spurious commits before submitting the PR via rebasing appropriately.
