from .. import console, traceback
from ..classes.collection import ParsedResults

from pydantic import TypeAdapter

from typing import List, Optional

def save_lyrics_json(json_filepath: str, batch_results: List[Optional[ParsedResults]]):
  """
    Save the parsed lyrics to a JSON file
  """
  try:
    console.print(f"Creating a JSON dump at {json_filepath}", style="magenta")
    filtered_results = [res for res in batch_results if res is not None]
    json_string = TypeAdapter(List[ParsedResults]).dump_json(filtered_results, indent=2)
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
