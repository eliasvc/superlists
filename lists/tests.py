# TestCase is an expanded version of unittest.TestCase that algo contains Django-specific goodies
from django.test import TestCase

class SmokeTest(TestCase):

	def test_bad_math(self):
		self.assertEquals(1 + 1, 3)