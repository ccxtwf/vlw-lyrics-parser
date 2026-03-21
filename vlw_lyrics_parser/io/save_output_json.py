from .. import console, traceback, JSON_INDENTATION
from ..classes.types import TParsedResults

from pydantic import TypeAdapter

from typing import List, Optional

def save_lyrics_json(json_filepath: str, batch_results: List[TParsedResults]):
  """
    Save the parsed lyrics to a JSON file
  """
  try:
    console.print(f"Creating a JSON dump at {json_filepath}", style="magenta")
    json_string = TypeAdapter(List[TParsedResults]).dump_json(batch_results, indent=JSON_INDENTATION)
    with open(json_filepath, "w", encoding="UTF-8") as file:
      file.write(json_string.decode('utf-8'))
  
  except Exception:
    console.print(
      f"Failed to save the parsed lyrics to the JSON file. Got the following error: ", 
      traceback.format_exc(), 
      sep="\n", 
      style="red"
    )
    raise
