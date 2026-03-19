import aiohttp

from .. import console, traceback, getenv
from ..classes.exceptions import ReadMediawikiException

from typing import Tuple, List

MEDIAWIKI_ACTION_API_ENTRYPOINT = getenv("MEDIAWIKI_ACTION_API_ENTRYPOINT") or "http://localhost:8080/api.php"

async def render_html(page_contents: str) -> Tuple[str, List[str], List[str]]:
  """
    A wikitext-to-HTML parser that works by calling upon the MediaWiki Action API 

    API Reference:
    https://www.mediawiki.org/wiki/API:Parsing_wikitext
  """
  try:
    headers = {
      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    payload = {
      "action": "parse",
      "format": "json",
      "text": page_contents,
      "contentmodel": "wikitext",
      "disableeditsection": "true",
      "disablelimitreport": "true",
      # "prop": "text|categories|sections|iwlinks|externallinks",
      # "prop": "text",
      "prop": "text|iwlinks|externallinks",
    }
    data = aiohttp.FormData(charset="utf-8")
    for k,v in payload.items():
      data.add_field(k, v)
    async with aiohttp.ClientSession() as session:
      async with session.post(
        MEDIAWIKI_ACTION_API_ENTRYPOINT, 
        headers=headers, 
        data=data
      ) as response:
        data = await response.json()
        if "error" in data:
          raise ReadMediawikiException(data["error"]["info"])
        parsed_html_string: str = data["parse"]["text"]["*"]

        """
        This may be used to get the position of each heading
        """
        #sections: List[Tuple[str, str]] = [(o["line"], o["linkAnchor"]) for o in data["parse"].get("sections", [])]

        """
        Can be used to parse additional information
        Example output: 
        Categories: "Japanese songs", "Mandarin songs"
        """
        #categories: List[str] = [o["*"] for o in data["parse"].get("categories", [])]

        """
        Can be used to parse links pointing to VocaDB
        Example output:
        iwlinks: "vdb:S/242985"
        externallinks: "https://vocadb.net/S/242985"
        """
        iw_links: List[str] = [o["*"] for o in data["parse"].get("iwlinks", []) if o["prefix"] == "vdb"]
        external_links: List[str] = data["parse"].get("externallinks", [])
        
        # return (parsed_html_string, sections, categories, iwlinks, externallinks)
        return (parsed_html_string, iw_links, external_links)
      
  except Exception:
    console.print(
      "Failed to get a response from the MediaWiki API. Got error: ",
      traceback.format_exc(),
      sep="\n", 
      style="red"
    )
    raise