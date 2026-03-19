from .. import console, traceback

from vlw_lyrics_parser.classes.collection import ParsedResults

from vlw_lyrics_parser.wikitext2html.mediawiki_action_api_parser import render_html
from vlw_lyrics_parser.html2lyrics.parse_to_plaintext import parse
from vlw_lyrics_parser.html2lyrics.utils import get_vocadb_ids

async def pipeline(wikitext: str, json_filepath: str) -> None:
  """
    A pipeline to convert a given portion of wikitext into a structured 
    object containing the parsed lyrics (in plaintext) and finally
    saving the parsed results into a JSON file
  """
  parsed_html, iw_links, external_links = await render_html(wikitext)
  vdb_ids = get_vocadb_ids(iw_links, external_links)
  table_ids, parsed_data, notes = parse(parsed_html)

  res = ParsedResults(
    title="TEST STRING",
    vlw_page_id=0, 
    vdb_ids=vdb_ids, 
    table_ids=table_ids,
    lyrics=parsed_data,
    notes=notes,
  )

  console.print(f"Creating a JSON dump at {json_filepath}", style="magenta")
  try:
    file = open(json_filepath, "w", encoding="UTF-8")
    file.write(res.model_dump_json(indent=2))
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