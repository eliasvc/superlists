# TestCase is an expanded version of unittest.TestCase that algo contains Django-specific goodies
from django.test import TestCase
from django.core.urlresolvers import resolve
from lists.views import home_page

class HomePageTest(TestCase):

	def test_root_url_resolves_to_home_page_view(self):
		found = resolve("/")
		self.assertEquals(found.func, home_page)	