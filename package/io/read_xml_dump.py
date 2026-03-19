import xml.etree.ElementTree as ET
from xml.sax.saxutils import unescape

from itertools import batched

from .. import console, traceback, getenv
from ..classes.exceptions import ReadXmlException

from typing import Tuple
from collections.abc import Callable, Awaitable

XML_DEFINITION = getenv("DUMP_XML_DEFINITION")

async def read_dump(dump_file_path: str, max_pages_to_unpack_at_a_time: int, batch_callback: Callable[[Tuple[ET.Element, ...]], Awaitable]) -> None:
  """
    Reads the given XML dump file, unpacks several pages at a time, then starts an async task 
    to call the MediaWiki action=parse API
  """
  try:
    console.print("Opening the file: ", dump_file_path, style="magenta")
    tree = ET.parse(dump_file_path)
    root = tree.getroot()
    xml_iter = iter(root)
    next(xml_iter)  # Skip siteinfo
    
    for batch in batched(xml_iter, max_pages_to_unpack_at_a_time):
      await batch_callback(batch)
    
  except Exception:
    console.print(
      f"Failed to read the XML dump. Got the following error: ", 
      traceback.format_exc(), 
      sep="\n", 
      style="red"
    )
  finally:
    console.print("Finished reading the file: ", dump_file_path, style="green")

def get_page_properties(xmlTree: ET.Element) -> Tuple[str, int]:
  try:
    title = xmlTree.find(f"{XML_DEFINITION}title")
    if title is None or title.text is None:
      raise ReadXmlException("Failed to read <title> of <page>")
    title = title.text

    page_id = xmlTree.find(f"{XML_DEFINITION}id")
    if page_id is None or page_id.text is None:
      raise ReadXmlException("Failed to read <id> of <page>")
    page_id = int(page_id.text) # type: ignore

    return (title, page_id)
  
  except Exception:
    console.print(
      f"Failed to treat the page \"{title}\". Got the following error: ", 
      traceback.format_exc(), 
      sep="\n", 
      style="red"
    )
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
    if xmlTree.tag != f"{XML_DEFINITION}page":
      raise ReadXmlException(f"Expected XML Element <page>, got <{xmlTree.tag}>")
    revision = xmlTree.find(f"{XML_DEFINITION}revision")
    if revision is None:
      raise ReadXmlException("Cannot find XML element node <revision> in <page>")
    contents = revision.find(f"{XML_DEFINITION}text")
    if contents is None or contents.text is None:
      raise ReadXmlException("Cannot find XML element node <text> in <revision>")
    contents = unescape(contents.text)
    return contents
  except Exception:
    console.print(
      f"Failed to get the page contents. Got the following error: ", 
      traceback.format_exc(), 
      sep="\n", 
      style="red"
    )
    raise