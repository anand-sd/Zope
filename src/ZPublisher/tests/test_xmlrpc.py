import unittest

from DateTime import DateTime


try:
    import xmlrpc.client as xmlrpclib
except ImportError:
    import xmlrpclib


class FauxResponse(object):

    def __init__(self):
        self._headers = {}
        self._body = None

    def setBody(self, body):
        self._body = body

    def setHeader(self, name, value):
        self._headers[name] = value

    def setStatus(self, status):
        self._status = status


class FauxInstance(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)


class XMLRPCResponseTests(unittest.TestCase):

    def _getTargetClass(self):
        from ZPublisher.xmlrpc import Response
        return Response

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_setBody(self):
        body = FauxInstance(_secret='abc', public='def')
        faux = FauxResponse()
        response = self._makeOne(faux)

        response.setBody(body)

        body_str = faux._body
        self.assertEqual(type(body_str), type(''))

        as_set, method = xmlrpclib.loads(body_str)
        as_set = as_set[0]

        self.assertIsNone(method)
        self.assertNotIn('_secret', as_set.keys())
        self.assertIn('public', as_set.keys())
        self.assertEqual(as_set['public'], 'def')

    def test_nil(self):
        body = FauxInstance(public=None)
        faux = FauxResponse()
        response = self._makeOne(faux)
        response.setBody(body)
        data, method = xmlrpclib.loads(faux._body)
        self.assertIs(data[0]['public'], None)

    def test_instance(self):
        # Instances are turned into dicts with their private
        # attributes removed.
        body = FauxInstance(_secret='abc', public='def')
        faux = FauxResponse()
        response = self._makeOne(faux)
        response.setBody(body)
        data, method = xmlrpclib.loads(faux._body)
        data = data[0]
        self.assertEqual(data, {'public': 'def'})

    def test_instanceattribute(self):
        # While the removal of private ('_') attributes works fine for the
        # top-level instance, how about attributes that are themselves
        # instances?
        body = FauxInstance(public=FauxInstance(_secret='abc', public='def'))
        faux = FauxResponse()
        response = self._makeOne(faux)
        response.setBody(body)
        data, method = xmlrpclib.loads(faux._body)
        data = data[0]['public']
        self.assertEqual(data, {'public': 'def'})

    def test_instanceattribute_recursive(self):
        # Instance "flattening" should work recursively, ad infinitum
        body = FauxInstance(public=FauxInstance(public=FauxInstance(
            _secret='abc', public='def')))
        faux = FauxResponse()
        response = self._makeOne(faux)
        response.setBody(body)
        data, method = xmlrpclib.loads(faux._body)
        data = data[0]['public']['public']
        self.assertEqual(data, {'public': 'def'})

    def test_instance_in_list(self):
        # Instances are turned into dicts with their private
        # attributes removed, even when embedded in another
        # data structure.
        body = [FauxInstance(_secret='abc', public='def')]
        faux = FauxResponse()
        response = self._makeOne(faux)
        response.setBody(body)
        data, method = xmlrpclib.loads(faux._body)
        data = data[0][0]
        self.assertEqual(data, {'public': 'def'})

    def test_instance_in_dict(self):
        # Instances are turned into dicts with their private
        # attributes removed, even when embedded in another
        # data structure.
        body = {'faux': FauxInstance(_secret='abc', public='def')}
        faux = FauxResponse()
        response = self._makeOne(faux)
        response.setBody(body)
        data, method = xmlrpclib.loads(faux._body)
        data = data[0]['faux']
        self.assertEqual(data, {'public': 'def'})

    def test_zopedatetimeinstance(self):
        # DateTime instance at top-level
        body = DateTime('2006-05-24 07:00:00 GMT+0')
        faux = FauxResponse()
        response = self._makeOne(faux)
        response.setBody(body)
        data, method = xmlrpclib.loads(faux._body)
        data = data[0]
        self.assertTrue(isinstance(data, xmlrpclib.DateTime))
        self.assertEqual(data.value, u'2006-05-24T07:00:00+00:00')

    def test_zopedatetimeattribute(self):
        # DateTime instance as attribute
        body = FauxInstance(public=DateTime('2006-05-24 07:00:00 GMT+0'))
        faux = FauxResponse()
        response = self._makeOne(faux)
        response.setBody(body)
        data, method = xmlrpclib.loads(faux._body)
        data = data[0]['public']
        self.assertTrue(isinstance(data, xmlrpclib.DateTime))
        self.assertEqual(data.value, u'2006-05-24T07:00:00+00:00')

    def test_zopedatetimeattribute_recursive(self):
        # DateTime encoding should work recursively
        body = FauxInstance(public=FauxInstance(
            public=DateTime('2006-05-24 07:00:00 GMT+0')))
        faux = FauxResponse()
        response = self._makeOne(faux)
        response.setBody(body)
        data, method = xmlrpclib.loads(faux._body)
        data = data[0]['public']['public']
        self.assertTrue(isinstance(data, xmlrpclib.DateTime))
        self.assertEqual(data.value, u'2006-05-24T07:00:00+00:00')

    def test_zopedatetimeinstance_in_list(self):
        # DateTime instance embedded in a list
        body = [DateTime('2006-05-24 07:00:00 GMT+0')]
        faux = FauxResponse()
        response = self._makeOne(faux)
        response.setBody(body)
        data, method = xmlrpclib.loads(faux._body)
        data = data[0][0]
        self.assertTrue(isinstance(data, xmlrpclib.DateTime))
        self.assertEqual(data.value, u'2006-05-24T07:00:00+00:00')

    def test_zopedatetimeinstance_in_dict(self):
        # DateTime instance embedded in a dict
        body = {'date': DateTime('2006-05-24 07:00:00 GMT+0')}
        faux = FauxResponse()
        response = self._makeOne(faux)
        response.setBody(body)
        data, method = xmlrpclib.loads(faux._body)
        data = data[0]['date']
        self.assertTrue(isinstance(data, xmlrpclib.DateTime))
        self.assertEqual(data.value, u'2006-05-24T07:00:00+00:00')

    def test_functionattribute(self):
        # Cannot marshal functions or methods, obviously

        def foo():
            pass

        body = FauxInstance(public=foo)
        faux = FauxResponse()
        response = self._makeOne(faux)
        response.setBody(body)
        func = xmlrpclib.loads(faux._body)
        self.assertEqual(func, (({'public': {}},), None))

    def test_emptystringattribute(self):
        # Test an edge case: attribute name '' is possible,
        # at least in theory.
        body = FauxInstance(_secret='abc')
        setattr(body, '', True)
        faux = FauxResponse()
        response = self._makeOne(faux)
        response.setBody(body)
        data, method = xmlrpclib.loads(faux._body)
        data = data[0]
        self.assertEqual(data, {'': True})
