import json
import os
def load_fixture(file_name: str) -> str:
  file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fixtures', file_name)
  print("file path: ", file_path)
  with open(file_path) as file:
    data = json.load(file)
    json_string = json.dumps(data)
    return json_string
