from pyquery import PyQuery as pq

from .. import console, traceback
from ..classes.collection import ParsedLyricsPlaintext

import re

from typing import List

def parse(raw_html: str) -> List[ParsedLyricsPlaintext]:
  d = pq(raw_html)
  lyrics = _parse_lyrics(d)
  return lyrics

def _parse_lyrics(d: pq) -> List[ParsedLyricsPlaintext]:
  """
    Parse the lyrics (as plaintext) from the given HTML string
  """
  try:
    res = []

    lyrics_tables = d('.mw-parser-output table.lyrics-table')
    n_tables = len(lyrics_tables)

    for i in range(n_tables):

      lyrics_table = lyrics_tables.eq(i)

      headers: List[str] = lyrics_table.find('tbody tr.lyrics-table-header > th').map(lambda _, node: pq(node).text())
      parsed_lyrics = ParsedLyricsPlaintext(headers)
      res.append(parsed_lyrics)

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
            parsed_lyrics.data[headers[i]].append(last_saved_cell_contents)
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
          table_cell = strip_coloured_blocks(table_cell)

          # Get text contents of td
          """
          Possible: Convert the HTML of each table cell into some rich text format?
          """
          last_saved_cell_contents = table_cell.text().strip()  # type: ignore
          # Account for shared <br /> cells throughout the row
          if i == 0 and n_table_cells == 1 and last_saved_cell_contents == "":
            saved_colspan_offset = num_columns - 1
          parsed_lyrics.data[headers[i]].append(last_saved_cell_contents)
          i += 1
        
        table_cells.each(traverse_cells)

        # In the case where <td colspan="2"> is the final or only cell
        while saved_colspan_offset > 0 and i < num_columns:
          parsed_lyrics.data[headers[i]].append(last_saved_cell_contents)
          i += 1
          saved_colspan_offset -= 1
    
      table_rows.each(traverse_rows)

    return res
  
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

def strip_coloured_blocks(td: pq) -> pq:
  """
    Remove `<span style="color:red;">■</span>` from the table cell
  """
  remove_blocks = td.find('span, div').filter(__is_coloured_block)
  remove_blocks.replace_with('')
  return td