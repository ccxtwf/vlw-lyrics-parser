from ..classes.collection import ParsedResults
from ..classes.types import LyricFormat

from ..transformers.wikitext2html import mediawiki_action_api_parser
from ..transformers.html2lyrics import index as html2lyrics
from ..transformers.html2lyrics.utils import get_vocadb_ids
from ..transformers.wikitext2lyrics import index as wikitext2lyrics

from typing import Callable, Coroutine, Any

class TransformerUtils:

  @staticmethod
  def test_string_to_lyrics(lyrics_format: LyricFormat, use_experimental_wtp: bool = False) -> Callable[[str], Coroutine[Any, Any, ParsedResults]]:
    if use_experimental_wtp:
      async def fn(wikitext: str) -> ParsedResults:
        res = wikitext2lyrics.parse(
          title="TEST STRING", 
          page_id=0,
          contents=wikitext, 
          lyrics_format=lyrics_format
        )
        return res
    
      return fn
    
    else:
    
      async def fn(wikitext: str) -> ParsedResults:
        parsed_html, iw_links, external_links, categories = await mediawiki_action_api_parser.render_html(wikitext)
        vdb_ids = get_vocadb_ids(iw_links, external_links)

        table_ids, parsed_data, notes = html2lyrics.parse(parsed_html, lyrics_format)

        res = ParsedResults(
          title="TEST STRING",
          vlw_page_id=0, 
          vdb_ids=vdb_ids, 
          categories=categories,
          table_ids=table_ids,
          lyrics=parsed_data,
          notes=notes,
        )

        return res
      
      return fn
  
  @staticmethod
  def wikipage_to_lyrics(lyrics_format: LyricFormat, use_experimental_wtp: bool = False) -> Callable[[str, int, str], Coroutine[Any, Any, ParsedResults]]:
    if use_experimental_wtp:
      async def fn(title: str, page_id: int, contents: str) -> ParsedResults:
        res = wikitext2lyrics.parse(title, page_id, contents, lyrics_format)
        return res
    
      return fn
    
    else:
      async def fn(title: str, page_id: int, contents: str) -> ParsedResults:
        parsed_html, iw_links, external_links, categories = await mediawiki_action_api_parser.render_html(contents)
        vdb_ids = get_vocadb_ids(iw_links, external_links)
            
        table_ids, parsed_data, notes = html2lyrics.parse(parsed_html, lyrics_format)
        res = ParsedResults(
          title=title,
          vlw_page_id=page_id, 
          vdb_ids=vdb_ids, 
          categories=categories,
          table_ids=table_ids,
          lyrics=parsed_data,
          notes=notes,
        )
        return res

      return fn