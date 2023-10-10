from sqlalchemy.sql import text
from src import database as db
class Customer:
  table_name = "customer"
  def __init__(self, id: int, str: str):
    self.id = id
    self.str = str 

  @staticmethod
  def upsert(customer_str: str):
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

