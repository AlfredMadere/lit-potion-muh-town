from .transaction import Transaction
from sqlalchemy.sql import text
from src import database as db
import math
from threading import Lock
import json
from pydantic import BaseModel

lock = Lock()

class Barrel(BaseModel):
    sku: str
    ml_per_barrel: int
    potion_type: list[int]
    price: int
    quantity: int

class WholesaleInventory:
  #TODO: update this template code
  table_name = "wholesale_inventory"
  def __init__(self, id, sku, type, num_ml):
    self.id = id
    self.sku = sku
    self.type = type
    self.num_ml = num_ml

  @staticmethod
  def get_bottler_plan():
    try:
      red_stock = WholesaleInventory.get_stock([1, 0, 0, 0])
      green_stock = WholesaleInventory.get_stock([0, 1, 0, 0])
      blue_stock = WholesaleInventory.get_stock([0, 0, 1, 0])
      bottler_plan = []
      max_red_potions = math.floor(red_stock / 100)
      max_green_potions = math.floor(green_stock / 100)
      max_blue_potions = math.floor(blue_stock / 100)

      if (max_red_potions > 0): 
        bottler_plan.append({
        "potion_type": [100, 0, 0, 0],
        "quantity": min(max_red_potions, 1)
        }) 
      if (max_green_potions > 0):
        bottler_plan.append({
        "potion_type": [0, 100, 0, 0],
        "quantity": min(max_green_potions, 1)
        })
      if (max_blue_potions > 0):
        bottler_plan.append({
        "potion_type": [0, 0, 100, 0],
        "quantity": min(max_blue_potions, 1)
        })
      return bottler_plan
    except Exception as error:
        print("unable to get bottler plan: ", error)
        return "ERROR"

  @staticmethod
  def get_wholesale_plan(wholesale_catalog: list[Barrel]):
    #TODO: update this to the following strategy:
    # 1. If there is a barel type that i don't have at least 50ml, and i have enough gold to buy it, then buy it.
    wholesale_plan = []
    available_balance = Transaction.get_current_balance()
    current_wholesale_materials = {}
    for catalog_item in wholesale_catalog:
      hashable_potion_type = "_".join(map(str, catalog_item.potion_type))
      potion_stock = WholesaleInventory.get_stock(catalog_item.potion_type)
      current_wholesale_materials[hashable_potion_type] = potion_stock
      if (catalog_item.price <= available_balance and catalog_item.potion_type != [0, 0, 0, 1]):
        available_balance -= catalog_item.price
        current_wholesale_materials[hashable_potion_type] = catalog_item.ml_per_barrel
        wholesale_plan.append({
          "sku": catalog_item.sku,
          "quantity": 1
        })
    return wholesale_plan

  @staticmethod
  def get_stock(potion_type: list[int]):
    try:
      sql_to_execute = text(f"SELECT num_ml FROM {WholesaleInventory.table_name} WHERE type = :type")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"type": potion_type})
        rows = result.fetchall()
        total_ml = 0
        for row in rows:
          total_ml += row[0]
        return total_ml
    except Exception as error:
        print("unable to get potion stock: ", error)
        return "ERROR"
    
  @staticmethod
  def accept_barrels_delivery (barrels_delivered: list[Barrel]):
    try:
      with lock:
        for barrel in barrels_delivered:
          #FIXME: issue with 
          if (barrel.price * barrel.quantity > Transaction.get_current_balance()):
              print("not enough gold to pay for delivery, may have processed a partial delivery")
              return "ERROR"
          response = WholesaleInventory.add_to_inventory(barrel)
          if (response == "ERROR"):
            return "ERROR"
          delta = barrel.quantity * barrel.price * -1
          Transaction.create(None, delta, f'payment of {delta} for delivery of {barrel.quantity} {barrel.sku} barrels of type {barrel.potion_type}') #flush this out

      return "OK"
    except Exception as error:
        print("unable to accept barrel delivery things may be out of sync due to no roleback: ", error)
        return "ERROR"
    
  def add_to_inventory(barrel: Barrel):
    #FIXME: figure out how the fuck to do error handling in python, this thing swallows hella errors
    #FIXME: sku means nothing here, its really most recent sku, should prob be generating sku from type
    try:
      sql_to_execute = text(f"SELECT * FROM {WholesaleInventory.table_name} WHERE sku = :sku")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"sku": barrel.sku}).fetchone()
        if(result == None):
          sql_to_execute = text(f"INSERT INTO {WholesaleInventory.table_name} (sku, type, num_ml) VALUES (:sku, :type, :num_ml)")
          connection.execute(sql_to_execute, {"sku": barrel.sku, "type": barrel.potion_type, "num_ml": barrel.quantity * barrel.ml_per_barrel})
        else:
          sql_to_execute = text(f"UPDATE {WholesaleInventory.table_name} SET num_ml = num_ml + :num_ml WHERE sku = :sku")
          connection.execute(sql_to_execute, {"sku": barrel.sku, "num_ml": barrel.quantity * barrel.ml_per_barrel})
      return 'OK'
    except Exception as error:
        print("unable to add to inventory: ", error)
        return "ERROR"
    
  
  @staticmethod
  def reset():
    try:
      sql_to_execute = text(f"DELETE FROM {WholesaleInventory.table_name}")
      with db.engine.begin() as connection:
        connection.execute(sql_to_execute)
      return "OK"
    except Exception as error:
        print("unable to reset wholesale inventory: ", error)
        return "ERROR"

  @staticmethod
  def use_potion_inventory(potion_type: list[int], quantity: int):
    try:
        for i, ml in enumerate(potion_type):
            if ml > 0:
                # Find the record with the corresponding potion type
                #construct a 
                barrel_type_to_subtract_from = [0, 0, 0, 0]
                barrel_type_to_subtract_from[i] = 1 if ml != 0 else 0
                potion_type_stock = WholesaleInventory.get_stock(barrel_type_to_subtract_from) 
                if (potion_type_stock < quantity * ml):
                    raise Exception(f"Not enough {barrel_type_to_subtract_from} ml potion in inventory for {quantity} potions of type {potion_type}")
                sql_to_execute = text(f"SELECT id, num_ml FROM {WholesaleInventory.table_name} WHERE type = :type")
                with db.engine.begin() as connection:
                    result = connection.execute(sql_to_execute, {"type": barrel_type_to_subtract_from}).fetchall()
                    amount_left_to_subtract = quantity * ml
                    for row in result:
                      if row[1] >= quantity * ml:
                        sql_to_execute = text(f"UPDATE {WholesaleInventory.table_name} SET num_ml = num_ml - :num_ml WHERE id = :id")
                        connection.execute(sql_to_execute, {"num_ml": amount_left_to_subtract, "id": row[0]})
                        amount_left_to_subtract = 0
                        break
                      sql_to_execute = text(f"UPDATE {WholesaleInventory.table_name} SET num_ml = 0 WHERE id = :id")
                      connection.execute(sql_to_execute, {"id": row[0]})
                      amount_left_to_subtract -= row[1]
                    if amount_left_to_subtract > 0:
                      raise Exception(f"This error should not be thrown unless there is a race condition causing wholesale inventory to change in the middle of this call")
        return "OK"
    except Exception as error:
        print("unable to use potion inventory: ", error)
        raise

 
  



    
   
  
