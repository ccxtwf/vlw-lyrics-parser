from .. import console, traceback, JSON_INDENTATION

from ..classes.collection import ParsedResults
from ..classes.types import OutputFileFormat

from typing import Callable, Coroutine, Any

async def pipeline(
    wikitext: str, 
    transformer: Callable[[str], Coroutine[Any, Any, ParsedResults]],
    json_filepath: str | None = None, 
    output_format: OutputFileFormat = 'console',
  ) -> None:
  """
    A pipeline to convert a given portion of wikitext into a structured 
    object containing the parsed lyrics and finally saving the parsed 
    results into a JSON file.
  """

  if output_format == 'json' and json_filepath is None:
    console.print(f"A JSON filepath has to be specified! Switching to output_format = 'console'", style="red")
    output_format = 'console'
  elif json_filepath is not None and output_format != 'json':
    output_format = 'json'

  res = await transformer(wikitext)

  if output_format == 'json':
    console.print(f"Creating a JSON dump at {json_filepath}", style="magenta")
    try:
      assert(json_filepath is not None)
      file = open(json_filepath, "w", encoding="UTF-8")
      file.write(res.model_dump_json(indent=JSON_INDENTATION))
      console.print(f"Created JSON dump at {json_filepath}", style="green")
    except Exception:
      console.print(
        f"Failed to save the parsed lyrics to the JSON file. Got the following error: ", 
        traceback.format_exc(), 
        sep="\n", 
        style="red"
      )
    finally:
      file.close()
  
  else:
    console.print(res.model_dump_json(indent=JSON_INDENTATION))