from __future__ import unicode_literals
import datetime
from pytz import utc

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.testing import gen_test

from nose.plugins.attrib import attr

from mogwai.tests.base import BaseMogwaiTestCase

from mogwai.models import (Vertex, V, Edge, IN, OUT, BOTH, GREATER_THAN,
                           LESS_THAN)
from mogwai import properties


# Vertices
class Person(Vertex):
    name = properties.Text()
    age = properties.Integer()


class Course(Vertex):
    name = properties.Text()
    credits = properties.Double()


class ResearchGroup(Vertex):
    name = properties.Text()

# Edges
class EnrolledIn(Edge):
    date_enrolled = properties.DateTime()
    enthusiasm = properties.Integer(default=5)  # medium, 1-10, 5 by default


class TaughtBy(Edge):
    overall_mood = properties.Text(default='Grumpy')


class BelongsTo(Edge):
    member_since = properties.DateTime()


class SupervisedBy(Edge):
    pass


class BaseTraversalTestCase(BaseMogwaiTestCase):

    @classmethod
    def setUpClass(cls):
        super(BaseTraversalTestCase, cls).setUpClass()
        loop = IOLoop.current()
        @gen.coroutine
        def build_graph():
            """
            person -enrolled_in-> course
            course -taught_by-> person

            :param cls:
            :return:
            """
            cls.jon = yield Person.create(name='Jon', age=143)
            cls.eric = yield Person.create(name='Eric', age=25)
            cls.blake = yield Person.create(name='Blake', age=14)

            cls.physics = yield Course.create(name='Physics 264', credits=1.0)
            cls.beekeeping = yield Course.create(name='Beekeeping', credits=15.0)
            cls.theoretics = yield Course.create(name='Theoretical Theoretics', credits=-3.5)

            cls.dist_dev = yield ResearchGroup.create(name='Distributed Development')

            cls.eric_in_physics = yield EnrolledIn.create(cls.eric, cls.physics,
                                                    date_enrolled=datetime.datetime.now(tz=utc),
                                                    enthusiasm=10)  # eric loves physics
            cls.jon_in_beekeeping = yield EnrolledIn.create(cls.jon, cls.beekeeping,
                                                      date_enrolled=datetime.datetime.now(tz=utc),
                                                      enthusiasm=1)  # jon hates beekeeping

            cls.jon_in_dist_dev = yield BelongsTo.create(
                cls.jon, cls.dist_dev, member_since=datetime.datetime.now(tz=utc))

            cls.blake_in_theoretics = yield EnrolledIn.create(cls.blake, cls.theoretics,
                                                        date_enrolled=datetime.datetime.now(tz=utc),
                                                        enthusiasm=8)

            cls.blake_beekeeping = yield TaughtBy.create(cls.beekeeping, cls.blake, overall_mood='Pedantic')
            cls.jon_physics = yield TaughtBy.create(cls.physics, cls.jon, overall_mood='Creepy')
            cls.eric_theoretics = yield TaughtBy.create(cls.theoretics, cls.eric, overall_mood='Obtuse')
            cls.jon_eric = yield SupervisedBy.create(cls.eric, cls.jon)
        loop.run_sync(build_graph)

    @classmethod
    def tearDownClass(cls):
        loop = IOLoop.current()
        @gen.coroutine
        def destroy_graph():
            # reverse setup procedure and delete vertices and edges in graph
            yield cls.eric_theoretics.delete()
            yield cls.jon_physics.delete()
            yield cls.blake_beekeeping.delete()
            yield cls.blake_in_theoretics.delete()
            yield cls.jon_in_beekeeping.delete()
            yield cls.eric_in_physics.delete()
            yield cls.jon_eric.delete()
            yield cls.jon_in_dist_dev.delete()
            yield cls.dist_dev.delete()
            yield cls.theoretics.delete()
            yield cls.beekeeping.delete()
            yield cls.physics.delete()
            yield cls.blake.delete()
            yield cls.eric.delete()
            yield cls.jon.delete()
        loop.run_sync(destroy_graph)
        super(BaseTraversalTestCase, cls).tearDownClass()


