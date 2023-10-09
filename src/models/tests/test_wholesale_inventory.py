import logging
from ..wholesale_inventory import WholesaleInventory, Barrel

WholesaleInventory.reset()

def test_get_stock():
  barrel_to_add: Barrel = Barrel(sku="red", ml_per_barrel=1000, potion_type=[1, 0, 0, 0], price=100, quantity=1) 
  second_barrel_to_add: Barrel = Barrel(sku="red_big", ml_per_barrel=500, potion_type=[1, 0, 0, 0], price=100, quantity=1) 
  third_barrel_to_add: Barrel = Barrel(sku="blue", ml_per_barrel=500, potion_type=[0, 0, 1, 0], price=100, quantity=2) 
  inventory = WholesaleInventory.add_to_inventory(barrel_to_add)
  red_ml = WholesaleInventory.get_stock([1, 0, 0, 0])
  blue_ml = WholesaleInventory.get_stock([0, 0, 1, 0])
  assert red_ml == 1000
  assert blue_ml == 0
  assert inventory == "OK"
  inventory = WholesaleInventory.add_to_inventory(second_barrel_to_add)
  red_ml = WholesaleInventory.get_stock([1, 0, 0, 0])
  blue_ml = WholesaleInventory.get_stock([0, 0, 1, 0])
  assert red_ml == 1500
  assert blue_ml == 0
  assert inventory == "OK"
  inventory = WholesaleInventory.add_to_inventory(third_barrel_to_add)
  red_ml = WholesaleInventory.get_stock([1, 0, 0, 0])
  blue_ml = WholesaleInventory.get_stock([0, 0, 1, 0])
  assert red_ml == 1500
  assert blue_ml == 1000 
  assert inventory == "OK"



def test_add_to_inventory():
  barrel_to_add: Barrel = Barrel(sku="green", ml_per_barrel=1000, potion_type=[0, 1, 0, 0], price=100, quantity=1) 
  inventory = WholesaleInventory.add_to_inventory(barrel_to_add)
  assert inventory == "OK"
  red_ml = WholesaleInventory.get_stock([0, 1, 0, 0])
  assert red_ml == 1000


