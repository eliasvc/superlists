from django.http import HttpRequest
# TestCase is an expanded version of unittest.TestCase that algo contains Django-specific goodies
from django.test import TestCase
from django.core.urlresolvers import resolve


from lists.views import home_page

class HomePageTest(TestCase):

	def test_uses_home_page_template(self):
		response = self.client.get('/')
		self.assertTemplateUsed(response, 'home.html')