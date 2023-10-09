from sqlalchemy import text
from src import database as db



class PotionType:
  table_name = "potion_type"
  def constructor(self, id: int , name: str, sku: str, type: list[int], score: int):
    self.id = id
    self.name = name
    sku = sku
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