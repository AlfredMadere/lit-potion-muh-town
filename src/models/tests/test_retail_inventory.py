
import logging
from ..retail_inventory import RetailInventory, PotionInventory
from ..potion_type import PotionType
from ..wholesale_inventory import WholesaleInventory, Barrel
from ..transaction import Transaction
def test_get_catalog():
  RetailInventory.reset()
  PotionType.reset()
  potion_type = PotionType.create("test name", "test sku", [30, 50, 20, 0], 0)
  potion_type2 = PotionType.create("test name 2", "test sku 2", [30, 40, 20, 10], 0)
  RetailInventory.create(potion_type.id, 2, 60)
  RetailInventory.create(potion_type.id, -2, -5)
  RetailInventory.create(potion_type.id, 1, -5)
  RetailInventory.create(potion_type2.id, 1, 20)

  catalog = RetailInventory.get_catalog()
  assert catalog == [
    {
      'sku': potion_type.sku,
      'name': potion_type.name,
      'quantity': 1, 
      'price': 50,  
      'potion_type': potion_type.type 
  },
    {
      'sku': potion_type2.sku,
      'name': potion_type2.name,
      'quantity': 1, 
      'price': 20,  
      'potion_type': potion_type2.type 
  },
  ]


def test_accept_potions_delivery():
  potions_delivered = [
    PotionInventory(
      potion_type=[100, 0, 0, 0],
      quantity=1
    )
  ]
  barrels_delivery = [
    Barrel(sku="red", ml_per_barrel=500, potion_type=[1, 0, 0, 0], price=100, quantity=1),
    Barrel(sku="red", ml_per_barrel=500, potion_type=[1, 0, 0, 0], price=100, quantity=2)
]
  Transaction.reset()
  RetailInventory.reset()
  WholesaleInventory.reset()
  PotionType.create("test namesf", "test skusdf", [100, 0, 0, 0], 0)
  Transaction.create(500, None)

  WholesaleInventory.accept_barrels_delivery(barrels_delivery)
  RetailInventory.accept_potions_delivery(potions_delivered)
  red_stock = WholesaleInventory.get_stock([1, 0, 0, 0])
  assert red_stock == 1400




  
