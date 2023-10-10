import logging
from ..wholesale_inventory import WholesaleInventory, Barrel
from ..potion_type import PotionType
from ...helpers.load_fixture import load_fixture
import json


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

def test_max_mixable():
  potion_type = PotionType(1, "test", "test", [30, 30, 20, 20], 0)
  available_ingredients = [0, 0, 0, 0]
  max_mixable =WholesaleInventory.max_mixable(potion_type, available_ingredients)
  assert max_mixable == 0
  available_ingredients = [100, 0, 0, 0]
  max_mixable =WholesaleInventory.max_mixable(potion_type, available_ingredients)
  assert max_mixable == 0
  available_ingredients = [100, 100, 100, 100]
  max_mixable =WholesaleInventory.max_mixable(potion_type, available_ingredients)
  assert max_mixable == 3


def test_get_bottler_plan():
  WholesaleInventory.reset()
  PotionType.reset()
  PotionType.create("test name", "test sku", [30, 50, 20, 0], 0)
  barrel_to_add: Barrel = Barrel(sku="red", ml_per_barrel=100, potion_type=[1, 0, 0, 0], price=100, quantity=1) 
  second_barrel_to_add: Barrel = Barrel(sku="green", ml_per_barrel=50, potion_type=[0, 1, 0, 0], price=100, quantity=2) 
  third_barrel_to_add: Barrel = Barrel(sku="blue", ml_per_barrel=50, potion_type=[0, 0, 1, 0], price=100, quantity=2) 
  WholesaleInventory.add_to_inventory(barrel_to_add)
  WholesaleInventory.add_to_inventory(second_barrel_to_add)
  WholesaleInventory.add_to_inventory(third_barrel_to_add)
  # assert red_ml == 100
  # assert blue_ml == 100 
  # assert green_ml == 100

  bottler_plan = WholesaleInventory.get_bottler_plan()

  assert bottler_plan == [
    {
      "potion_type": [30, 50, 20, 0],
      "quantity": 2
    },
    
  ]


  