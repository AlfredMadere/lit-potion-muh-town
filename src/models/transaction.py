from sqlalchemy import text
from src import database as db
class Transaction: 
  table_name = "transaction"

  #TODO: update template code
  def __init__(self, id, debit_credit: int, invoice_id, created_at):
    self.id = id
    self.debit_credit = debit_credit
    self.invoice_id = invoice_id

    self.created_at = created_at

  @staticmethod
  def get_current_balance():
    #FIXME: update to create an invoice for initial transaction
    current_balance = 0
    sql_to_execute = text(f"SELECT id, debit_credit FROM {Transaction.table_name}")
    with db.engine.begin() as connection:
      result = connection.execute(sql_to_execute)
      rows = result.fetchall()
      for row in rows:
        current_balance += row[1]
      if rows is None or rows == [] :
        sql_to_execute = text(f"INSERT INTO {Transaction.table_name} (debit_credit) VALUES (100)")
        result = connection.execute(sql_to_execute)
        current_balance = 100
    return current_balance


  @staticmethod
  def create(debit_credit: int, invoice_id: int):
    try:
      sql_to_execute = text(f"INSERT INTO {Transaction.table_name} (debit_credit, invoice_id) VALUES (:debit_credit, :invoice_id)")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"debit_credit": debit_credit, "invoice_id": invoice_id})
      return "OK"
    except Exception as error:
      print("unable to create transaction: ", error)
      return "ERROR"
    

  @staticmethod
  def reset():
    try:
      sql_to_execute = text(f"DELETE FROM {Transaction.table_name}")
      with db.engine.begin() as connection:
        connection.execute(sql_to_execute)
      return "OK"
    except Exception as error:
        print("unable to reset retail inventory: ", error)
        return "ERROR"

      

