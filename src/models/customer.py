from sqlalchemy.sql import text
from src import database as db
class Customer:
  table_name = "customer"
  def __init__(self, id: int, str: str):
    self.id = id
    self.str = str 

  @staticmethod
  def upsert(customer_str: str) -> "Customer":
    try: 
      sql_to_execute = text(f'SELECT id, str FROM {Customer.table_name} WHERE str = :customer_str')
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"customer_str": customer_str})
        row = result.fetchone()
        if row is not None:
          return Customer(row[0], row[1])
        else:
          sql_to_execute = text(f"INSERT INTO {Customer.table_name} (str) VALUES (:customer_str) RETURNING id, str")
          result = connection.execute(sql_to_execute, {"customer_str": customer_str})
          row = result.fetchone()
          return Customer(row[0], row[1])
    except Exception as error:
      print("unable to upsert customer: ", error)
      raise Exception("ERROR: unable to upsert customer", error)

  
  @staticmethod
  def reset():
    try:
      sql_to_execute = text(f"DELETE FROM {Customer.table_name}")
      with db.engine.begin() as connection:
        connection.execute(sql_to_execute)
      return "OK"
    except Exception as error:
      print("unable to reset customer table: ", error)
      raise Exception("ERROR: unable to reset customer table", error)
  

  @staticmethod
  def find(id: int) -> "Customer":
    try:
      sql_to_execute = text(f"SELECT id, str FROM {Customer.table_name} WHERE id = {id}")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute)
        row = result.fetchone()
        if row is None:
          raise Exception("Customer not found")
        return Customer(row[0], row[1])
    except Exception as error:
      print("unable to find customer: ", error)
      raise Exception("ERROR: unable to find customer", error)