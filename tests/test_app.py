import unittest
import json
from app import app

class CatalogAppTestCase(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.csrf_token = None

    def login(self):
        login_data = {
            "username_or_email": "brucy",
            "password": "brucy123"
        }
        response = self.client.post('/api/login', json=login_data)
        self.assertEqual(response.status_code, 200)

        # Extract CSRF token and JWT access token from Set-Cookie headers
        csrf_token = None
        access_token_cookie = None
        cookies = response.headers.getlist('Set-Cookie')
        for cookie in cookies:
          if 'csrf_access_token=' in cookie:
            csrf_token = cookie.split('csrf_access_token=')[1].split(';')[0]
          if 'access_token_cookie=' in cookie:
            access_token_cookie = cookie.split('access_token_cookie=')[1].split(';')[0]

        self.assertIsNotNone(csrf_token, "CSRF token missing in login response cookies.")
        self.assertIsNotNone(access_token_cookie, "JWT access token cookie missing in login response.")

    # Set cookies on test client for subsequent requests (corrected usage)
        self.client.set_cookie('csrf_access_token', csrf_token, domain='localhost')
        self.client.set_cookie('access_token_cookie', access_token_cookie, domain='localhost')

        self.csrf_token = csrf_token
        return response

    def test_01_login(self):
        response = self.login()
        self.assertIn('message', response.get_json())
        self.assertEqual(response.status_code, 200)

    def test_02_access_protected_endpoint_without_login(self):
        # Access /api/catalogs POST without login - should fail (401 or 422)
        catalog_data = {
            "name": "Test Catalog",
            "description": "Description",
            "start_date": "2030-01-01",
            "end_date": "2030-01-31",
            "status": "active"
        }
        response = self.client.post('/api/catalogs', json=catalog_data)
        self.assertIn(response.status_code, [401, 422])

    def test_03_create_catalog(self):
        self.login()
        catalog_data = {
            "name": "Test Catalog",
            "description": "Test description",
            "start_date": "2030-01-01",
            "end_date": "2030-01-31",
            "status": "active"
        }
        response = self.client.post('/api/catalogs', json=catalog_data, headers={'X-CSRF-TOKEN': self.csrf_token})
        self.assertEqual(response.status_code, 201)
        self.assertIn('catalog_id', response.get_json().get('data', {}))

    def test_04_get_all_catalogs(self):
        response = self.client.get('/api/catalogs')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.get_json().get('data'), list)

    def test_05_get_catalog_by_id(self):
        self.login()
        # First create catalog
        catalog_data = {
            "name": "Catalog For Get",
            "description": "Description",
            "start_date": "2030-01-01",
            "end_date": "2030-01-31",
            "status": "active"
        }
        create_resp = self.client.post('/api/catalogs', json=catalog_data, headers={'X-CSRF-TOKEN': self.csrf_token})
        self.assertEqual(create_resp.status_code, 201)
        catalog_id = create_resp.get_json()['data']['catalog_id']

        # Get by id
        get_resp = self.client.get(f'/api/catalogs/{catalog_id}')
        self.assertEqual(get_resp.status_code, 200)
        self.assertEqual(get_resp.get_json()['data']['catalog_id'], catalog_id)

    def test_06_update_catalog(self):
        self.login()
        # Create first
        catalog_data = {
            "name": "Catalog To Update",
            "description": "Description",
            "start_date": "2030-01-01",
            "end_date": "2030-01-31",
            "status": "active"
        }
        create_resp = self.client.post('/api/catalogs', json=catalog_data, headers={'X-CSRF-TOKEN': self.csrf_token})
        catalog_id = create_resp.get_json()['data']['catalog_id']

        # Update
        updated_data = {
            "name": "Updated Catalog Name",
            "description": "Updated description",
            "start_date": "2030-02-01",
            "end_date": "2030-02-28",
            "status": "inactive"
        }
        update_resp = self.client.put(f'/api/catalogs/{catalog_id}', json=updated_data, headers={'X-CSRF-TOKEN': self.csrf_token})
        self.assertEqual(update_resp.status_code, 200)

    def test_07_delete_catalog(self):
        self.login()
        # Create first
        catalog_data = {
            "name": "Catalog To Delete",
            "description": "Description",
            "start_date": "2030-01-01",
            "end_date": "2030-01-31",
            "status": "active"
        }
        create_resp = self.client.post('/api/catalogs', json=catalog_data, headers={'X-CSRF-TOKEN': self.csrf_token})
        catalog_id = create_resp.get_json()['data']['catalog_id']

        # Delete
        delete_resp = self.client.delete(f'/api/catalogs/{catalog_id}', headers={'X-CSRF-TOKEN': self.csrf_token})
        self.assertEqual(delete_resp.status_code, 200)

    def test_08_logout(self):
        self.login()
        logout_resp = self.client.post('/api/logout', headers={'X-CSRF-TOKEN': self.csrf_token})
        self.assertEqual(logout_resp.status_code, 200)

if __name__ == '__main__':
    unittest.main()
