import xml.etree.ElementTree as ET
from xml.sax.saxutils import unescape

from itertools import batched

from .. import console, traceback, getenv
from ..classes.exceptions import ReadXmlException

from typing import Tuple
from collections.abc import Callable, Awaitable

XML_NAMESPACE = getenv("MW_XML_DUMP_NAMESPACE")

async def read_dump(
    dump_file_path: str, 
    max_pages_to_unpack_at_a_time: int, 
    batch_callback: Callable[[Tuple[ET.Element, ...]], Awaitable]
  ) -> None:
  """
    Reads the given XML dump file, unpacks several pages at a time, then starts an async task 
    to call the MediaWiki `action=parse` API
  """
  try:
    console.print("Opening file: ", dump_file_path, style="magenta")
    
    for batch in batched(iterate_xml(dump_file_path), max_pages_to_unpack_at_a_time):
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

def iterate_xml(dump_file_path: str):
  """
    Overly simplistic XML parser
    
    Will prolly break over malformed XML or incorrectly formatted XML
  """
  xml_iter = ET.iterparse(dump_file_path, events=['start', 'end'])
  # last_tag = None
  is_open = False
  root = None
  cur = next(xml_iter, None)
  while cur:
    event, element = cur
    if event == "start" and not is_open and element.tag in [f"{XML_NAMESPACE}page"]:
      is_open = True
      root = element
      # last_tag = element.tag
    elif event == "end" and root is not None and element.tag == root.tag:
      yield root
      is_open = False
      root = None
    cur = next(xml_iter, None)

def get_page_properties(xmlTree: ET.Element) -> Tuple[str, int]:
  try:
    title = xmlTree.find(f"{XML_NAMESPACE}title")
    if title is None or title.text is None:
      raise ReadXmlException("Failed to read <title> of <page>")
    title = title.text

    page_id = xmlTree.find(f"{XML_NAMESPACE}id")
    if page_id is None or page_id.text is None:
      raise ReadXmlException("Failed to read <id> of <page>")
    page_id = int(page_id.text) # type: ignore

    return (title, page_id)
  
  except Exception:
    raise

def get_page_contents(xmlTree: ET.Element) -> str:
  """
    Reads the page content for the given XML element

    IMPORTANT: 
    xmlTree.find() finds the first element (from top) with the given tag
    This function assumes that there can only be one <revision> element in one <page> element
    If you exported only the latest revision of the pages, then you shouldn't worry.
    If you exported the full history, worry more.
  """
  try: 
    if xmlTree.tag != f"{XML_NAMESPACE}page":
      raise ReadXmlException(f"Expected XML Element <page>, got <{xmlTree.tag}>")
    revision = xmlTree.find(f"{XML_NAMESPACE}revision")
    if revision is None:
      raise ReadXmlException("Cannot find XML element node <revision> in <page>")
    contents = revision.find(f"{XML_NAMESPACE}text")
    if contents is None or contents.text is None:
      raise ReadXmlException("Cannot find XML element node <text> in <revision>")
    contents = unescape(contents.text)
    return contents
  except Exception:
    raise