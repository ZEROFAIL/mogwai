from __future__ import unicode_literals
import logging

from tornado.concurrent import Future

from mogwai._compat import float_types, print_
from mogwai import connection
from mogwai.exceptions import MogwaiQueryError
from .element import Element
from mogwai.constants import (EQUAL, NOT_EQUAL, GREATER_THAN,
                              GREATER_THAN_EQUAL, LESS_THAN,
                              LESS_THAN_EQUAL, WITHIN, INSIDE,
                              OUTSIDE, BETWEEN)
import copy
from mogwai.properties.base import GraphProperty

logger = logging.getLogger(__name__)


class V(object):
    """
    All query operations return a new query object, which currently deviates from blueprints.
    The blueprints query object modifies and returns the same object
    This method seems more flexible, and consistent w/ the rest of Gremlin.
    """
    _limit = None

    def __init__(self, vertex):
        self._vertex = vertex
        self._steps = []
        self._bindings = {}

    def count(self, *args, **kwargs):
        """
        :returns: number of matching vertices
        :rtype: int
        """
        pass

    def has(self, key, value, compare=EQUAL):
        """
        :param key: key to lookup
        :type key: str | mogwai.properties.GraphProperty
        :param value: value to compare
        :type value: str, float, int
        :param compare: comparison keyword
        :type compare: str
        :rtype: Query
        """
        q = copy.copy(self)
        if issubclass(type(key), property):
            logger.error("Use %s.get_property_by_name instead, this won't work" % self.__class__.__name__)
            raise MogwaiQueryError("Use %s.get_property_by_name instead, this won't work" % self.__class__.__name__)
        binding = self._get_binding(value)
        if compare in [INSIDE, OUTSIDE, BETWEEN, WITHIN]:
            step = "has('{}', {}(*{}))".format(key, compare, binding)
        else:
            step = "has('{}', {}({}))".format(key, compare, binding)
        q._steps.append(step)
        return q

    def has_label(self, *labels):
        labels = self._get_labels(labels)
        return self._unpack_step("hasLabel", labels)

    def has_id(self, *ids):
        return self._unpack_step("hasId", ids)

    # def has_key(self, *keys):
    #     return self._unpack_step("hasKey", keys)

    # def has_value(self, *values):
    #     return self._unpack_step("hasValue", values)

    def out(self, *labels):
        labels = self._get_labels(labels)
        return self._unpack_step("out", labels)

    def in_step(self, *labels):
        labels = self._get_labels(labels)
        return self._unpack_step("in", labels)

    def both(self, *labels):
        labels = self._get_labels(labels)
        return self._unpack_step("both", labels)

    def out_e(self, *labels):
        labels = self._get_labels(labels)
        return self._unpack_step("outE", labels)

    def in_e(self, *labels):
        labels = self._get_labels(labels)
        return self._unpack_step("inE", labels)

    def both_e(self, *labels):
        labels = self._get_labels(labels)
        return self._unpack_step("bothE", labels)

    def out_v(self):
        return self._simple_step("outV")

    def in_v(self):
        return self._simple_step("inV")

    def both_v(self):
        return self._simple_step("bothV")

    def other_v(self):
        return self._simple_step("otherV")

    def _get_labels(self, labels):
        new_labels = []
        for label in labels:
            try:
                label = label.get_label()
                new_labels.append(label)
            except:
                new_labels.append(label)
        return new_labels

    def _simple_step(self, func):
        q = copy.copy(self)
        step = '{}()'.format(func)
        q._steps.append(step)
        return q

    def _unpack_step(self, func, vals):
        q = copy.copy(self)
        binding = self._get_binding(vals)
        step = '{}(*{})'.format(func, binding)
        q._steps.append(step)
        return q

    def _get_binding(self, val):
        binding = 'b{}'.format(len(self._bindings))
        self._bindings[binding] = val
        return binding

    def limit(self, limit):
        pass

    def get(self, deserialize=True, *args, **kwargs):
        script = "g.V(vid).{}".format(self._get())
        self._bindings.update({"vid": self._vertex._id})

        def process_results(results):
            if not results:
                results = []
            if deserialize:
                results = [Element.deserialize(r) for r in results]
            return results

        future_results = connection.execute_query(
            script, params=self._bindings, handler=process_results, **kwargs)

        return future_results

    def _get(self):
        return '.'.join(self._steps)
