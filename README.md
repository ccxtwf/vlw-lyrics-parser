# Vocaloid Lyrics Wiki Lyrics Parser

This is a Python package used to parse individual lyrics from the [Vocaloid Lyrics Wiki](https://vocaloidlyrics.miraheze.org).

## Disclosure
### Copyright disclosure

Original lyrics uploaded to the Vocaloid Lyrics Wiki are copyrighted by their respective rights holders. Organizations involved in music copyright include, but are not limited to, [ASCAP](https://www.ascap.com/help/music-business-101/money-copyright), [BMI](https://www.bmi.com/faq/category/copyright), [JASRAC](https://www.jasrac.or.jp/en/creators/), NexTone, and the [Music Copyright Society of China](https://www.mcsc.com.cn/en/situation.html). Users are responsible for ensuring that their use of lyrics and translations does not infringe on these rights.

The authors of this repository are not responsible for any legal consequences resulting from misuse of lyrics or translations.

All other content hosted on the Vocaloid Lyrics Wiki is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.en) unless otherwise stated.

### Policy on high-volume API usage and scraping

Vocaloid Lyrics Wiki and the platform it is hosted on, Miraheze, are *volunteer-run* projects. High-volume API usage and scraping should be avoided unless absolutely necessary.

When making network requests to the Vocaloid Lyrics Wiki, make sure to follow proper etiquette:
 - Add a custom User Agent to your requests. The User Agent should contain contact details, e.g. a username or an email. [See this page for more information.](https://meta.miraheze.org/wiki/Tech:User_Agents)
 - You should not make requests at a rate higher than one every 3 seconds.

Failure to follow these rules may result in rate-limiting or blocking by the technology team.

## Setup

1) Clone this repository.
2) Create a file `.env` that contains the following variables:
```sh
# A working MediaWiki app is needed to parse wikitext -> HTML
# It is recommended to use a local MediaWiki mirror than to 
# make requests to the real Vocaloid Lyrics Wiki
MEDIAWIKI_ACTION_API_ENTRYPOINT="http://localhost:8080/api.php"

# For reading the MediaWiki XML dumps: 
#   XML namespace
MW_XML_DUMP_NAMESPACE="{http://www.mediawiki.org/xml/export-0.11/}"
#   number of pages to unpack from an XML dump at a time
MW_XML_UNPACK_MAX_NUM_PAGES=20
#   number of items to insert into the database per batch operation
SQL_INSERT_BATCH_SIZE=100
#   number of items to load per JSON dump
JSON_DUMP_BATCH_SIZE=100
```
3) Install the required Python packages listed on requirements.txt

## Usage

You can either use this package as part of another Python script/project, or use the provided command line interface (CLI). To start interacting with the CLI, run the following command:
```sh
python parse.py -h
```

### Parsing lyrics from a wiki page

The following snippet shows how you may use this package to parse lyrics from the Vocaloid Lyrics Wiki:

```sh
from vlw_lyrics_parser import parse_lyrics_from_wiki_api

# Print to console
parse_lyrics_from_wiki_api(
  title="ハローワールド (Hello World)",
  api_entrypoint="https://vocaloidlyrics.miraheze.org/w/api.php",
  user_agent="<Custom User Agent>"
)

# Save as JSON file
parse_lyrics_from_wiki_api(
  title="ハローワールド (Hello World)",
  api_entrypoint="https://vocaloidlyrics.miraheze.org/w/api.php",
  user_agent="<Custom User Agent>",
  json_filepath='vlw_test.json',
  output_format='json'
)
```

Alternatively, you can use the CLI:
```sh
# Prints to console
python parse.py api -t "ハローワールド (Hello World)" -ua "<Custom User Agent>"

# Save as JSON 
python parse.py api -t "ハローワールド (Hello World)" -o "/path/to/file.json" -ua "<Custom User Agent>"
```

### Parsing a test string into lyrics

The following snippet parses raw wikitext (sourced from the <code>?action=raw</code> output of a wiki page) into a set of lyrics, which may be printed onto the console output or saved as a JSON file.

```py
from vlw_lyrics_parser import parse_lyrics_from_test_string

import asyncio

json_filepath = "vlw_test.json"

s = """
{{sort}}{{Infobox Song
|songtitle = "'''ハローワールド'''"<br />Romaji: Haroo Waarudo<br />Official English: Hello World
|color = black; color:white
|original upload date = {{Date|2026|January|1}}
|singer = [[Hatsune Miku (VOCALOID)]]
|producer = [[faz]]
|#views = 100,000+
|link = {{#|https://www.youtube.com/watch?v=dQw4w9WgXcQ}}
|language = Japanese
}}

...
"""

# Print to console
asyncio.run(
  parse_lyrics_from_test_string(wikitext=s)
)

# Save as JSON file
asyncio.run(
  parse_lyrics_from_test_string(
    wikitext=s, 
    json_filepath=json_filepath,
    output_format='json'
  )
)
```

Alternatively, you can use the CLI:
```sh
python parse.py str "<WIKITEXT>"
```

### Parsing a MediaWiki export dump into plaintext lyrics

The following snippet parses a MediaWiki XML dump into a set of plaintext lyrics that are saved onto a SQLITE database.

```py
from vlw_lyrics_parser import initialize_db, parse_lyrics_from_xml_dump

import asyncio

DUMP_FILE_NAME = "/path/to/xml/dump"
OUTPUT_DIR = "/path/to/output/folder/dir"
SQLITE_DB_FILENAME = "lyrics.db"

# Recreates the database schema at the given filepath
initialize_db(OUTPUT_DIR, SQLITE_DB_FILENAME)
asyncio.run(
  parse_lyrics_from_xml_dump(
    xml_dump_file_path=DUMP_FILE_NAME, 
    output_directory=OUTPUT_DIR,
    filename=SQLITE_DB_FILENAME,
    output_format='sqlite'
  )
)
```

To save as JSON instead:

```py
from vlw_lyrics_parser import initialize_db, parse_lyrics_from_xml_dump

import asyncio

DUMP_FILE_NAME = "/path/to/xml/dump"
OUTPUT_DIR = "/path/to/output/folder/dir"
JSON_FILE_NAME = "lyrics.json"

asyncio.run(
  parse_lyrics_from_xml_dump(
    xml_dump_file_path=DUMP_FILE_NAME, 
    output_directory=OUTPUT_DIR,
    filename=JSON_FILE_NAME, 
    output_format='json'
  )
)
```

The equivalent CLI command is:
```sh
# Saves the results onto lyrics.db in the given directory
python parse.py xml -i /path/to/xml -dir /path/to/output

# Saves the results onto lyrics-1.json, lyrics-2.json, and so on in the given directory
python parse.py xml -i /path/to/xml -dir /path/to/output --output-format json

# Saves the results onto lyrics-1.json, lyrics-2.json, and so on in the given directory
# Saves 100 items per JSON file
python parse.py xml -i /path/to/xml -dir /path/to/output --output-format json -n 100
```