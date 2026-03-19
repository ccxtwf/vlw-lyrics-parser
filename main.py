from package.io.save_output_sqlite import initialize_db
from package.pipeline.xml_to_html_to_lyrics_plaintext import pipeline

import asyncio

def main():
  DUMP_FILE_NAME = "path/to/xml/dump"
  OUTPUT_SQL_FILE = "vlw_parsed_lyrics.db"

  initialize_db(OUTPUT_SQL_FILE)
  asyncio.run(pipeline(DUMP_FILE_NAME, OUTPUT_SQL_FILE))

if __name__ == "__main__":
  main()