#write 2 - 5 tests that fully test the functionality of the API
import json
import requests
import os
import logging
import pytest



base_route = "http://127.0.0.1:3000"
headers = {'Access_token': f'{os.environ.get("API_KEY")}'}


@pytest.mark.skipif(os.environ.get('ENV') != 'DEV', reason="Only run in dev")
def test_reset():
  endpoint = "/admin/reset/"
  url = base_route + endpoint
  response = requests.post(url, headers=headers)
  assert response.status_code == 200, "Should return status code 200"
  endpoint = "/catalog/"
  url = base_route + endpoint
  response = requests.get(url, headers=headers)
  assert response.status_code == 200
  assert response.content == b'[]', "Should return empty array"
  endpoint = "/audit/inventory"
  url = base_route + endpoint
  response = requests.get(url, headers=headers)
  assert response.status_code == 200
  expected_inventory = {
  "number_of_potions": 0,
  "ml_in_barrels": 0,
  "gold": 100
}
  assert json.loads(response.content) == json.loads(json.dumps(expected_inventory)), "Should return inventory"