#write 2 - 5 tests that fully test the functionality of the API
import json
import requests
import os
import pytest
from ...helpers.load_fixture import load_fixture
from ...models.transaction import Transaction
from ...models.wholesale_inventory import WholesaleInventory
from ...models.customer import Customer
from ...models.cart import Cart

base_route = "http://127.0.0.1:3000"
headers = {'Access_token': f'{os.environ.get("API_KEY")}'}


def call_reset(): 
  endpoint = "/admin/reset/"
  url = base_route + endpoint
  response = requests.post(url, headers=headers)
  return response.status_code == 200

@pytest.mark.skipif(os.environ.get('ENV') != 'DEV', reason="Only run in dev")
def test_create_cart():
  assert call_reset()
  endpoint = "/carts/"
  url = base_route + endpoint
  request_body = load_fixture("carts/create_cart_req.json")
  customer_str =  json.loads(request_body)["customer"]
  response = requests.post(url, headers=headers, data=request_body)
  response_obj = json.loads(response.content)
  assert response.status_code == 200, "Should return status code 200"
  assert response_obj["cart_id"] != None, "Should return a cart_id"
  created_cart = Cart.find(response_obj["cart_id"])
  created_customer = Customer.find(created_cart.customer_id)
  assert created_customer != None
  assert created_customer.str == customer_str, "Should create customer with correct str"

def test_add_items_to_cart():
  #TODO: finish writing this test.... seems like i made my life horribly hard by adding too much abstraction layer
  assert call_reset()
  #TODO: populate catalog with things to buy
  endpoint = "/carts/"
  url = base_route + endpoint
  request_body = load_fixture("carts/create_cart_req.json")
  response = requests.post(url, headers=headers, data=request_body)
  response_obj = json.loads(response.content)
  assert response.status_code == 200, "Should return status code 200"
  endpoint = f"/carts/{response_obj['cart_id']}/items/{response_obj['cart_id']}"
  url = base_route + endpoint



   


