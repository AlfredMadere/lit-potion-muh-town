from sqlalchemy import text
from src import database as db
from .retail_inventory import RetailInventory
from .potion_type import PotionType

class CartItemM:
  table_name = "cart_item"
  def __init__(self, id: int, cart_id: int, potion_type_id: int, quantity: int):
    self.id = id
    self.cart_id = cart_id
    self.potion_type_id = potion_type_id
    self.quantity = quantity
    self.potion_type = None

  @staticmethod
  def create(cart_id: int, potion_type_id: int, quantity: int):
    try:
      sql_to_execute = text(f"INSERT INTO {CartItemM.table_name} (cart_id, potion_type_id, quantity) VALUES (:cart_id, :potion_type_id, :quantity)")
      with db.engine.begin() as connection:
        connection.execute(sql_to_execute, {"cart_id": cart_id, "potion_type_id": potion_type_id, "quantity": quantity})
    except Exception as error:
      print("unable to create cart item: ", error)
      raise Exception("ERROR: unable to create cart item", error)


  def is_available(self):
    try:
      catalog = RetailInventory.get_catalog()
      self.get_potion_type()
      catalog_potion = [potion for potion in catalog if potion["potion_type"] == self.potion_type.type]
      if self.quantity <= catalog_potion["quantity"]:
        return True
      else:
        return False
    except Exception as error:
      print("unable to check if item is available: ", error)
      raise Exception("ERROR: unable to check if item is available", error)

  def get_potion_type(self):
    try:
      potion_type = PotionType.find(self.potion_type_id)
      self.potion_type = potion_type
      return self.potion_type 
    except Exception as error:
      print("unable to get potion type: ", error)
      raise Exception("ERROR: unable to get potion type", error)
