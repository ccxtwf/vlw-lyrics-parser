from ...libs.wikitextprocessor.src.wikitextprocessor import Wtp
from ...libs.wikitextprocessor.src.wikitextprocessor.parser import (
  NodeKind, 
  WikiNode, 
  GeneralNode
)

from ... import console, traceback
from .utils import get_wikitext_processor
from ...classes.collection import (
  ParsedResults, 
  ParsedLyrics, 
  ParsedTranslators, 
  ReferenceItem,
)
from ...classes.types import LyricFormat
from ...classes.exceptions import LyricsFormatNotImplementedException

from html import unescape
import json
import re
from itertools import dropwhile
from collections import defaultdict

from typing import List, Set, Dict, Tuple, Iterable, get_args

def parse(title: str, page_id: int, contents: str, lyrics_format: LyricFormat) -> ParsedResults:
  """
    Uses wikitextprocessor to parse the given page contents into a tree, and processes
    the tree accordingly.

    wikitextprocessor is less memory intensive than making a request to the Action API on
    a local wiki but is far more experimental.
  """
  
  if lyrics_format not in get_args(LyricFormat):
    raise LyricsFormatNotImplementedException()
  
  wtp = get_wikitext_processor()
  wtp.start_page(title)
  tree = __get_parse_tree(wtp, contents)

  table_ids: List[str] = []
  """parsed_lyrics: <[Table ID], [Struct]>"""
  parsed_lyrics: Dict[str, ParsedLyrics[str]] = {}
  """translators: <[Table ID], <[Column ID], [Struct]> >"""
  translators: Dict[str, Dict[str, ParsedTranslators]] = defaultdict(dict)
  """notes: <[Table ID], <[Column ID], [Struct]> >"""
  notes: Dict[str, Dict[str, List[ReferenceItem]]] = defaultdict(lambda: defaultdict(list))
  categories: List[str]
  vocadb_ids: List[int]

  __get_lyrics_from_lyrics_tables(
    wtp=wtp,
    tree=tree,
    table_ids=table_ids,
    res=parsed_lyrics,
    lyrics_format=lyrics_format,
  )
  __get_lyrics_from_poem_divs(
    wtp=wtp,
    tree=tree,
    res=parsed_lyrics,
    lyrics_format=lyrics_format,
  )

  categories, vocadb_ids = __get_properties(
    tree=tree
  )

  translator_templates, official_english_tl_templates, reflist_templates = __fetch_templates(
    tree=tree
  )
  __get_translation_info(
    wtp=wtp,
    translator_templates=translator_templates,
    official_english_templates=official_english_tl_templates,
    translators=translators,
  )
  __get_notes(
    wtp=wtp,
    ref_elements=tree.find_html_recursively(target_tag="ref"),
    reflist_templates=reflist_templates,
    notes=notes
  )

  res = __collate_results(
    title=title,
    page_id=page_id,
    table_ids=table_ids,
    parsed_lyrics=parsed_lyrics,
    translators=translators,
    notes=notes,
    vocadb_ids=vocadb_ids,
    categories=categories,
  )
  
  return res

def __get_parse_tree(wtp: "Wtp", contents: str) -> WikiNode:
  """
    It is especially important to have the following templates expanded:
    
    Required to parse the song page's categories, e.g. Mandarin songs
     - Infobox Song
     - AlternateVersion",
    
    Required to parse the lyrics anchors correctly
     - Lyrics toggle
     - Lyrics header
     - Lyrics table class
     - Lyrics column anchor
     - Reflist
     - OfficialEnglishNotify 
     - Translator

    Colspan formatting
     - Shared

    <poem>
     - Lyrics
     - LyricsJp
     - LyricsRz

    Link templates
     - VDB
  """
  return wtp.parse(contents, expand_all=True)

