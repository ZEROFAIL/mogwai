from __future__ import unicode_literals
import datetime
from pytz import utc
from uuid import uuid4
from nose.plugins.attrib import attr

from tornado.testing import gen_test

from mogwai.exceptions import MogwaiGremlinException
from mogwai.tests.base import BaseMogwaiTestCase

from mogwai.models import Vertex
from mogwai import properties
from mogwai import gremlin


class GroovyTestModel(Vertex):
    text = properties.Text()
    get_self = gremlin.GremlinMethod()
    cm_get_self = gremlin.GremlinMethod(method_name='get_self', classmethod=True)

    return_default = gremlin.GremlinValue(method_name='return_value', defaults={'val': lambda: 5000})
    return_list = gremlin.GremlinValue(property=1)
    return_value = gremlin.GremlinValue()

    arg_test1 = gremlin.GremlinValue()
    arg_test2 = gremlin.GremlinValue()


@attr('unit', 'gremlin')
class TestMethodLoading(BaseMogwaiTestCase):

    @gen_test
    def test_method_loads_and_works(self):
        v1 = yield GroovyTestModel.create(text='cross fingers')
        try:
            stream = yield v1.get_self()
            v2 = yield stream.read()
            self.assertEqual(v1.id, v2[0].id)

            stream = yield v1.cm_get_self(v1.id)
            v3 = yield stream.read()
            self.assertEqual(v1.id, v3[0].id)
        finally:
            yield v1.delete()


@attr('unit', 'gremlin', 'gremlin2')
class TestMethodArgumentHandling(BaseMogwaiTestCase):

    @gen_test
    def test_callable_defaults(self):
        """
        Tests that callable default arguments are called
        """
        v1 = yield GroovyTestModel.create(text='cross fingers')
        try:
            default = yield v1.return_default()
            self.assertEqual(default, 5000)
        finally:
            yield v1.delete()

    @gen_test
    def test_gremlin_value_enforces_single_object_returned(self):
        """
        Tests that a GremlinValue instance raises an error if more than one object is returned
        """
        v1 = yield GroovyTestModel.create(text='cross fingers')
        try:
            with self.assertRaises(MogwaiGremlinException):
                yield v1.return_list
        finally:
            yield v1.delete()

    @gen_test
    def test_type_conversion(self):
        """ Tests that the gremlin method converts certain python objects to their gremlin equivalents """
        v1 = yield GroovyTestModel.create(text='cross fingers')

        now = datetime.datetime.now(tz=utc)
        uu = uuid4()
        try:
            n = yield v1.return_value(now)
            self.assertEqual(n, properties.DateTime().to_database(now))

            u = yield v1.return_value(uu)
            self.assertEqual(u, properties.UUID().to_database(uu))
        finally:
            yield v1.delete()

    @gen_test
    def test_initial_arg_name_isnt_set(self):
        """ Tests that the name of the first argument in a instance method """
        v = yield GroovyTestModel.create(text='cross fingers')
        try:
            arg1 = yield v.arg_test1()
            arg2 = yield v.arg_test2()
            self.assertEqual(v, arg1)
            self.assertEqual(v, arg2)
        finally:
            v.delete()
