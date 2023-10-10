
import logging
from ..retail_inventory import RetailInventory
from ..potion_type import PotionType
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
  
