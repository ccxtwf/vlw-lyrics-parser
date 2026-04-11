from .. import console, traceback, JSON_INDENTATION
from ..classes.collection import ParsedResults

from pydantic import TypeAdapter

from typing import List, Any

def save_lyrics_json(json_filepath: str, batch_results: List[ParsedResults[Any]]) -> None:
  """
    Save the parsed lyrics to a JSON file.

    This method is an agnostic implementation, meaning that each 
    `ParsedResults[T]` object being passed into this method is 
    responsible for correctly implementing the serialization of 
    its lyrics via its `lyrics` (type: *Dict&lt;[column ID], [string]&gt;*) 
    field. Therefore this method does not make any assumptions on 
    how the lyrics may be represented (in string format) when 
    extracted in raw form from the `ParsedResults[T]`'s `data` 
    (type: *Dict&lt;[column ID], [List&lt;T>]&gt;*) field.

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
