import sqlite3

from os.path import abspath

from .. import console, traceback
from ..classes.collection import ParsedResults

from typing import List, Optional

def initialize_db(db_filepath: str):
  db_filepath = abspath(db_filepath)
  console.print(f"Creating an SQLITE Database at {db_filepath}", style="magenta")
  db_conn = sqlite3.connect(db_filepath)
  db_cursor = db_conn.cursor()
  db_cursor.execute("DROP TABLE IF EXISTS VLW_PAGES;")
  db_cursor.execute("DROP TABLE IF EXISTS VDB_LINKS;")
  db_cursor.execute("DROP TABLE IF EXISTS LYRICS;")
  db_cursor.execute("CREATE TABLE VLW_PAGES(VLW_ID INTEGER NOT NULL, VLW_TITLE VARCHAR);")
  db_cursor.execute("CREATE TABLE VDB_LINKS(VLW_ID INTEGER NOT NULL REFERENCES VLW_PAGES(VLW_ID) ON UPDATE CASCADE ON DELETE CASCADE, VDB_ID INTEGER NOT NULL);")
  db_cursor.execute("CREATE TABLE LYRICS(VLW_ID INTEGER NOT NULL REFERENCES VLW_PAGES(VLW_ID) ON UPDATE CASCADE ON DELETE CASCADE, INDEX_POS INTEGER, HEADER VARCHAR, LYRICS TEXT);")
  # No index, sorry

def save_lyrics(db_filepath: str, batch_results: List[Optional[ParsedResults]]):
  """
    Save the parsed lyrics to a SQLITE database
  """
  
  # Aggregate
  pages = []
  vdb_links = []
  lyrics = []
  for results in batch_results:
    if results is None:
      continue
    page_id = results.vlw_page_id
    pages.append((page_id, results.title))
    vdb_links.extend([(page_id, id) for id in results.vdb_ids])
    for l_idx, l_table in enumerate(results.lyrics):
      lyrics.extend([(page_id, l_idx, header, "\n".join(lyrics)) for header, lyrics in l_table.data.items()])

  db_conn = sqlite3.connect(db_filepath)
  db_cursor = db_conn.cursor()
  db_cursor.execute("BEGIN TRANSACTION;")
  try:
    db_cursor.executemany(
      f"INSERT INTO VLW_PAGES(VLW_ID, VLW_TITLE) VALUES (?, ?);", 
      pages
    )
    db_cursor.executemany(
      f"INSERT INTO VDB_LINKS(VLW_ID, VDB_ID) VALUES (?, ?);", 
      vdb_links
    )
    db_cursor.executemany(
      f"INSERT INTO LYRICS(VLW_ID, INDEX_POS, HEADER, LYRICS) VALUES (?, ?, ?, ?);", 
      lyrics
    )
    db_cursor.execute("COMMIT;")
  except Exception:
    console.print(
      f"Failed to save the parsed lyrics to the database. Got the following error: ", 
      traceback.format_exc(), 
      sep="\n", 
      style="red"
    )
    db_cursor.execute("ROLLBACK;")
    raise