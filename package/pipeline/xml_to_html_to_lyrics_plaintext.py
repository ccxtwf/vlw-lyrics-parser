import xml.etree.ElementTree as ET
import asyncio

from .. import console, traceback, getenv
from ..classes.collection import ParsedResults

from ..io.read_xml_dump import read_dump, get_page_contents, get_page_properties
from ..io.save_output_sqlite import save_lyrics
from ..wikitext2html.mediawiki_action_api_parser import render_html
from ..html2lyrics.utils import get_vocadb_ids
from ..html2lyrics.parse_to_plaintext import parse_lyrics

from typing import Optional, Tuple

XML_DEFINITION = getenv("DUMP_XML_DEFINITION")

async def pipeline(xml_dump_file_path: str, sqlite_db_file_path: str) -> None:
  """
    A pipeline to convert/parse several wiki pages (in the format of a MediaWiki XML dump)
    into HTML, then into a structured object containing the parsed lyrics (in plaintext), 
    and finally saving the parsed results into a SQLITE database 
  """
  MAX_PAGES_TO_UNPACK = getenv("DUMP_UNPACK_MAX_NUMBER_OF_PAGES") or "10"

  async def treat_batch(batch: Tuple[ET.Element, ...]) -> None:
    """
      Async handler to parallelize several separate coroutines (one per page) for each batch
    """
    waitTasks = asyncio.gather(
      *map(lambda page_contents: treat_page(page_contents), batch),
      return_exceptions=False
    )
    await waitTasks
    batch_results = waitTasks.result()
    save_lyrics(sqlite_db_file_path, batch_results)

  await read_dump(
    xml_dump_file_path, 
    max_pages_to_unpack_at_a_time=int(MAX_PAGES_TO_UNPACK), 
    batch_callback=treat_batch
  )

async def treat_page(node: ET.Element) -> Optional[ParsedResults]:
  """
    Coroutine for each individual page
  """
  try:
    title, page_id = get_page_properties(node)
    page_contents = get_page_contents(node)
    parsed_html, iw_links, external_links = await render_html(page_contents)
    vdb_ids = get_vocadb_ids(iw_links, external_links)
    lyrics = parse_lyrics(parsed_html)

    res = ParsedResults(
      title=title, # type: ignore
      vlw_page_id=page_id, 
      vdb_ids=vdb_ids, 
      lyrics=lyrics
    )
    return res
  
  except Exception:
    console.print(
      f"Failed to treat the page \"{title}\". Got the following error: ", 
      traceback.format_exc(), 
      sep="\n", 
      style="red"
    )
    return None