from .. import console, traceback, getenv, JSON_INDENTATION

from vlw_lyrics_parser.classes.collection import ParsedResultsPlaintext

from vlw_lyrics_parser.wikitext2html.mediawiki_action_api_parser import (
  prepare_api_headers, 
  prepare_api_payload, 
  handle_api_response
)
from vlw_lyrics_parser.html2lyrics.parse_to_plaintext import parse_to_plaintext
from vlw_lyrics_parser.html2lyrics.utils import get_vocadb_ids

import requests

import asyncio

from typing import Literal

def pipeline(
    title: str | None = None,
    revid: int | None = None,
    pageid: int | None = None,
    json_filepath: str | None = None, 
    lyrics_format: Literal['plaintext'] = 'plaintext',
    api_entrypoint: str | None = None, 
    output_format: Literal['json', 'console'] = 'console',
    user_agent: str | None = None,
  ) -> None:
  """
    Makes a request to the given MediaWiki API entrypoint (or the entrypoint set on .env if 
    this argument is unspecified), parses the lyrics (in plaintext) and finally
    saves the parsed results into a JSON file
  """
  if lyrics_format != 'plaintext':
    raise NotImplementedError("Can only parse plaintext lyrics")

  if output_format == 'json' and json_filepath is None:
    console.print(f"A JSON filepath has to be specified! Switching to output_format = 'console'", style="red")
    output_format = 'console'

  if api_entrypoint is None:
    api_entrypoint = getenv("MEDIAWIKI_ACTION_API_ENTRYPOINT", "")

  api_headers = prepare_api_headers(user_agent=user_agent)
  api_payload = prepare_api_payload(title=title, pageid=pageid, revid=revid)
  with requests.Session() as session:
    resp = session.get(url=api_entrypoint, headers=api_headers, params=api_payload)
    data = resp.json()
    title_from_api = data["parse"]["title"]
    pageid_from_api = data["parse"]["pageid"]
    parsed_html, iw_links, external_links = handle_api_response(data)

  vdb_ids = get_vocadb_ids(iw_links, external_links)
  table_ids, parsed_data, notes = parse_to_plaintext(parsed_html)

  res = ParsedResultsPlaintext(
    title=title_from_api,
    vlw_page_id=pageid_from_api, 
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