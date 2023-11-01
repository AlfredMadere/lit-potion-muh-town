
from pydantic import BaseModel
from .retail_inventory import RetailInventory
from sqlalchemy.sql import text
from src import database as db
from .customer import Customer
from .cart_item import CartItemM
from .potion_type import PotionType
from .invoice import Invoice
from .transaction import Transaction

class NewCart(BaseModel):
  customer: str

class CartItem(BaseModel):
  quantity: int


class CartCheckout(BaseModel):
  payment: str

class InventoryItem(BaseModel):
  sku: str
  quantity: int


class Cart:
  table_name = "cart"
  def __init__(self, id: int, customer_id: int, checked_out: bool):
    self.id = id
    self.customer_id = customer_id
    self.checked_out = checked_out
    self._items = None


  @staticmethod
  def reset():
    try:
      sql_to_execute = text(f"DELETE FROM {Cart.table_name}")
      with db.engine.begin() as connection:
        connection.execute(sql_to_execute)
      return "OK"
    except Exception as error:
        print("unable to reset cart table: ", error)
        raise Exception("ERROR: unable to reset cart table", error)
  @staticmethod
  def find(id: int):
    try:
      sql_to_execute = text(f"SELECT id, customer_id, checked_out FROM {Cart.table_name} WHERE id = {id}")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute)
        row = result.fetchone()
        if row is None:
          raise Exception("Cart not found")
        
        return Cart(row[0], row[1], row[2])
    except Exception as error:
      print("unable to find cart: ", error)
      raise Exception("ERROR: unable to find cart", error)
  
  @staticmethod
  def new_cart(new_cart: NewCart): 
    try:
      customer = Customer.upsert(new_cart.customer)
      sql_to_execute = text(f"INSERT INTO {Cart.table_name} (customer_id) VALUES (:customer_id) RETURNING id")
      with db.engine.begin() as connection:
        result =connection.execute(sql_to_execute, {"customer_id": customer.id})
        row = result.fetchone()
        return Cart(row[0], customer.id, False)
    except Exception as error:
      raise Exception("ERROR: unable to create cart", error)

  
  def checkout(self, cart_checkout: CartCheckout):
    try: 
      #TODO fix checkout method so it doesn't time out with large queue pool whatever that means
      #TODO: check if the payment string is valid
      checkout_result = {}
      if self.checked_out:
        raise Exception("Cart already checked out")
      try: 
        if not self.items:
          raise Exception("Cart could not retrieve items")
        adjustment_result = RetailInventory.adjust_inventory(self.items)
        checkout_result['total_gold_paid'] = adjustment_result['total_gold_paid']
        checkout_result['total_potions_bought'] = adjustment_result['total_potions_bought']
        #pickup here: figure how how to create the invioces and transactions for a checkout 
        #TODO: make better invoice description by adding a way to get item string
        invoice_description = f"payment of {adjustment_result['total_gold_paid']} for {adjustment_result['total_potions_bought']} items. Items were: {self.get_cart_items_string()}"
        invoice = Invoice.create(None, self.id, invoice_description)
        Transaction.create(adjustment_result['total_gold_paid'], invoice.id)
        self.set_checked_out()
        print("checkout_result: ", checkout_result)
        return checkout_result
      except Exception as error:
        raise Exception("Transaction Failed: Could not adjust inventory", error)
    except Exception as error:
      raise Exception("ERROR: unable to checkout cart", error) 
    

  def get_cart_items_string(self):
    try:
      generated_string = ""
      items = self.get_items()
      for item in items:
        generated_string += item.get_item_string()
      return generated_string
    except Exception as error:
      print("unable to get cart items string: ", error)
      raise Exception("ERROR: unable to get cart items string", error)

  #depricated
  def check_item_availability(self):
    try:
      items = self.get_items()
      print("items: ", items)
      unavailable_items = []
      for item in items:
        available = item.is_available(RetailInventory.get_catalog())
        if available:
          pass
        else:
          unavailable_items.append(item)
      return unavailable_items
    except Exception as error:
      print("unable to check item availability: ", error)
      raise Exception("ERROR: unable to check item availability", error)

      

  def set_item_quantity(self, item_sku: str, quantity: int):
    try:
      potion_type_id = PotionType.find_by_sku(item_sku).id
      #FIXME: when you create a cart item it should also remove it from the retail_inventory until the cart is voided
      quantity_available = RetailInventory.num_potion_type_available(potion_type_id)
      if quantity_available < quantity:
        raise Exception(f"Insufficient inventory for potion_type_id {potion_type_id}")
      else:
        CartItemM.create(self.id, potion_type_id, quantity)

    except Exception as error:
      print("unable to set item quantity: ", error)
      raise Exception("ERROR: unable to set item quantity", error)

  def get_items(self):
    try:
      items: list[CartItemM] = []
      sql_to_execute = text(f"SELECT id, cart_id, potion_type_id, quantity FROM {CartItemM.table_name} WHERE cart_id = {self.id}")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute)
        rows = result.fetchall()
        for row in rows:
          items.append(CartItemM(row[0], row[1], row[2], row[3]))
      self.items = items
      return items    
    except Exception as error:
      print("unable to get cart items: ", error)
      raise Exception("ERROR: unable to get cart items", error)

  def set_checked_out(self):
    try:
      sql_to_execute = text(f"UPDATE {Cart.table_name} SET checked_out = true WHERE id = {self.id}")
      with db.engine.begin() as connection:
        connection.execute(sql_to_execute)
    except Exception as error:
      raise Exception("ERROR: unable to set cart checked out", error)
  

  
  @property
  def items(self) -> list[CartItemM]:
    items = self.get_items()
    self._items = items
    return self._items
  
  @items.setter
  def items(self, value):
    self._items = value

