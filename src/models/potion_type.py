from sqlalchemy import text
from src import database as db



class PotionType:
  table_name = "potion_type"
  def __init__(self, id: int , name: str, sku: str, type: list[int], score: int):
    self.id = id
    self.name = name
    self.sku = sku
    self.type = type
    self.score = score

  @staticmethod
  def get_all() -> list["PotionType"]:
    try:
      sql_to_execute = text(f"SELECT id, name, sku, type, score FROM {PotionType.table_name} ORDER BY score DESC")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute)
        rows = result.fetchall()
        potion_types: list[PotionType] = []
        for row in rows:
          potion_types.append(PotionType(row[0], row[1], row[2], row[3], row[4]))
        return potion_types
    except Exception as error:
      print("unable to get potion types: ", error)
      raise Exception("ERROR: unable to get potion types", error)
    


  @staticmethod
  def reset():
    try:
      sql_to_execute = text(f"DELETE FROM {PotionType.table_name}")
      with db.engine.begin() as connection:
        connection.execute(sql_to_execute)
      return "OK"
    except Exception as error:
      print("unable to reset resize types: ", error)
      raise Exception("ERROR: unable to reset resize types", error)


  @staticmethod
  def create(name: str, sku: str, type: list[int], score: int ) -> "PotionType":
    try:
      potion_type = None
      sql_to_execute = text(f"INSERT INTO {PotionType.table_name} (name, sku, type, score) VALUES (:name, :sku, :type, :score) RETURNING id, name, sku, type, score")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"name": name, "sku": sku, "type": type, "score": score})
        row = result.fetchone()
        potion_type = PotionType(row[0], row[1], row[2], row[3], row[4])
      return potion_type
    except Exception as error:
      print("unable to create resize type: ", error)
      raise Exception("ERROR: unable to create resize type", error)
  
  @staticmethod
  def find(id: int):
    try:
      sql_to_execute = text(f"SELECT id, name, sku, type, score FROM {PotionType.table_name} WHERE id = :id")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"id": id})
        row = result.fetchone()
        return PotionType(row[0], row[1], row[2], row[3], row[4])
    except Exception as error:
      print("unable to find resize type: ", error)
      raise Exception("ERROR: unable to find resize type", error)

  @staticmethod
  def find_by_sku(sku: str):
    try:
      sql_to_execute = text(f"SELECT id, name, sku, type, score FROM {PotionType.table_name} WHERE sku = :sku")
      with db.engine.begin() as connection:
        result = connection.execute(sql_to_execute, {"sku": sku})
        row = result.fetchone()
        return PotionType(row[0], row[1], row[2], row[3], row[4])
    except Exception as error:
      print("unable to find resize type: ", error)
      raise Exception("ERROR: unable to find resize type", error)