def __convert_node_to_text(wtp: "Wtp", node: "WikiNode", remove_coloured_blocks: bool = False) -> str:
  """Parses the text contents of a wikinode"""
  sb: List[str] = []
  def recurse(node: GeneralNode, parent: GeneralNode | None = None):
    if type(node) == str:
      contents = unescape(node)
      if (
        remove_coloured_blocks and 
        parent is not None and isinstance(parent, WikiNode) and 
        re.search(r"^\s*■[\s■]*$", contents) is not None and 
        re.search(r"color\s*:", parent.attrs.get("style", "")) is not None
      ):
        """
        Skip:
        `<span style="color:red;">■</span>`
        `<span style="color:red;">■<span style="color:green;">■</span></span>`
        `<span style="color:red;">■</span><span style="color:green;">■</span>`\
        """
        return
      sb.append(contents)
      return
    assert(isinstance(node, WikiNode))
    if node.kind == NodeKind.TEMPLATE:
      expanded = wtp.parse(wtp.node_to_wikitext(node), expand_all=True)
      recurse(expanded, node)
      # do not recurse the current node's children
      return
    elif node.kind == NodeKind.LINK or node.kind == NodeKind.URL:
      if len(node.largs) == 1:
        recurse(node.largs[0][0])
      else:
        for p in node.largs[1]:
          recurse(p)
    for child in node.children:
      recurse(child, node)
  recurse(node)
  return "".join(sb)

def __get_lyrics_from_lyrics_tables(
    wtp: "Wtp", 
    tree: "WikiNode", 
    table_ids: List[str], 
    res: Dict[str, ParsedLyrics[str]],
    lyrics_format: LyricFormat
  ) -> None:
  """Parses lyrics from each column of the lyrics tables"""
  for node in tree.find_html_recursively(
    target_tag='div', 
    attr_name='class', 
    attr_value='lyrics-options'
  ):
    lyrics_table_id = node.attrs.get('data-id', None)
    if lyrics_table_id is None:
      continue
    
    lyrics_id_map: Dict[str, str]
    __lyrics_id_map_attr = node.attrs.get('data-labels', None)
    try:
      if __lyrics_id_map_attr is not None:
        lyrics_id_map = json.loads(unescape(__lyrics_id_map_attr))
    except:
      lyrics_id_map = {}
      
    __col_ids_attr = unescape(node.attrs.get('data-languages', ''))
    col_ids = re.split(r"\s*,\s*", __col_ids_attr)
    headers = [lyrics_id_map.get(col_id, "") for col_id in col_ids]
    n_columns = len(col_ids)

    table_ids.append(lyrics_table_id)
    parsed_lyrics = ParsedLyrics[str](
      table_id=lyrics_table_id, 
      map_ids=lyrics_id_map, 
      headers=headers
    )
    res[lyrics_table_id] = parsed_lyrics

    """Get the lyrics table corresponding to the toggle"""
    tbl = None
    for n in dropwhile(
      lambda n: (
        "id" not in n.attrs or 
        "lyrics-table" not in re.split(r"\s+", n.attrs.get("class", "")) or
        n.attrs.get("id", None) != f"lyrics-{lyrics_table_id}"
      ),
      tree.find_child_recursively(target_kinds=NodeKind.TABLE)
    ):
      tbl = n
      break
    if tbl is None:
      continue  # Move to the next lyrics options toggle

    """Start fetching the lyrics from each column here"""
    trs = tbl.find_child(target_kinds=NodeKind.TABLE_ROW)
    next(trs, None) # skip first table row
    for tr in trs:
      tds = list(tr.find_child(target_kinds=NodeKind.TABLE_CELL))
      i = 0
      for td in tds:
        td_text = __convert_node_to_text(wtp, td, remove_coloured_blocks=True).rstrip()

        colspan = 1
        # shared <br /> column
        if len(tds) == 1 and td_text == "":
          colspan = n_columns
        # either a single cell or a cell with a set colspan attribute
        else:
          colspan = td.attrs.get("colspan", "1").strip()
          colspan = int(colspan) if colspan.isnumeric() else 1

        while i < n_columns and colspan > 0:    
          col_id = col_ids[i]
          parsed_lyrics.data[col_id].append(td_text)
          i += 1
          colspan -= 1
        
        # if having reached the last column, continue to the next row
        if i >= n_columns:
          break
    
def __get_lyrics_from_poem_divs(
    wtp: "Wtp", 
    tree: "WikiNode", 
    res: Dict[str, ParsedLyrics[str]],
    lyrics_format: LyricFormat
  ) -> None:
  """Parses lyrics from invocations of <poem> or {{Lyrics}}"""
  for i, node in enumerate(tree.find_html_recursively(target_tag="poem")):
    id = f"___poem-{i+1}"
    a = ParsedLyrics[str](
      headers=["*"],
      table_id=id,
    )
    a.data["*"] = [__convert_node_to_text(wtp, node, remove_coloured_blocks=True).rstrip()]
    res[id] = a

