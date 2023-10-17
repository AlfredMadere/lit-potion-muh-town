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
  potion_price = 50 
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
    # Use a single SQL query to fetch all rows from the current_catalog view
    sql_to_execute = text('SELECT potion_type, potion_name, potion_sku, price, available_quantity FROM "current_catalog" WHERE available_quantity > 0 LIMIT 6')
    inventory = []
    
    with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute)
        rows = result.fetchall()
        
        for row in rows:
            inventory.append({
                'sku': row[2],
                'name': row[1],
                'quantity': min(row[4], 2), #limiting to selling two at a time to avoid this weird bullshit issue 
                'price': row[3],
                'potion_type': row[0]
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
      with db.engine.begin() as connection:
        for potion in potions_delivered:
          #insert a row into the retail_inventory table with the same type as the potion delivered and the quantity_delta equal to the quantity of the potion delivered. the price_delta should be equal to the difference between the price of the potion as seen in the current_catalog view and the RetailInventory.potion_price
          retail_inventory_query = text("""
                    INSERT INTO retail_inventory (potion_type_id, quantity_delta, price_delta)
                    SELECT pt.id, :quantity_delta, 
                        :new_potion_price - COALESCE((SELECT price FROM "current_catalog" WHERE potion_type = pt.type), :new_potion_price)
                    FROM potion_type pt
                    WHERE pt.type = :potion_type
                """)
          connection.execute(retail_inventory_query, {'potion_type': potion.potion_type, 'quantity_delta': potion.quantity, 'new_potion_price': RetailInventory.potion_price})

          wholesale_adjustment_rows = []
          for i, ml in enumerate(potion.potion_type):
            if ml > 0:
                #FIXME: collapse into one query if this takes too long 
                barrel_type_to_subtract_from = [0, 0, 0, 0]
                barrel_type_to_subtract_from[i] = 1 if ml != 0 else 0
                wholesale_adjustment_rows.append({"sku": "MIXING", "type": barrel_type_to_subtract_from, "num_ml_delta": potion.quantity * ml * -1})
                wholesale_inventory_query = text("""
                        INSERT INTO wholesale_inventory (sku, type, num_ml_delta)
                        VALUES ('MIXING', :type, :num_ml_delta)
                    """)
                connection.execute(wholesale_inventory_query, {'type': barrel_type_to_subtract_from, 'num_ml_delta': ml * potion.quantity * -1})  # Assuming ml_needed is the amount of ml needed for this type
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


  # @staticmethod
  # def items_available(items: list[CartItemM]):
  #   inventory = RetailInventory.get_inventory()

  #   for item_sku, quantity in items.items():
  #     print("Inventory:", [item.sku for item in inventory])
  #     print("Looking for SKU:", item_sku)
  #     print("Type of SKUs in inventory:", [type(item.sku) for item in inventory])
  #     print("Type of target SKU:", type(item_sku))


  #     #get the inventory item with the same sku as the item_sku
  #     inventory_item = None
  #     for item in inventory:
  #       print("item.sku:", item.sku)
  #       print("item_sku:", item_sku)
  #       if f'{item.sku.strip()}' == f'{item_sku.strip()}':
  #         inventory_item = item
  #         break      
  #     print ("inventory item: ", inventory_item)
  #     if( inventory_item is None):
  #       raise Exception("Item not found")
  #     if inventory_item.quantity < quantity:
  #       raise Exception("Not enough items available")
  #   return True  
  

  def num_potion_type_available(id: int):
    try:
       sql_to_execute = text(f"SELECT quantity_delta FROM {RetailInventory.table_name} WHERE potion_type_id = :potion_type_id")
       total_potions = 0
       with db.engine.begin() as connection:
         result = connection.execute(sql_to_execute, {"potion_type_id": id})
         rows = result.fetchall()
         for row in rows:
           total_potions += row[0] 
       return total_potions
    except Exception as error:
      print("unable to get resize stock: ", error)
      raise Exception("ERROR: unable to get resize stock", error)

  #FIXME: hardcoded potion price 
  @staticmethod
  def adjust_inventory(items: list[CartItemM]):
    try:
        total_gold_paid = 0
        total_potions_bought = 0

        with db.engine.begin() as connection:
            for item in items:
                # Check available inventory
                sql_check_inventory = text(f"""
                    SELECT SUM(quantity_delta) as available_inventory
                    FROM {RetailInventory.table_name}
                    WHERE potion_type_id = :potion_type_id
                """)
                result = connection.execute(sql_check_inventory, {"potion_type_id": item.potion_type_id})
                available_inventory = result.fetchone()[0]

                if available_inventory < item.quantity:
                    raise Exception(f"Insufficient inventory for potion_type_id {item.potion_type_id}")

                # Update inventory
                potion_price = RetailInventory.get_potion_price(item.potion_type_id)
                total_gold_paid += potion_price * item.quantity
                total_potions_bought += item.quantity

                sql_to_execute = text(f"""
                    INSERT INTO {RetailInventory.table_name} (potion_type_id, quantity_delta, price_delta)
                    VALUES (:potion_type_id, :quantity_delta, :price_delta)
                    RETURNING id, potion_type_id, quantity_delta, price_delta
                """)
                connection.execute(sql_to_execute, {"potion_type_id": item.potion_type_id, "quantity_delta": item.quantity * -1, "price_delta": 0})

        return {"total_potions_bought": total_potions_bought, "total_gold_paid": total_gold_paid}

    except Exception as e:
        raise Exception(f"Could not adjust inventory: {str(e)}")


  
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
        

  







    

  

  



      