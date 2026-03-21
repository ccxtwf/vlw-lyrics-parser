from .. import console, traceback, JSON_INDENTATION
from ..classes.collection import ParsedResults

from pydantic import TypeAdapter

from typing import List, Any

def save_lyrics_json(json_filepath: str, batch_results: List[ParsedResults[Any]]) -> None:
  """
    Save the parsed lyrics to a JSON file.

    Parameters:
        json_filepath (str):
        batch_results (List[ParsedResults[Any]]):
  """
  try:
    console.print(f"Creating a JSON dump at {json_filepath}", style="magenta")
    json_string = TypeAdapter(List[ParsedResults[Any]]).dump_json(batch_results, indent=JSON_INDENTATION)
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
