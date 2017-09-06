import json

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class UserViewSetTests(APITestCase):
    """
    Unit tests for User API endpoint.
    """
    def setUp(self):
        self.user = get_user_model().objects.create_user('johndoe', 'john@doe.com', 'johndoe')
        self.client.login(username='johndoe', password='johndoe')

    def test_me_endpoint(self):
        url = reverse('users:myuser-me')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('username'), self.user.username)
        self.assertEqual(response.data.get('email'), self.user.email)
        self.assertEqual(response.data.get('token'), self.user.auth_token.key)

    def test_me_endpoint_with_query_string_token(self):
        url = reverse('users:myuser-me')

        self.client.logout()
        response = self.client.get('{}?token={}'.format(url, self.user.auth_token.key))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_me_endpoint_without_credentials_that_return_forbidden(self):
        url = reverse('users:myuser-me')

        self.client.logout()
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_endpoint(self):
        url = reverse('users:myuser-detail', args=[self.user.pk])
        data = json.dumps({
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'should.not.be@updated.com',
            'username': 'should.not.be.updated'
        })

        response = self.client.put(url, data, content_type='application/json')
        user = get_user_model().objects.get(email=self.user.email)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(self.user.email, user.email)
        self.assertEqual(self.user.username, user.username)

        self.assertNotEqual(self.user.first_name, user.first_name)
        self.assertNotEqual(self.user.last_name, user.last_name)
