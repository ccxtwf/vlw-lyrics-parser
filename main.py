from package.io.save_output_sqlite_plaintext import initialize_db
from package.pipeline.xml_to_html_to_lyrics_plaintext import pipeline

import asyncio

def main():
  DUMP_FILE_NAME = "path/to/xml/dump"
  OUTPUT_SQL_FILE = "vlw_parsed_lyrics.db"
  OUTPUT_JSON_FILE = "vlw_parsed_lyrics.json"

  # initialize_db(OUTPUT_SQL_FILE)
  # asyncio.run(pipeline(DUMP_FILE_NAME, OUTPUT_SQL_FILE, as_sql_db=True))
  asyncio.run(pipeline(DUMP_FILE_NAME, OUTPUT_JSON_FILE, as_sql_db=False))

if __name__ == "__main__":
  main()