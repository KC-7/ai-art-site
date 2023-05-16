from django.urls import reverse
from django.test import Client, TestCase


class PostListViewTest(TestCase):
    """
    Basic test case for PostList view.
    """
    def setUp(self):
        self.client = Client()

    def test_post_list_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertIn('object_list', response.context)