def __get_properties(tree: "WikiNode") -> Tuple[List[str], List[int]]:
  """Get the VocaDB ids and categories that are parsed from the tree."""
  vocadb_ids: List[int] = []
  categories: Set[str] = set()

  iwlinks = tree.find_child_recursively(target_kinds=NodeKind.LINK)
  for iwlink in iwlinks:
    iwlink_internal = str(iwlink.largs[0][0])
    
    # Find [[vdb:S/NNN|VocaDB]]
    m = re.search(r"^\s*vdb\s*:\s*S\/([0-9]+)", iwlink_internal) 
    if m is not None:
      vocadb_ids.append(int(m.group(1)))
    
    # Find [[Category:some cat|sortkey]]
    m = re.search(r"^[Cc]at(?:egory|)\s*:\s*(.*)\s*$", iwlink_internal)
    if m is not None:
      categories.add(m.group(1))
  
  extlinks = tree.find_child_recursively(target_kinds=NodeKind.URL)
  for extlink in extlinks:
    extlink_url = str(extlink.largs[0][0])
    
    # Find [https://vocadb.net Some text]
    m = re.search(r"^\s*https?:\/\/vocadb\.net\/S\/([0-9]+)", extlink_url)
    if m is not None:
      vocadb_ids.append(int(m.group(1)))
  
  return (list(categories), vocadb_ids)

def __fetch_templates(tree: "WikiNode") -> Tuple[List[WikiNode], List[WikiNode], List[WikiNode]]:
  translator_templates: List[WikiNode] = []
  official_english_tl_templates: List[WikiNode] = []
  reflist_templates: List[WikiNode] = []

  def recurse(node: GeneralNode):
    if isinstance(node, str):
      return
    assert(isinstance(node, WikiNode))
    if node.has_css_class("references-small"):
      # yield expanded {{Reflist}}
      yield (node, "ref")
      # do not traverse further the tree 
      return
    if node.has_css_class("lyrics-anchor"):
      for child in node.children:
        if not isinstance(child, WikiNode):
          continue
        child_class_list = child.css_classes()
        if "vlw-translators" in child_class_list:
          # yield expanded {{Translator}}
          yield (node, "tl")
          break
        if "vlw-official-english" in child_class_list:
          # yield expanded {{OfficialEnglishNotify}}
          yield (node, "offeng")
          break
      # do not traverse further the tree 
      return
    for child in node.children:
      yield from recurse(child)

  for tpl, ttype in recurse(tree):
    if ttype == "ref":
      reflist_templates.append(tpl)
    elif ttype == "tl":
      translator_templates.append(tpl)
    elif ttype == "offeng":
      official_english_tl_templates.append(tpl)
  
  return (translator_templates, official_english_tl_templates, reflist_templates)

def __parse_template_params(wtp: "Wtp", largs: List[List[str | WikiNode]]) -> Dict[str, str]:
  res: Dict[str, str] = {}
  n = 0
  for larg in largs:
    k_nodes: GeneralNode
    v_nodes: GeneralNode
    x: int = -1
    for i, p in enumerate(larg):
      if type(p) != str:
        continue
      if "=" in p:
        x = i
        break
    if x == -1:
      n += 1
      k_nodes = [str(n)]
      v_nodes = larg[:]
    else:
      s = larg[x]
      assert(type(s) == str)
      m = re.search(r"^\s*(.*?)\s*=\s*(.*)\s*$", s)
      assert(m is not None)
      k_nodes = larg[:x] + [m.group(1)]
      v_nodes = [m.group(2)] + larg[x+1:]

    k = wtp.expand(wtp.node_to_wikitext(k_nodes))
    v = wtp.expand(wtp.node_to_wikitext(v_nodes))
    res[k] = v
  return res

def __get_anchor_table_and_column_ids(node: WikiNode) -> Tuple[str | None, str | None]:
  class_list = node.css_classes()
  anchor_table_id: str | None = None
  anchor_column_id: str | None = None
  for cls in class_list:
    if cls.startswith("lyrics-table-"):
      anchor_table_id = cls[len("lyrics-table-"):]
    if cls.startswith("lyrics-anchor-"):
      anchor_column_id = cls[len("lyrics-anchor-"):]
  return anchor_table_id, anchor_column_id

