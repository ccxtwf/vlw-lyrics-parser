from .. import console, traceback, JSON_INDENTATION

from vlw_lyrics_parser.classes.collection import ParsedResultsPlaintext

from vlw_lyrics_parser.wikitext2html.mediawiki_action_api_parser import render_html
from vlw_lyrics_parser.html2lyrics.parse_to_plaintext import parse_to_plaintext
from vlw_lyrics_parser.html2lyrics.utils import get_vocadb_ids

from typing import Literal

async def pipeline(
    wikitext: str, 
    lyrics_format: Literal['plaintext'] = 'plaintext',
    json_filepath: str | None = None, 
    output_format: Literal['json', 'console'] = 'console',
  ) -> None:
  """
    A pipeline to convert a given portion of wikitext into a structured 
    object containing the parsed lyrics (in plaintext) and finally
    saving the parsed results into a JSON file
  """
  if lyrics_format != 'plaintext':
    raise NotImplementedError

  if output_format == 'json' and json_filepath is None:
    console.print(f"A JSON filepath has to be specified! Switching to output_format = 'console'", style="red")
    output_format = 'console'
  elif json_filepath is not None and output_format != 'json':
    output_format = 'json'

  parsed_html, iw_links, external_links = await render_html(wikitext)
  vdb_ids = get_vocadb_ids(iw_links, external_links)
  table_ids, parsed_data, notes = parse_to_plaintext(parsed_html)

  res = ParsedResultsPlaintext(
    title="TEST STRING",
    vlw_page_id=0, 
    vdb_ids=vdb_ids, 
    table_ids=table_ids,
    lyrics=parsed_data,
    notes=notes,
  )

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
    print(res.model_dump_json(indent=JSON_INDENTATION))