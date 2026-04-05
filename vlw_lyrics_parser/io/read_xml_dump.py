from lxml import etree
from xml.sax.saxutils import unescape

from itertools import batched

from .. import console, traceback
from ..classes.exceptions import ReadXmlException

from typing import Tuple
from collections.abc import Callable, Awaitable

async def read_dump(
    dump_file_path: str, 
    max_pages_to_unpack_at_a_time: int, 
    batch_callback: Callable[[Tuple[etree.Element, ...]], Awaitable]
  ) -> None:
  """
    Reads the given XML dump file, unpacks several pages at a time, then starts an async task 
    to call the MediaWiki `action=parse` API

    Parameters:
        dump_file_path (str):
        max_pages_to_unpack_at_a_time (int):
                                      Number of XML nodes to unpack at a time
        batch_callback ((lxml.etree.Element[]) -> Awaitable):
                                      Callback to execute upon yielding a batch of XML nodes
  """
  try:
    console.print("Opening file: ", dump_file_path, style="magenta")
    
    for batch in batched(
      etree.iterparse(dump_file_path, tag="{*}page"), 
      max_pages_to_unpack_at_a_time
    ):
      await batch_callback(batch)
    
  except Exception:
    console.print(
      f"Failed to read the XML dump. Got the following error: ", 
      traceback.format_exc(), 
      sep="\n", 
      style="red"
    )
  finally:
    console.print("Finished reading: ", dump_file_path, style="green")

def get_page_properties(xmlTree: etree.Element) -> Tuple[str, int]:
  """    
    Parameters:
        xmlTree (lxml.etree.Element):
                          An XML node representing a wikipage
    
    Returns:
        ( str, int ):     The page title and the numeric page ID       
  """
  try:
    title = xmlTree.findtext("{*}title", None)
    if title is None:
      raise ReadXmlException("Failed to read <title> of <page>")

    page_id = xmlTree.findtext("{*}id", None)
    if page_id is None:
      raise ReadXmlException("Failed to read <id> of <page>")
    if page_id.isnumeric():
      page_id = int(page_id)
    else:
      page_id = 0

    return (title, page_id)
  
  except Exception:
    raise

def get_page_contents(xmlTree: etree.Element) -> str:
  """
    Reads the page content for the given XML element

    IMPORTANT: 
    xmlTree.find() finds the first element (from top) with the given tag
    This function assumes that there can only be one <revision> element in one <page> element
    If you exported only the latest revision of the pages, then you shouldn't worry.
    If you exported the full history, worry more.
    
    Parameters:
        xmlTree (lxml.etree.Element):
                          An XML node representing a wikipage
    
    Returns:
        str:              Page contents
  """
  try: 
    revision = xmlTree.find("{*}revision")
    if revision is None:
      raise ReadXmlException("Cannot find XML element node <revision> in <page>")
    contents = revision.findtext("{*}text", None)
    if contents is None:
      raise ReadXmlException("Cannot find XML element node <text> in <revision>")
    contents = unescape(contents)
    return contents
  except Exception:
    raise