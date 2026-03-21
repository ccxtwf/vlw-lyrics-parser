from pyquery import PyQuery as pq

from .. import console, traceback
from ..classes.collection import ParsedTranslators, ReferenceItem

import json

from typing import List, Dict, Tuple

def parse_ids_and_headers(lyrics_table: pq) -> Tuple[str, Dict[str, str], List[str]]:
  """
    Parse the table ID, the semantic ID of each column, as well as the text contents of each 
    column header, of the lyrics table

    The table ID is the **semantic ID** of the lyrics table, needed for the toggle feature of 
    the wiki. For example, a lyrics table with the HTML `id` attribute of `lyrics-1` has the 
    table ID of `1`.

    The column **semantic ID** is the backbone upon which the column toggle feature works.
    Several elements on the page, e.g. the reference groups, the translation credits 
    & licenses, are bound to specific columns of the lyrics table and are identifiable
    by these semantic IDs. For example, a lyrics table may have the following semantic column 
    IDs: `jp`, `rom`, and `eng` (representing 'Japanese', 'Romaji', 'English'). The lyrics columns 
    will then have the CSS classes `lyrics-jp`, `lyrics-rom`, and `lyrics-eng` corresponding 
    to these semantic IDs.

    Parameters:
        lyrics_table (PyQuery):   PyQuery document object representing a lyrics table
    
    Returns:
        ( &lt;TABLE_ID&gt;, &lt;TABLE_COLUMN_ID_HASHMAP&gt;, &lt;TABLE_COLUMN_HEADERS&gt; ):
                                  `TABLE_ID` (str) is the semantic ID of the table.

                                  `TABLE_COLUMN_ID_HASHMAP` (Dict[str, str]) is a 
                                  dictionary mapping the semantic ID of each column
                                  with the column headers

                                  `TABLE_COLUMN_HEADERS` (List[str]) is a list
                                  of plaintext representations of the table column
                                  headers 
  """
  table_id = str(lyrics_table.attr('id') or "lyrics-1")[len("lyrics-"):]
  th = lyrics_table.find('tbody tr.lyrics-table-header > th')
  th_ids = {}
  headers = []
  for i in range(len(th)):
    n = th.eq(i)
    clss = str(n.attr("class") or "")
    col_id = clss.replace("lyrics-", "")
    text = n.text()
    th_ids[col_id] = text
    headers.append(text)
  return (table_id, th_ids, headers)

def parse_translators(root: pq, lyrics_table_id: str) -> Dict[str, ParsedTranslators]:
  """
    Parse the names of the translator who worked on the translation. 

    Official translations are marked by the `{{OfficialEnglishNotify}}`
    template.

    The translation credits is marked by the `{{Translator}}` template on VLW.
    Each translation credits is bound to the `eng` column (or a custom column)
    on the lyrics table.

    Parameters:
        root (PyQuery):                 PyQuery document root
        lyrics_table_id (str):          Semantic ID of the table

    Returns:
        ( Dict[str, ParsedTranslators] ):   
                                        A dictionary mapping the semantic column
                                        of the ID with the parsed translators info
  """
  res: Dict[str, ParsedTranslators] = {}
  
  """
    Check for the presence of {{Translator}}
  """
  divs = root.find(f".lyrics-table-{lyrics_table_id}:has(.vlw-translator)")
  for i in range(len(divs)):
    div = divs.eq(i)
    tl = div.find('.vlw-translator')

    list_classes = [clss[len('lyrics-anchor-'):] for clss in str(div.attr('class')).split(" ") if clss.startswith('lyrics-anchor-')]
    col_id = list_classes[0]

    text = str(tl.text() or "").strip()
    
    if col_id not in res:
      res[col_id] = ParsedTranslators(
        col_id=col_id, 
        translators=[], 
        text=text,
        is_official=False
      )
    
    translators = []
    try:
      translators = json.loads(str(tl.attr('data-array') or ""))
    except json.decoder.JSONDecodeError:
      console.print(
        f"Unable to parse the loaded translators' data from the 'data-array' attribute. Got string: {str(tl.attr('data-array') or "None")}",
        traceback.format_exc(),
        sep="\n", 
        style="red"
      )
      raise
    
    res[col_id].translators.extend(translators)
  
  """
    Check for the presence of {{OfficialEnglishNotify}}
  """
  divs = root.find(f".lyrics-table-{lyrics_table_id}:has(.vlw-official-english)")
  for i in range(len(divs)):
    div = divs.eq(i)
    list_classes = [clss[len('lyrics-anchor-'):] for clss in str(div.attr('class')).split(" ") if clss.startswith('lyrics-anchor-')]
    if len(list_classes) == 0:
      continue
    col_id = list_classes[0]
    if col_id not in res:
      continue
    res[col_id].is_official = True

  return res
    