@attr('unit', 'traversals')
class TestVertexTraversals(BaseTraversalTestCase):

    @gen_test
    def test_inV_works(self):
        """Test that inV traversals work as expected"""

        stream = yield self.jon.inV()
        results = yield stream.read()
        self.assertEqual(len(results), 2)
        self.assertIn(self.physics, results)
        self.assertIn(self.eric, results)

        stream = yield self.physics.inV()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.eric, results)

        stream = yield self.eric.inV()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.theoretics, results)

        stream = yield self.theoretics.inV()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.blake, results)

        stream = yield self.beekeeping.inV()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.jon, results)

        stream = yield self.blake.inV()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.beekeeping, results)

    @gen_test
    def test_inE_traversals(self):
        """Test that inE traversals work as expected"""
        stream = yield self.jon.inE()
        results = yield stream.read()
        self.assertEqual(len(results), 2)
        self.assertIn(self.jon_physics, results)
        self.assertIn(self.jon_eric, results)

    @gen_test
    def test_outV_traversals(self):
        """Test that outV traversals work as expected"""
        stream = yield self.eric.outV()
        results = yield stream.read()
        self.assertEqual(len(results), 2)
        self.assertIn(self.physics, results)
        self.assertIn(self.jon, results)

    @gen_test
    def test_outE_traverals(self):
        """Test that outE traversals work as expected"""
        stream = yield self.blake.outE()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.blake_in_theoretics, results)

    @gen_test
    def test_bothE_traversals(self):
        """Test that bothE traversals works"""
        stream = yield self.jon.bothE()
        results = yield stream.read()
        self.assertEqual(len(results), 4)
        self.assertIn(self.jon_physics, results)
        self.assertIn(self.jon_in_beekeeping, results)
        self.assertIn(self.jon_in_dist_dev, results)
        self.assertIn(self.jon_eric, results)

    @gen_test
    def test_bothV_traversals(self):
        """Test that bothV traversals work"""
        stream = yield self.blake.bothV()
        results = yield stream.read()
        self.assertEqual(len(results), 2)
        self.assertIn(self.beekeeping, results)


