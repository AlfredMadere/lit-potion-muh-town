from src import database as db
from sqlalchemy.sql import text
from typing import List
from .wholesale_inventory import WholesaleInventory
import json
from pydantic import BaseModel
from .transaction import Transaction
from .potion_type import PotionType
from .cart_item import CartItemM

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int


class RetailInventory:
  table_name = "retail_inventory"
  potion_price = 1 
  def __init__(self, id, potion_type_id: int, quantity_delta: int, price_delta: int ):
    self.id = id
    self.potion_type_id = potion_type_id
    self.quantity_delta = quantity_delta
    self.price_delta = price_delta

  #11900 red ml
  #1100 green ml
  #1100 blue ml
  #10000 dark ml


  @staticmethod
  def get_total_potions():
    try:
      total_retail_potions = 0
      sql_to_execute = text(f"SELECT id, potion_type_id, quantity_delta, price_delta, FROM retail_inventory")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute)
        rows = result.fetchall()
        for row in rows:
          total_retail_potions += row[2]
      return total_retail_potions
    except Exception as error:
      print("unable to get total potions: ", error)
      raise Exception("ERROR: unable to get total potions", error)

  @staticmethod
  def get_catalog() -> List[PotionInventory]:
    # Get all the rows from the catalog table and return them as an array of objects
    # Add up all the quantity and price_deltas for each potion_type_id
    sql_to_execute = text("SELECT id, potion_type_id, quantity_delta, price_delta FROM retail_inventory")
    inventory = []
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute)
        rows = result.fetchall()
        potion_type_totals = {}
        for row in rows:
            potion_type_id = row[1]
            quantity_delta = row[2]
            price_delta = row[3]
            if potion_type_id in potion_type_totals:
                potion_type_totals[potion_type_id]['quantity'] += quantity_delta
                potion_type_totals[potion_type_id]['price'] += price_delta
            else:
                potion_type_totals[potion_type_id] = {
                    'quantity': quantity_delta,
                    'price': price_delta
                }

        for potion_type_id, totals in potion_type_totals.items():
            # Query potiontype table for the type name and sku
            # Assuming you have a PotionType class with a get_potion_type function that retrieves the name and sku based on the potion_type_id
            potion_type = PotionType.find(potion_type_id)
            if totals['quantity'] == 0:
                continue
            inventory.append({
                'sku': potion_type.sku,
                'name': potion_type.name,
                'quantity': totals['quantity'],
                'price': totals['price'],
                'potion_type': potion_type.type 
            })

    return inventory
  


  @staticmethod
  def get_total_potions():
    try:
      inventory = RetailInventory.get_catalog()
      total_potions = 0
      for item in inventory:
        total_potions += item["quantity"]
      return total_potions
    except Exception as error:
      print("unable to get total potions: ", error)
      return "ERROR"

  def convert_to_catalog_item(self):
    return {
      "sku": self.sku,
      "name": self.name,
      "quantity": self.quantity,
      "price": self.price,
      "potion_type": self.type
    }
  @staticmethod
  def reset():
    try:
      sql_to_execute = text(f"DELETE FROM {RetailInventory.table_name}")
      with db.engine.begin() as connection:
        connection.execute(sql_to_execute)
      return "OK"
    except Exception as error:
        print("unable to reset retail inventory: ", error)
        return "ERROR"
  
  
  @staticmethod
  def accept_potions_delivery(potions_delivered: list[PotionInventory]):
    try:
      #check to see if there already exists an entry in the retailinventory with the same type as the potion delivered, if so then update the quantity, if not then create a new entry
      for potion in potions_delivered:
        with db.engine.begin() as connection:
          sql_to_execute = text(f'SELECT id FROM {"potion_type"} WHERE type = :potion_type')
          result = connection.execute(sql_to_execute, {"potion_type": potion.potion_type})
          row = result.fetchone()
          if row is None:
             raise Exception("Potion type in delivery not found")
          potion_type_id = row[0]
          potion_type = PotionType.find(potion_type_id)
          #get current price for potion type
          current_potion_price = RetailInventory.get_potion_price(potion_type_id)
          price_delta = RetailInventory.potion_price  
          if current_potion_price is not None:
            price_delta = 0
          sql_to_execute = text(f'INSERT INTO {RetailInventory.table_name} (potion_type_id, quantity_delta, price_delta) VALUES (:potion_type_id, :quantity_delta, :price_delta)') 
          result = connection.execute(sql_to_execute, {"potion_type_id": potion_type_id, "quantity_delta": potion.quantity, "price_delta": price_delta}) 
          WholesaleInventory.use_potion_inventory(potion_type.type, potion.quantity)
      return "OK"
    except Exception as error:
        print("unable to accept potion delivery things may be out of sync due to no roleback, check logs ", error)
        raise Exception("ERROR: unable to accept potion delivery things may be out of sync due to no roleback, check logs", error)
  @staticmethod
  def get_potion_price(potion_type_id: int):
    try:
      sql_to_execute = text(f"SELECT price_delta FROM {RetailInventory.table_name} WHERE potion_type_id = :potion_type_id")  
      current_potion_price = None
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"potion_type_id": potion_type_id})
        rows = result.fetchall()
        for row in rows:
          if current_potion_price is None:
            current_potion_price = row[0]
          else:
            current_potion_price += row[0]
      return current_potion_price
    except Exception as error:
      print("unable to get potion price: ", error)
      raise Exception("ERROR: unable to get potion price", error) 


  @staticmethod
  def items_available(items: list[CartItemM]):
    inventory = RetailInventory.get_inventory()

    for item_sku, quantity in items.items():
      print("Inventory:", [item.sku for item in inventory])
      print("Looking for SKU:", item_sku)
      print("Type of SKUs in inventory:", [type(item.sku) for item in inventory])
      print("Type of target SKU:", type(item_sku))


      #get the inventory item with the same sku as the item_sku
      inventory_item = None
      for item in inventory:
        print("item.sku:", item.sku)
        print("item_sku:", item_sku)
        if f'{item.sku.strip()}' == f'{item_sku.strip()}':
          inventory_item = item
          break      
      print ("inventory item: ", inventory_item)
      if( inventory_item is None):
        raise Exception("Item not found")
      if inventory_item.quantity < quantity:
        raise Exception("Not enough items available")
    return True  
  

  #FIXME: hardcoded potion price 
  @staticmethod
  def adjust_inventory(items: list[CartItemM]):
        #update the specific row in the table self.id
        try:
          total_gold_paid = 0
          total_potions_bought = 0
          for item in items:
            #FIXME: hardcoded potion price
            potion_price = RetailInventory.get_potion_price(item.potion_type_id)
            total_gold_paid += potion_price*item.quantity
            total_potions_bought += item.quantity
            sql_to_execute = text(f"INSERT INTO {RetailInventory.table_name} (potion_type_id, quantity_delta, price_delta) VALUES (:potion_type_id, :quantity_delta, :price_delta) RETURNING id, potion_type_id, quantity_delta, price_delta")
            with db.engine.begin() as connection:
              connection.execute(sql_to_execute, {"potion_type_id": item.potion_type_id, "quantity_delta": item.quantity + -1, "price_delta": 0})
          return {"total_potions_bought": total_potions_bought, "total_gold_paid": total_gold_paid}
        except: 
            raise Exception("Could not adjust inventory")

  
  @staticmethod
  def create(potion_type_id: int, quantity_delta: int, price_delta: int):
    try:
      sql_to_execute = text(f"INSERT INTO {RetailInventory.table_name} (potion_type_id, quantity_delta, price_delta) VALUES (:potion_type_id, :quantity_delta, :price_delta) RETURNING id, potion_type_id, quantity_delta, price_delta")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"potion_type_id": potion_type_id, "quantity_delta": quantity_delta, "price_delta": price_delta}) 
        row = result.fetchone()
        if row is None:
          raise Exception("ERROR: unable to create retail inventory")
        return RetailInventory(row[0], row[1], row[2], row[3]) 
    except Exception as error:
      print("unable to create retail inventory: ", error)
      raise Exception("ERROR: unable to create retail inventory", error)
        

  







    

  

  



      