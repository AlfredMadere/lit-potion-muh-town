import logging
from ..wholesale_inventory import WholesaleInventory, Barrel

WholesaleInventory.reset()
def test_add_to_inventory():
  barrel_to_add: Barrel = Barrel(sku="red", ml_per_barrel=1000, potion_type=[1, 0, 0, 0], price=100, quantity=1) 
  inventory = WholesaleInventory.add_to_inventory(barrel_to_add)
  assert inventory == "OK"
  red_ml = WholesaleInventory.get_stock([1, 0, 0, 0])
  assert red_ml == 1000