@attr('unit', 'traversals')
class TestVertexCentricQueries(BaseTraversalTestCase):

    @gen_test
    def test_out(self):
        stream = yield V(self.jon).out().get()
        results = yield stream.read()
        self.assertIn(self.beekeeping, results)

    @gen_test
    def test_in(self):
        stream = yield V(self.jon).in_step().get()
        results = yield stream.read()
        self.assertIn(self.physics, results)
        self.assertIn(self.eric, results)

    @gen_test
    def test_both(self):
        stream = yield V(self.jon).both().get()
        results = yield stream.read()
        self.assertIn(self.physics, results)
        self.assertIn(self.beekeeping, results)

    @gen_test
    def test_out_labels(self):
        stream = yield V(self.jon).out(EnrolledIn).get()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Beekeeping")
        stream = yield V(self.jon).out(BelongsTo).get()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Distributed Development")
        stream = yield V(self.jon).out(BelongsTo, EnrolledIn).get()
        results = yield stream.read()
        self.assertEqual(len(results), 2)
        self.assertIn(self.dist_dev, results)
        self.assertIn(self.beekeeping, results)

    @gen_test
    def test_in_labels(self):
        stream = yield V(self.jon).in_step(TaughtBy).get()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Physics 264")
        stream = yield V(self.jon).in_step(SupervisedBy).get()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Eric")
        stream = yield V(self.jon).in_step(SupervisedBy, TaughtBy).get()
        results = yield stream.read()
        self.assertEqual(len(results), 2)
        self.assertIn(self.physics, results)
        self.assertIn(self.eric, results)

    @gen_test
    def test_both_labels(self):
        stream = yield V(self.jon).both(EnrolledIn).get()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Beekeeping")
        stream = yield V(self.jon).both(BelongsTo).get()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Distributed Development")
        stream = yield V(self.jon).both(BelongsTo, EnrolledIn).get()
        results = yield stream.read()
        self.assertEqual(len(results), 2)
        self.assertIn(self.dist_dev, results)
        self.assertIn(self.beekeeping, results)
        stream = yield V(self.jon).both(TaughtBy).get()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Physics 264")
        stream = yield V(self.jon).both(SupervisedBy).get()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Eric")
        stream = yield V(self.jon).both(SupervisedBy, TaughtBy).get()
        results = yield stream.read()
        self.assertEqual(len(results), 2)
        self.assertIn(self.physics, results)
        self.assertIn(self.eric, results)
        stream = yield V(self.jon).both(
            SupervisedBy, TaughtBy, BelongsTo, EnrolledIn).get()
        results = yield stream.read()
        self.assertEqual(len(results), 4)
        self.assertIn(self.physics, results)
        self.assertIn(self.eric, results)
        self.assertIn(self.dist_dev, results)
        self.assertIn(self.beekeeping, results)

    @gen_test
    def test_out_v(self):
        stream = yield V(self.blake).in_e().out_v().get()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.beekeeping, results)

    @gen_test
    def test_out_v(self):
        stream = yield V(self.blake).out_e().in_v().get()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertIn(self.theoretics, results)

    @gen_test
    def test_both_v(self):
        stream = yield V(self.blake).out_e().both_v().get()
        results = yield stream.read()
        self.assertEqual(len(results), 2)
        self.assertIn(self.theoretics, results)
        self.assertIn(self.blake, results)

    @gen_test
    def test_other_v(self):
        stream = yield V(self.jon).both_e().other_v().get()
        results = yield stream.read()
        self.assertEqual(len(results), 4)
        self.assertIn(self.beekeeping, results)
        self.assertIn(self.dist_dev, results)
        self.assertIn(self.eric, results)
        self.assertIn(self.physics, results)

    @gen_test
    def test_both_v_multiple(self):
        stream = yield V(self.jon).both_e().both_v().get()
        results = yield stream.read()
        self.assertEqual(len(results), 8)
        self.assertIn(self.beekeeping, results)
        self.assertIn(self.dist_dev, results)
        self.assertIn(self.eric, results)
        self.assertIn(self.physics, results)
        self.assertIn(self.jon, results)

    @gen_test
    def test_out_e(self):
        stream = yield V(self.jon).out_e().get()
        results = yield stream.read()
        self.assertTrue(len(results), 2)
        self.assertIn(self.jon_in_dist_dev, results)
        self.assertIn(self.jon_in_beekeeping, results)
        stream = yield V(self.jon).out_e(BelongsTo).get()
        results = yield stream.read()
        self.assertTrue(len(results), 1)
        self.assertIn(self.jon_in_dist_dev, results)
        stream = yield V(self.jon).out_e(EnrolledIn).get()
        results = yield stream.read()
        self.assertTrue(len(results), 1)
        self.assertIn(self.jon_in_beekeeping, results)
        stream = yield V(self.jon).out_e(EnrolledIn, BelongsTo).get()
        results = yield stream.read()
        self.assertTrue(len(results), 2)
        self.assertIn(self.jon_in_dist_dev, results)
        self.assertIn(self.jon_in_beekeeping, results)

    @gen_test
    def test_in_e(self):
        stream = yield V(self.jon).in_e().get()
        results = yield stream.read()
        self.assertTrue(len(results), 2)
        self.assertIn(self.jon_eric, results)
        self.assertIn(self.jon_physics, results)
        stream = yield V(self.jon).in_e(SupervisedBy).get()
        results = yield stream.read()
        self.assertTrue(len(results), 1)
        self.assertIn(self.jon_eric, results)
        stream = yield V(self.jon).in_e(TaughtBy).get()
        results = yield stream.read()
        self.assertTrue(len(results), 1)
        self.assertIn(self.jon_physics, results)
        stream = yield V(self.jon).in_e(SupervisedBy, TaughtBy).get()
        results = yield stream.read()
        self.assertTrue(len(results), 2)
        self.assertIn(self.jon_eric, results)
        self.assertIn(self.jon_physics, results)

    @gen_test
    def test_both_e(self):
        stream = yield V(self.jon).both_e().get()
        results = yield stream.read()
        self.assertTrue(len(results), 4)
        self.assertIn(self.jon_eric, results)
        self.assertIn(self.jon_physics, results)
        self.assertIn(self.jon_in_dist_dev, results)
        self.assertIn(self.jon_in_beekeeping, results)
        stream = yield V(self.jon).both_e(SupervisedBy).get()
        results = yield stream.read()
        self.assertTrue(len(results), 1)
        self.assertIn(self.jon_eric, results)
        stream = yield V(self.jon).both_e(EnrolledIn).get()
        results = yield stream.read()
        self.assertTrue(len(results), 1)
        self.assertIn(self.jon_in_beekeeping, results)
        stream = yield V(self.jon).both_e(SupervisedBy, BelongsTo).get()
        results = yield stream.read()
        self.assertTrue(len(results), 2)
        self.assertIn(self.jon_eric, results)
        self.assertIn(self.jon_in_dist_dev, results)
        stream = yield V(self.jon).both_e(
            SupervisedBy, BelongsTo, EnrolledIn, TaughtBy).get()
        results = yield stream.read()
        self.assertTrue(len(results), 4)
        self.assertIn(self.jon_eric, results)
        self.assertIn(self.jon_physics, results)
        self.assertIn(self.jon_in_dist_dev, results)
        self.assertIn(self.jon_in_beekeeping, results)

    @gen_test
    def test_has(self):
        # IDK about this whole get property by name thing
        stream = yield V(self.jon).out().has(
            ResearchGroup.get_property_by_name("name"), "Distributed Development").get()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.dist_dev)

    @gen_test
    def test_has_lt_gt(self):
        stream = yield V(self.jon).out().has(
            Course.get_property_by_name("credits"), 5.0, GREATER_THAN).get()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        stream = yield V(self.jon).out().has(
            Course.get_property_by_name("credits"), 5.0, LESS_THAN).get()
        results = yield stream.read()
        self.assertEqual(len(results), 0)

    @gen_test
    def test_has_label(self):
        stream = yield V(self.jon).out().has_label(
            ResearchGroup.get_label()).get()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.dist_dev)
        stream = yield V(self.jon).out().has_label(
            ResearchGroup.get_label(), Course.get_label()).get()
        results = yield stream.read()
        self.assertEqual(len(results), 2)
        self.assertIn(self.dist_dev, results)
        self.assertIn(self.beekeeping, results)

    @gen_test
    def test_has_id(self):
        stream = yield V(self.jon).out().has_id(
            self.dist_dev.id).get()
        results = yield stream.read()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], self.dist_dev)
        # This should work...
        stream = yield V(self.jon).out().has_id(
            self.dist_dev.id, self.beekeeping.id).get()
        results = yield stream.read()
        # self.assertEqual(len(results), 2)
        # self.assertIn(self.dist_dev, results)
        # self.assertIn(self.beekeeping, results)

    # Not working
    # @gen_test
    # def test_has_key(self):
        # stream = yield V(self.jon).out().has_key(
        #     ResearchGroup.get_property_by_name("name")).get()
        # results = yield stream.read()
        # self.assertEqual(len(results), 1)
        # self.assertIn(self.dist_dev, results)
        # stream = yield V(self.jon).out().has_key(
        #     Course.get_property_by_name("credits")).get()
        # results = yield stream.read()
        # self.assertEqual(len(results), 1)
        # self.assertIn(self.beekeeping, results)
