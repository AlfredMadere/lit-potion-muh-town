from sqlalchemy import text
from src import database as db
# from .retail_inventory import RetailInventory
from .potion_type import PotionType
from sqlalchemy import create_engine, MetaData, Table, select, desc, asc, and_, or_, func



def encrypt(cursor: str) -> str:
    # Your encryption logic here
    return cursor

def decrypt(token: str) -> str:
    # Your decryption logic here
    return token 


class CartItemM:
  table_name = "cart_item"
  def __init__(self, id: int, cart_id: int, potion_type_id: int, quantity: int):
    self.id = id
    self.cart_id = cart_id
    self.potion_type_id = potion_type_id
    self.quantity = quantity
    self.potion_type = None

  @staticmethod
  def create(cart_id: int, potion_type_id: int, quantity: int):
    try:
      sql_to_execute = text(f"INSERT INTO {CartItemM.table_name} (cart_id, potion_type_id, quantity) VALUES (:cart_id, :potion_type_id, :quantity)")
      with db.engine.begin() as connection:
        connection.execute(sql_to_execute, {"cart_id": cart_id, "potion_type_id": potion_type_id, "quantity": quantity})
    except Exception as error:
      print("unable to create cart item: ", error)
      raise Exception("ERROR: unable to create cart item", error)


 #Depricated
  def is_available(self, catalog: list):
    try:
      self.get_potion_type()
      catalog_potion = next((potion for potion in catalog if potion["potion_type"] == self.potion_type.type), None)
      if catalog_potion is None:
        raise Exception("ERROR: unable to check if item is available because we didn't find it in the catalog")
      if self.quantity <= catalog_potion["quantity"]:
        return False
      else:
        return True
    except Exception as error:
      print("unable to check if item is available: ", error)
      raise Exception("ERROR: unable to check if item is available", error)

  def get_potion_type(self):
    try:
      potion_type = PotionType.find(self.potion_type_id)
      self.potion_type = potion_type
      return self.potion_type 
    except Exception as error:
      print("unable to get potion type: ", error)
      raise Exception("ERROR: unable to get potion type", error)
    

  def get_item_string(self):
    try:
      self.get_potion_type()
      generated_string = f"ITEM: id: '{self.id}', \n POTION_TYPE: quantity: {self.quantity}, name: '{self.potion_type.name}', type: {self.potion_type.type}"
      return generated_string
    except Exception as error:
      print("unable to get item string: ", error)
      raise Exception("ERROR: unable to get item string", error)


  @staticmethod
  def reset():
    try:
      sql_to_execute = text(f"DELETE FROM {CartItemM.table_name}")
      with db.engine.begin() as connection:
        connection.execute(sql_to_execute)
      return "OK"
    except Exception as error:
      print("unable to reset cart item: ", error)
      raise Exception("ERROR: unable to reset cart item", error)

  @staticmethod
  def search(customer_name: str, potion_sku: str, search_page: str, sort_col: str, sort_order: str):
    page_size = 5
    try:
      offset = 0
      if (search_page != ""):
        offset = int(search_page)
      metadata = MetaData()
      order = Table('order', metadata, autoload_with=db.engine)

      order_by_column = {
        'customer_name': order.c.customer_name, 
        'item_sku': order.c.potion_sku,
        'line_item_total': order.c.line_item_total,
        'timestamp': order.c.created_at
      }.get(sort_col)

      sort_func = asc if sort_order == 'asc' else desc
      
    
      stmt = (
          select(order.c.line_item_id, order.c.potion_sku, order.c.customer_name,  order.c.line_item_total, order.c.created_at)
          .limit(page_size)
          .order_by(sort_func(order_by_column)).offset(offset)
      )

      if customer_name != "":
          stmt = stmt.where(order.c.customer_name.ilike(f"%{customer_name}%"))
      
      if potion_sku != "":
          stmt = stmt.where(order.c.potion_sku.ilike(f"%{potion_sku}%"))


      # if cursor_value and cursor_id:
      #     operator = and_ if sort_order == 'asc' else or_
      #     stmt = stmt.where(
      #         operator(
      #             order_by_column > cursor_value if sort_order == 'asc' else order_by_column < cursor_value,
      #             and_(order_by_column == cursor_value, order.c.id > cursor_id if sort_order == 'asc' else order.c.id < cursor_id)
      #         )
      #     )
    
      results = []
      prev_cursor, next_cursor = None, None

      with db.engine.connect() as conn:
          result = conn.execute(stmt)
          
          for row in result:
              results.append({
                  "line_item_id": row[0],
                  "item_sku": row[1],
                  "customer_name": row[2],
                  "line_item_total": row[3],
                  "timestamp": row[4],
              })

          count_stmt = select(func.count()).select_from(order)
          total_records = conn.execute(count_stmt).scalar()

          if results:
              next_cursor = f'{offset + page_size }'
              if (offset + page_size) >= total_records:
                next_cursor = None
              prev_cursor = f'{offset - page_size if offset - page_size > 0 else 0}'

          
      return {
          "previous": prev_cursor,
          "next": next_cursor,
          "results": results
      }
    except Exception as error:
      print("unable to search cart items: ", error)
      raise Exception("ERROR: unable to search cart items", error)