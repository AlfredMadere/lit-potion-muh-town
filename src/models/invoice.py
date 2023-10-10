

from sqlalchemy import text
from src import database as db
class Invoice:
  table_name = "invoice"
  def __init__(self, id: int , wholesale_inventory_id: int , cart_id: int, description: str):
    self.id = id
    self.wholesale_inventory_id = wholesale_inventory_id
    self.cart_id = cart_id
    self.description = description


  @staticmethod
  def create(wholesale_inventory_id: int | None , cart_id: int | None, description: str) -> "Invoice":
    try:
      sql_to_execute = text(f"INSERT INTO {Invoice.table_name} (wholesale_inventory_id, cart_id, description) VALUES (:wholesale_inventory_id, :cart_id, :description) RETURNING id, wholesale_inventory_id, cart_id, description")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"wholesale_inventory_id": wholesale_inventory_id, "cart_id": cart_id, "description": description})
        row = result.fetchone()
        if row is None:
          raise Exception("ERROR: unable to create invoice")
        return Invoice(row[0], row[1], row[2], row[3])
    except Exception as error:
      print("unable to create invoice: ", error)
      raise Exception("ERROR: unable to create invoice", error)


  @staticmethod
  def reset():
    try:
      sql_to_execute = text(f"DELETE FROM {Invoice.table_name}")
      with db.engine.begin() as connection:
        connection.execute(sql_to_execute)
      return "OK"
    except Exception as error:
        print("unable to reset invoice: ", error)
        raise Exception("ERROR: unable to reset invoice", error)
