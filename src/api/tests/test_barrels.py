#write 2 - 5 tests that fully test the functionality of the API
import json
import requests
import os
import logging
import pytest
from ...helpers.load_fixture import load_fixture
from ...models.transaction import Transaction
from ...models.wholesale_inventory import WholesaleInventory



base_route = "http://127.0.0.1:3000"
headers = {'Access_token': f'{os.environ.get("API_KEY")}'}



def call_reset(): 
  endpoint = "/admin/reset/"
  url = base_route + endpoint
  response = requests.post(url, headers=headers)
  return response.status_code == 200

@pytest.mark.skipif(os.environ.get('ENV') != 'DEV', reason="Only run in dev")
def test_plan():
  assert call_reset()
  endpoint = "/barrels/plan/"
  url = base_route + endpoint
  request_body = load_fixture("wholesale_catalog_0.json")

  response = requests.post(url, headers=headers, data=request_body)
  assert response.status_code == 200, "Should return status code 200"
  expected_plan = [
  {
    "sku": "SMALL_RED_BARREL",
    "quantity": 1
  }
]
  assert json.loads(response.content) == json.loads(json.dumps(expected_plan)), "Should return correct plan"
  
@pytest.mark.skipif(os.environ.get('ENV') != 'DEV', reason="Only run in dev")
def test_single_delivery():
  assert call_reset()
  endpoint = "/barrels/deliver/"
  url = base_route + endpoint
  request_body = load_fixture("barrels/deliver_input_1_sm_red.json")
  response = requests.post(url, headers=headers, data=request_body)
  assert response.status_code == 200, "Should return status code 200"
  current_balance = Transaction.get_current_balance()
  assert current_balance == 0
  endpoint = "/audit/inventory"
  url = base_route + endpoint
  response = requests.get(url, headers=headers)
  assert response.status_code == 200
  expected_inventory = {
  "number_of_potions": 0,
  "ml_in_barrels": 500,
  "gold": 0
  }
  assert json.loads(response.content) == json.loads(json.dumps(expected_inventory)), "Should return 500ml in barrels"
  


@pytest.mark.skipif(os.environ.get('ENV') != 'DEV', reason="Only run in dev")
def test_double_delivery_too_many():
  assert call_reset()
  endpoint = "/barrels/deliver/"
  url = base_route + endpoint
  request_body = load_fixture("barrels/deliver_request_2_sm_red.json")
  response = requests.post(url, headers=headers, data=request_body)
  assert response.status_code == 500, "Should return status code 500"
  current_balance = Transaction.get_current_balance()
  assert current_balance == 100
  endpoint = "/audit/inventory"
  url = base_route + endpoint
  response = requests.get(url, headers=headers)
  assert response.status_code == 200
  expected_inventory = {
  "number_of_potions": 0,
  "ml_in_barrels": 0,
  "gold": 100
  }
  assert json.loads(response.content) == json.loads(json.dumps(expected_inventory)), "Should return 500ml in barrels"
  
  
@pytest.mark.skipif(os.environ.get('ENV') != 'DEV', reason="Only run in dev")
def test_correct_double_delivery():
  assert call_reset()
  Transaction.create(200, None) # make sure we got enough gold to pay for this shit
  endpoint = "/barrels/deliver/"
  url = base_route + endpoint
  request_body = load_fixture("barrels/deliver_request_2_sm_red.json")
  response = requests.post(url, headers=headers, data=request_body)
  assert response.status_code == 200, "Should return status code 500"
  current_balance = Transaction.get_current_balance()
  assert current_balance == 0
  endpoint = "/audit/inventory"
  url = base_route + endpoint
  response = requests.get(url, headers=headers)
  assert response.status_code == 200
  expected_inventory = {
  "number_of_potions": 0,
  "ml_in_barrels": 1000,
  "gold": 0 
  }
  assert WholesaleInventory.get_stock([1, 0, 0, 0]) == 1000
  assert json.loads(response.content) == json.loads(json.dumps(expected_inventory)), "Should return 500ml in barrels"
  
