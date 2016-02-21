from __future__ import unicode_literals
from nose.plugins.attrib import attr

from mogwai.connection import MogwaiQueryError
from mogwai.tests.base import BaseMogwaiTestCase
from mogwai.models import V, Edge, Vertex, GREATER_THAN
from mogwai.properties import Integer, Double


class MockVertex(object):
    eid = 1


class MockVertex2(Vertex):
    age = Integer()


class MockEdge(Edge):
    age = Integer()
    fierceness = Double()


@attr('unit', 'query_vertex')
class SimpleQueryTest(BaseMogwaiTestCase):
    def setUp(self):
        super(SimpleQueryTest, self).setUp()
        self.q = V(MockVertex())

    def test_has(self):
        result = self.q.has(MockEdge.get_property_by_name("age"), 10)
        self.assertEqual(result._get(), "has('mockedge_age', eq(b0))")
        self.assertEqual(result._bindings['b0'], 10)

    def test_has_double_casting(self):
        result = self.q.has(MockEdge.get_property_by_name("fierceness"), 3.3)
        self.assertEqual(result._get(), "has('mockedge_fierceness', eq(b0))")
        self.assertEqual(result._bindings['b0'], 3.3)

    def test_has_within(self):
        result = self.q.has(
            MockEdge.get_property_by_name("age"), (10, 11), compare="within")
        self.assertEqual(result._get(), "has('mockedge_age', within(*b0))")
        self.assertEqual(result._bindings['b0'], (10, 11))

    def test_has_label(self):
        result = self.q.has_label("label1", "label2")
        self.assertEqual(result._get(), "hasLabel(*b0)")
        self.assertEqual(result._bindings['b0'], ["label1", "label2"])

    def test_has_id(self):
        result = self.q.has_id("aaaa", "bbbb")
        self.assertEqual(result._get(), "hasId(*b0)")
        self.assertEqual(result._bindings['b0'], ("aaaa", "bbbb"))

    def test_has_key(self):
        result = self.q.has_key("name", "age")
        self.assertEqual(result._get(), "hasKey(*b0)")
        self.assertEqual(result._bindings['b0'], ("name", "age"))

    def test_has_value(self):
        result = self.q.has_value("dave", 25)
        self.assertEqual(result._get(), "hasValue(*b0)")
        self.assertEqual(result._bindings['b0'], ("dave", 25))

    def test_out(self):
        result = self.q.out("tweet", "user")
        self.assertEqual(result._get(), "out(*b0)")
        self.assertEqual(result._bindings['b0'], ["tweet", "user"])

    def test_in(self):
        result = self.q.in_step("tweet", "user")
        self.assertEqual(result._get(), "in(*b0)")
        self.assertEqual(result._bindings['b0'], ["tweet", "user"])

    def test_both(self):
        result = self.q.both("tweet", "user")
        self.assertEqual(result._get(), "both(*b0)")
        self.assertEqual(result._bindings['b0'], ["tweet", "user"])

    def test_out_e(self):
        result = self.q.out_e("tweets", "follows")
        self.assertEqual(result._get(), "outE(*b0)")
        self.assertEqual(result._bindings['b0'], ["tweets", "follows"])

    def test_in_e(self):
        result = self.q.in_e("tweets", "follows")
        self.assertEqual(result._get(), "inE(*b0)")
        self.assertEqual(result._bindings['b0'], ["tweets", "follows"])

    def test_both_e(self):
        result = self.q.both_e("tweets", "follows")
        self.assertEqual(result._get(), "bothE(*b0)")
        self.assertEqual(result._bindings['b0'], ["tweets", "follows"])

    def test_out_v(self):
        result = self.q.out_v()
        self.assertEqual(result._get(), "outV()")

    def test_in_v(self):
        result = self.q.in_v()
        self.assertEqual(result._get(), "inV()")

    def test_both_v(self):
        result = self.q.both_v()
        self.assertEqual(result._get(), "bothV()")

    def test_other_v(self):
        result = self.q.other_v()
        self.assertEqual(result._get(), "otherV()")