def __get_translation_info(wtp: "Wtp", translator_templates: List["WikiNode"], official_english_templates: List["WikiNode"], translators: Dict[str, Dict[str, ParsedTranslators]]) -> None:
  for tpl in translator_templates:
    anchor_table_id, anchor_column_id = __get_anchor_table_and_column_ids(tpl)
    if anchor_table_id is None and anchor_column_id is None:
      continue
    assert(anchor_table_id is not None)
    assert(anchor_column_id is not None)

    el = [child for child in tpl.children if isinstance(child, WikiNode) and child.has_css_class("vlw-translators")]
    if len(el) == 0:
      continue
    el = el[0]
    credits = unescape(el.attrs.get("data-array", "[]"))
    try:
      credits = json.loads(credits)
    except json.decoder.JSONDecodeError:
      console.print(
        f"Unable to parse the loaded translators' data from the 'data-array' attribute. Got string: {credits}",
        traceback.format_exc(),
        sep="\n", 
        style="red"
      )
      continue
    text = __convert_node_to_text(wtp, el).rstrip() + "\n"
    
    if anchor_column_id not in translators[anchor_table_id]:
      translators[anchor_table_id][anchor_column_id] = ParsedTranslators(
        col_id=anchor_column_id,
        is_official=False,
        translators=[],
        text="",
      )
    
    o = translators[anchor_table_id][anchor_column_id]
    o.translators.extend(credits)
    o.text += text
  
  for tpl in official_english_templates:
    anchor_table_id, anchor_column_id = __get_anchor_table_and_column_ids(tpl)
    if anchor_table_id is None and anchor_column_id is None:
      continue
    assert(anchor_table_id is not None)
    assert(anchor_column_id is not None)

    if anchor_column_id not in translators[anchor_table_id]:
      translators[anchor_table_id][anchor_column_id] = ParsedTranslators(
        col_id=anchor_column_id,
        is_official=False,
        translators=[],
        text="",
      )
    o = translators[anchor_table_id][anchor_column_id]
    o.is_official = True

def __get_notes(wtp: "Wtp", ref_elements: Iterable["WikiNode"], reflist_templates: List["WikiNode"], notes: Dict[str, Dict[str, List[ReferenceItem]]]) -> None:
  """Parses the translation notes"""
  ref_items: Dict[str, List[ReferenceItem]] = defaultdict(list)
  ss = set()
  for node in ref_elements:
    ref_group = node.attrs.get("group", None)
    counter = int(node.attrs.get("__ref_count", "0"))
    node_contents = __convert_node_to_text(wtp, node).rstrip()
    ssu = f"{ref_group or "*"}-{counter}"
    if ssu in ss:
      continue
    ss.add(ssu)
    ref_items[ref_group or "*"].append(
      ReferenceItem(
        group_name=ref_group, 
        counter=counter,
        text=node_contents,
      )
    )
  
  for node in reflist_templates:
    anchor_element = None
    for child in node.children:
      if type(child) == str:
        continue
      if isinstance(child, WikiNode) and child.kind == NodeKind.HTML and child.has_css_class("lyrics-anchor"):
        anchor_element = child
        break
    
    ref_element = next(node.find_html_recursively(target_tag="references"), None)
    if ref_element is None:
      continue

    ref_group = ref_element.attrs.get("group", "*")
    anchor_table_id, anchor_column_id = None, None
    if anchor_element is not None:
      anchor_table_id, anchor_column_id = __get_anchor_table_and_column_ids(anchor_element)

    notes[anchor_table_id or "*"][anchor_column_id or "*"] = ref_items[ref_group]

def __collate_results(
  title: str,
  page_id: int,
  table_ids: List[str],
  parsed_lyrics: Dict[str, ParsedLyrics[str]],
  translators: Dict[str, Dict[str, ParsedTranslators]],
  notes: Dict[str, Dict[str, List[ReferenceItem]]],
  vocadb_ids: List[int],
  categories: List[str],
) -> ParsedResults:
  
  res: ParsedResults = ParsedResults(
    title=title,
    vlw_page_id=page_id,
    vdb_ids=vocadb_ids,
    categories=categories,
    table_ids=table_ids,
    lyrics=parsed_lyrics,
    notes=notes,
  )

  for table_id, struct in translators.items():
    if table_id not in res.lyrics:
      res.lyrics[table_id] = ParsedLyrics(
        table_id=table_id,
        map_ids={},
        data={},
        translators=struct
      )
    elif res.lyrics[table_id].translators is None:
      res.lyrics[table_id].translators = struct
    else:
      o = res.lyrics[table_id].translators
      assert(o is not None)
      for col_id, parsed_translators in struct.items():
        o[col_id] = parsed_translators

  return res