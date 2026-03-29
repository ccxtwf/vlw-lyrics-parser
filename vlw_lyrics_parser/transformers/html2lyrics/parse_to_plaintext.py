from pyquery import PyQuery as pq

from ... import console, traceback
from ...classes.collection import ParsedLyrics, ReferenceItem
from .parse_properties import parse_ids_and_headers, parse_translators, parse_reference_notes

import re

from typing import Dict, Tuple, List

def parse_to_plaintext(raw_html: str) -> Tuple[List[str], Dict[str, ParsedLyrics[str]], Dict[str, Dict[str, List[ReferenceItem]]]]:
  """
    Parse the lyrics (as plaintext) from the given HTML string

    Parameters:
        raw_html (str):       Raw HTML string
    
    Returns:
        ( &lt;TABLE_IDS&gt;, &lt;PARSED_LYRICS&gt;, &lt;PARSED_REFERENCE_NOTES&gt; ):
                              `TABLE_IDS` (List[str]) is the list of semantic IDs of 
                              each table
                              `PARSED_LYRICS` (Dict[str, ParsedLyrics[str]]) is a
                              dictionary mapping the semantic ID of each table with
                              the parsed lyrics
                              `PARSED_REFERENCE_NOTES` (Dict[str, Dict[str, List[ReferenceItem]]]) 
                              is a dictionary mapping the semantic ID of each table 
                              with the parsed notes
    Output:
    ( Array[ &lt;TABLE_ID> ], Map[ &lt;TABLE ID>, &lt;PARSED LYRICS & OTHER INFO> ] )
  """
  try:
    table_ids: List[str] = []
    res: Dict[str, ParsedLyrics[str]] = {}
    notes: Dict[str, Dict[str, List[ReferenceItem]]] = {}

    d = pq(raw_html)

    lyrics_tables = d('.mw-parser-output table.lyrics-table')
    n_tables = len(lyrics_tables)

    for i in range(n_tables):

      lyrics_table = lyrics_tables.eq(i)

      table_id, map_col_id_to_header, headers = parse_ids_and_headers(lyrics_table)
      col_ids = list(map_col_id_to_header.keys())
      table_ids.append(table_id)
      parsed_lyrics = ParsedLyrics[str](
        table_id=table_id, 
        map_ids=map_col_id_to_header, 
        headers=headers
      )
      res[table_id] = parsed_lyrics

      # Assume that the number of columns in a table is less than or equal to 
      # the number of headers in the table
      num_columns = len(headers)
      
      table_rows = lyrics_table.find('tbody tr:not(.lyrics-table-header)')

      def traverse_rows():
        table_cells = pq(this).find('td') # type: ignore
        saved_colspan_offset = 0
        last_saved_cell_contents = ""
        i = 0
        n_table_cells = len(table_cells)
        def traverse_cells():
          table_cell = pq(this) # type: ignore
          nonlocal saved_colspan_offset
          nonlocal last_saved_cell_contents
          nonlocal i
          nonlocal n_table_cells

          # Account for <td colspan="2">
          while saved_colspan_offset > 0 and i < num_columns:
            parsed_lyrics.data[col_ids[i]].append(last_saved_cell_contents)
            i += 1
            saved_colspan_offset -= 1
          
          # Ignore cells located outside the max. number of columns
          if i >= num_columns:
            return
          
          # Save colspan offset (e.g. for <td colspan="2">, save offset as 1)
          if table_cell.attr("colspan"):
            try:
              _colspan = int(table_cell.attr("colspan")) # type: ignore
              if _colspan > 1:
                saved_colspan_offset += _colspan - 1
            except ValueError:
              pass
          
          # Manipulate the contents of table_cell
          table_cell = __strip_coloured_blocks(table_cell)
          table_cell = __strip_ruby(table_cell)

          # Get text contents of td
          """
          Possible: Convert the HTML of each table cell into some rich text format?
          """
          last_saved_cell_contents = str(table_cell.text() or "").strip()
          # Account for shared <br /> cells throughout the row
          if i == 0 and n_table_cells == 1 and last_saved_cell_contents == "":
            saved_colspan_offset = num_columns - 1
          parsed_lyrics.data[col_ids[i]].append(last_saved_cell_contents)
          i += 1
        
        table_cells.each(traverse_cells)

        # In the case where <td colspan="2"> is the final or only cell
        while saved_colspan_offset > 0 and i < num_columns:
          parsed_lyrics.data[col_ids[i]].append(last_saved_cell_contents)
          i += 1
          saved_colspan_offset -= 1
    
      table_rows.each(traverse_rows)

      try:
        res[table_id].translators = parse_translators(d, lyrics_table_id=table_id)
      except:
        pass
      
    poem_divs = d('.mw-parser-output .poem')
    for i in range(len(poem_divs)):
      id = f"___poem-{i+1}"
      poem_div = poem_divs.eq(i)
      a = ParsedLyrics[str](
        headers=["*"],
        table_id=id,
      )
      a.data["*"] = [str(poem_div.text())]
      res["*"] = a
    
    notes = parse_reference_notes(d)

    return (table_ids, res, notes)
  
  except Exception:
    console.print(
      "Failed to parse the lyrics from the given HTML string. Got error: ",
      traceback.format_exc(),
      sep="\n", 
      style="red"
    )
    raise

def __is_coloured_block(idx: int, node: pq) -> bool:
  """
    Filter for:
    
    `<span style="color:red;">■</span>`
    
    `<span style="color:red;">■<span style="color:green;">■</span></span>`
    
    `<span style="color:red;">■</span><span style="color:green;">■</span>`
  """
  node = pq(node)
  has_color_style = (node.css.color or "") != ""  # type: ignore
  if not has_color_style:
    return False
  has_no_content = re.match(r"^\s*■[\s■]*$", (str(node.text() or ""))) is not None
  return has_no_content

def __strip_coloured_blocks(td: pq) -> pq:
  """
    Remove `<span style="color:red;">■</span>` from the table cell
  """
  remove_blocks = td.find('span, div').filter(__is_coloured_block)
  remove_blocks.replace_with('')
  return td

def __strip_ruby(td: pq) -> pq:
  """
    Convert `<ruby><rb>腸</rb><rp>(</rp><rt>はらわた</rt><rp>)</rp></ruby>` -> `腸(はらわた)`
  """
  ruby = td.find('ruby')
  for i in range(len(ruby)):
    ruby_elements = ruby.eq(i).children().map(lambda i, e: str(pq(this).text() or ""))   # type: ignore
    ruby.eq(i).replace_with(f"<span>{"".join(ruby_elements)}</span>")
  return td