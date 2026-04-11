from lxml import etree
import asyncio

from .. import console, traceback
from ..classes.collection import ParsedResults
from ..classes.types import LyricFormat, MassOutputFileFormat

from ..io.read_xml_dump import read_dump, get_page_contents, get_page_properties
from ..io.save_output_sqlite import save_lyrics_sqlite
from ..io.save_output_json import save_lyrics_json
from ..transformers.wikitext2html.mediawiki_action_api_parser import render_html
from ..transformers.html2lyrics.utils import get_vocadb_ids
from ..transformers.html2lyrics.index import parse
from ..config import (
  MAX_PAGES_TO_UNPACK,
  JSON_DUMP_BATCH_SIZE,
  SQL_INSERT_BATCH_SIZE,
)

from typing import Optional, List, Tuple, Any
from collections.abc import Callable, Coroutine, Awaitable
from os.path import join, exists
import re

async def pipeline(
    xml_dump_file_path: str, 
    output_directory: str, 
    filename: str,
    transformer: Callable[[str, int, str], Coroutine[Any, Any, ParsedResults]],
    lyrics_format: LyricFormat = 'plaintext',
    output_format: MassOutputFileFormat = 'json',
    batch_size: int | None = None,
  ) -> None:
  """
    A pipeline to convert/parse several wiki pages (in the format of a MediaWiki XML dump)
    into HTML, then into a structured object containing the parsed lyrics (in plaintext), 
    and finally saving the parsed results into a SQLITE database or JSON file
  """
  if lyrics_format != 'plaintext':
    raise NotImplementedError("Can only parse plaintext lyrics")

  n = batch_size or __get_batch_size(output_format)
  q = asyncio.Queue(n)
  
  _tb = __treat_batch(
    transformer=transformer,
    queue=q
  )

  producer = asyncio.create_task(
    read_dump(
      xml_dump_file_path, 
      max_pages_to_unpack_at_a_time=int(MAX_PAGES_TO_UNPACK), 
      batch_callback=_tb
    ))
  _write_operation = _prepare_save_data_operation(lyrics_format, output_format)
  consumer = asyncio.create_task(
    __save_lyrics(
      output_directory=output_directory,
      filename=filename,
      queue=q,
      output_batch_size=n,
      producer_future=producer,
      _save_operation=_write_operation,
    )
  )
  await producer
  await q.join()
  consumer.cancel()

def check_if_file_exists(output_directory: str, output_format: MassOutputFileFormat, filename: str | None = None):
  """
    Checks if a given SQLITE/JSON file exists at the given directory. A default filename of 
    `lyrics.{db|json}` is assumed if no filename is given.

    JSON files have a sequential suffix attached, e.g. `lyrics-1.json`, `lyrics-2.json`, etc...
    In this case, this function checks for the existence of `lyrics-1.json` only.
  """
  if filename is None:
    filename = get_default_filename(output_format)
  
  if output_format == "json":
    filename = __get_filename_with_sequential_suffix(filename, 1)

  return exists(join(output_directory, filename))

def get_default_filename(output_format: MassOutputFileFormat) -> str:
  return f"lyrics{__get_extension(output_format)}"

def __get_batch_size(output_format: MassOutputFileFormat) -> int:
  if output_format == "json":
    return JSON_DUMP_BATCH_SIZE
  elif output_format == "sqlite":
    return SQL_INSERT_BATCH_SIZE
  raise ValueError

def __get_extension(output_format: MassOutputFileFormat) -> str:
  if output_format == "json":
    return ".json"
  elif output_format == "sqlite":
    return ".db"
  raise ValueError

def __get_filename_with_sequential_suffix(filename: str, counter: int) -> str:
  return re.sub(r"(\.[a-zA-Z0-9]+)$", fr"-{counter}\1", filename)

def __treat_batch(
    transformer: Callable[[str, int, str], Coroutine[Any, Any, ParsedResults]],
    queue: asyncio.Queue
  ) -> Callable[[Tuple[Tuple[str, etree.Element], ...]], Awaitable]:
  async def _fn(batch: Tuple[Tuple[str, etree.Element], ...]) -> None:
    """
      Async handler to parallelize several separate coroutines (one per page) for each batch
    """
    fn = __treat_page(transformer)
    waitTasks = asyncio.gather(
      *[fn(page) for _, page in batch],
      return_exceptions=False
    )
    await waitTasks
    for res in waitTasks.result():
      if res is None:
        continue
      await queue.put(res)
  return _fn

def __treat_page(transformer: Callable[[str, int, str], Coroutine[Any, Any, ParsedResults]]) -> Callable[[etree.Element], Coroutine[Any, Any, Optional[ParsedResults[Any]]]]:
  async def _fn(node: etree.Element) -> Optional[ParsedResults[Any]]:
    """
      Coroutine for each individual page
    """
    try:
      title, page_id, ns = get_page_properties(node)
      if ns != 0:
        return None
      page_contents = get_page_contents(node)
      res = await transformer(title, page_id, page_contents)
      return res
    
    except Exception:
      console.print(
        f"Failed to treat the page \"{title}\". Got the following error: ", 
        traceback.format_exc(), 
        sep="\n", 
        style="red"
      )
      return None
  return _fn

def _prepare_save_data_operation(
    lyrics_format: LyricFormat, 
    output_format: MassOutputFileFormat, 
  ) -> Callable[[str, str, int, List[Any]], None]:
  if output_format == "json":
    def inner(dir: str, filename: str, counter: int, data: List[Any]) -> None:
      rfilename = __get_filename_with_sequential_suffix(filename, counter)
      save_lyrics_json(join(dir, rfilename), data)
    return inner
  elif output_format == "sqlite":
    def inner(dir: str, filename: str, counter: int, data: List[Any]) -> None:
      save_lyrics_sqlite(
        db_filepath=join(dir, filename), 
        batch_results=data,
      )
    return inner
  raise NotImplementedError

async def __save_lyrics(
    output_directory: str,
    filename: str,
    queue: asyncio.Queue,
    output_batch_size: int,
    producer_future: asyncio.Future,
    _save_operation: Callable[[str, str, int, List[Any]], None],
  ):
  c = 1
  attempts, MAX_WRITE_ATTEMPTS = 0, 3
  buffer = []
  while True:
    popped = await queue.get()
    buffer.append(popped)
    queue.task_done()
    if len(buffer) >= output_batch_size or (producer_future.done() and queue.empty()):
      to_write = buffer[:output_batch_size]
      
      try:
        _save_operation(
          output_directory, 
          filename, 
          c,
          to_write
        )
        attempts = 0
        c += 1
      
      except Exception:
        attempts += 1
        if attempts < MAX_WRITE_ATTEMPTS:
          continue

        console.print("Exceeded maximum number of write attempts. Stopping operation...", style="magenta")
        producer_future.cancel()
        while not queue.empty():
          a = await queue.get()
          queue.task_done()
        break
      
      buffer = buffer[output_batch_size:]