def parse_reference_notes(root: pq) -> Dict[str, Dict[str, List[ReferenceItem]]]:
  """
    Parses the references "{{Reflist}}" or "<references />" within the page
    In VLW, different reference groups may be bound to different columns of different
    lyrics tables. When the column's visibility is toggled on/off, so does the
    visibility of the references group. The modules/templates that control this 
    behaviour may be observed in the following pages:
     - Template:Reflist
     - Template:Lyrics column anchor
    
    This function does not yet differentiate between reference groups that are 
    noting about something in the lyrics and/or translation, and reference groups 
    that are not.

    Parameters:
        root (PyQuery):                 PyQuery document root
    
    Returns:
        ( Dict[str, Dict[str, List[ReferenceItem]]] ):
                                        A dictionary mapping the semantic ID of the
                                        table, with another dictionary mapping the 
                                        semantic column ID of the table with the 
                                        parsed reference item
  """
  ddict: Dict[str, Dict[str, List[ReferenceItem]]] = {}
  outer_wrappers = root.find('.references-small')
  for i in range(len(outer_wrappers)):
    outer_wrapper = outer_wrappers.eq(i)
    
    """
      Determine which column of the lyrics table the references div is bound to
    """
    anchor_wrapper_div = outer_wrapper.children(':not(.mw-references-wrap)')
    anchor_table = None
    anchor_col = None
    if len(anchor_wrapper_div) == 0:
      # The references group is not bound to any column
      pass
    else:
      list_classes = (str(anchor_wrapper_div.eq(0).attr('class')) or "").split(" ")
      a = [clss for clss in list_classes if clss.startswith('lyrics-table-')]
      b = [clss for clss in list_classes if clss.startswith('lyrics-anchor-')]
      if len(a) > 0:
        anchor_table = a[0][len('lyrics-table-'):]
      if len(b) > 0:
        anchor_col = b[0][len('lyrics-anchor-'):]

    # Default to these keys if the <references /> are not bound to anything
    anchor_table = anchor_table or "*"
    anchor_col = anchor_col or "*"
    if anchor_table not in ddict:
      ddict[anchor_table] = {}

    res: List[ReferenceItem] = []
    if (anchor_col in ddict[anchor_table]):
      res = ddict[anchor_table][anchor_col]
    else:
      ddict[anchor_table][anchor_col] = res

    """
      Get the text content of the references group
    """
    references_ol = outer_wrapper.find('ol.references')
    ref_group_name = references_ol.attr('data-mw-group')
    ref_group_name = str(ref_group_name) if ref_group_name is not None else None
    references_items = references_ol.children('li')
    counter = 0
    for j in range(len(references_items)):
      ref_item = references_items.eq(j)
      counter += 1
      anchor_hash = str(ref_item.attr('id') or "")
      plaintext = str(ref_item.find('.reference-text').text() or "").strip()
      res.append(
        ReferenceItem(
          group_name=ref_group_name,
          anchor_hash=anchor_hash, 
          counter=counter, 
          text=plaintext
        )
      )
  
  return ddict
