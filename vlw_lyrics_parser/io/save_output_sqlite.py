import sqlite3

from os.path import abspath, join

from .. import console, traceback
from ..classes.collection import ParsedResults

from typing import List, Tuple, Literal

def initialize_db(output_directory: str, filename: str):
  """
    Initialize a SQLITE database for storing lyrics.

    If a database exists at the given path, then data in the existing tables will 
    be cleared and the schema rebuilt.
    
    Parameters:
        output_directory (str):
        filename (str):
  """
  filename = abspath(join(output_directory, filename))
  console.print(f"Creating an SQLITE Database at {filename}", style="magenta")
  db_conn = sqlite3.connect(filename)
  db_cursor = db_conn.cursor()
  db_cursor.execute("DROP TABLE IF EXISTS VLW_PAGES;")
  db_cursor.execute("DROP TABLE IF EXISTS VDB_LINKS;")
  db_cursor.execute("DROP TABLE IF EXISTS LYRICS_PLAINTEXT;")
  db_cursor.execute("DROP TABLE IF EXISTS TRANSLATORS;")
  db_cursor.execute("CREATE TABLE VLW_PAGES(VLW_ID INTEGER NOT NULL, VLW_TITLE VARCHAR);")
  db_cursor.execute("""
    CREATE TABLE VDB_LINKS(
      VLW_ID INTEGER NOT NULL 
        REFERENCES VLW_PAGES(VLW_ID) ON UPDATE CASCADE ON DELETE CASCADE, 
      VDB_ID INTEGER NOT NULL
    );""")
  db_cursor.execute("""
    CREATE TABLE LYRICS_PLAINTEXT(
      VLW_ID INTEGER NOT NULL 
        REFERENCES VLW_PAGES(VLW_ID) ON UPDATE CASCADE ON DELETE CASCADE, 
      TABLE_ID VARCHAR, 
      COL_ID VARCHAR,
      HEADER VARCHAR, 
      LYRICS TEXT, 
      TRANSLATION_CREDITS VARCHAR, 
      IS_OFFICIAL_TRANSLATION INTEGER,
      NOTES TEXT
    );""")
  db_cursor.execute("""
    CREATE TABLE TRANSLATORS(
      VLW_ID INTEGER NOT NULL 
        REFERENCES VLW_PAGES(VLW_ID) ON UPDATE CASCADE ON DELETE CASCADE, 
      TABLE_ID VARCHAR, 
      COL_ID VARCHAR,
      HEADER VARCHAR, 
      TRANSLATOR VARCHAR
    );""")
  # No index, sorry
  
  db_conn.commit()
  db_conn.close()

def save_lyrics_sqlite_plaintext(db_filepath: str, batch_results: List[ParsedResults[str]]):
  """
    Save the parsed plaintext lyrics to a SQLITE database.
    
    Parameters:
        db_filepath (str):
        batch_results (List[ParsedResults[str]]):
  """
  # Aggregate
  dto_pages: List[Tuple[int, str]] = []
  dto_vdb_links: List[Tuple[int, int]] = []
  dto_lyrics: List[Tuple[int, str, str, str, str | None, str | None, Literal[0, 1] | None, str | None]] = []
  dto_translators: List[Tuple[int, str, str, str, str]] = []
  for results in batch_results:
    page_id = results.vlw_page_id
    dto_pages.append((page_id, results.title))
    dto_vdb_links.extend([(page_id, id) for id in results.vdb_ids])
    for table_id, st in results.lyrics.items():
      m = st.map_ids
      tn = results.notes.get(table_id, None)
      for col_id, header in m.items():
        lyrics = st.data.get(col_id, [])
        lyrics = "\n".join(lyrics)
        translators = st.translators.get(col_id, None) if st.translators is not None else None
        translators_text = translators.text if translators is not None else None
        notes = tn.get(col_id, None) if tn is not None else None
        notes = "\n".join(map(lambda note: note.to_plaintext(), notes)) if notes is not None else None
        is_official_translation = None
        if translators is not None:
          is_official_translation = 1 if translators.is_official else 0
        dto_lyrics.extend([
          (page_id, table_id, col_id, header, lyrics, translators_text, is_official_translation, notes)
        ])
        if translators is not None:
          dto_translators.extend(
            [(page_id, table_id, col_id, header, translator) for translator in translators.translators]
          )
      if tn is not None and "*" in tn:
        notes = tn["*"]
        notes = "\n".join(map(lambda note: note.to_plaintext(), notes))
        dto_lyrics.append(
          (page_id, table_id, "*", "*", None, None, None, notes)
        )
    if "*" in results.notes:
      for col_id, notes in results.notes["*"].items():
        notes = "\n".join(map(lambda note: note.to_plaintext(), notes))
        dto_lyrics.append(
          (page_id, "*", col_id, col_id, None, None, None, notes)
        )

  db_conn = sqlite3.connect(db_filepath)
  db_cursor = db_conn.cursor()
  db_cursor.execute("BEGIN TRANSACTION;")
  try:
    db_cursor.executemany(
      f"INSERT INTO VLW_PAGES(VLW_ID, VLW_TITLE) VALUES (?, ?);", 
      dto_pages
    )
    db_cursor.executemany(
      f"INSERT INTO VDB_LINKS(VLW_ID, VDB_ID) VALUES (?, ?);", 
      dto_vdb_links
    )
    db_cursor.executemany(
      f"INSERT INTO LYRICS_PLAINTEXT(VLW_ID, TABLE_ID, COL_ID, HEADER, LYRICS, TRANSLATION_CREDITS, IS_OFFICIAL_TRANSLATION, NOTES) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", 
      dto_lyrics
    )
    db_cursor.executemany(
      f"INSERT INTO TRANSLATORS(VLW_ID, TABLE_ID, COL_ID, HEADER, TRANSLATOR) VALUES (?, ?, ?, ?, ?);", 
      dto_translators
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
  finally:
    db_conn.close()