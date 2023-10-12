# write 2 - 5 tests that fully test the functionality of the API

import requests
import os
import logging
import pytest



base_route = "http://127.0.0.1:3000"
headers = {'Access_token': f'{os.environ.get("API_KEY")}'}

@pytest.mark.skipif(os.environ.get('ENV') != 'DEV', reason="Only run in dev")
def test_deliver_and_mix():
  endpoint = "/admin/reset/"
  url = base_route + endpoint
  response = requests.post(url, headers=headers)
  assert response.status_code == 200, "Should return status code 200"
  