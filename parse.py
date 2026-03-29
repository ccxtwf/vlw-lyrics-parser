import argparse

from vlw_lyrics_parser import (
  console,
  parse_lyrics_from_test_string,
  parse_lyrics_from_wiki_api,
  parse_lyrics_from_xml_dump
)
from vlw_lyrics_parser.pipeline.xml_to_html_to_lyrics import (
  get_default_filename,
  check_if_file_exists
)
from vlw_lyrics_parser.io.save_output_sqlite import (
  initialize_db
)
from vlw_lyrics_parser.config import (
  VLW_LIVE_API_ENTRYPOINT,
  CUSTOM_USER_AGENT,
)

import asyncio
import re

def confirm_action(prompt_message):
  while True:
    user_input = input(prompt_message + " [Y/N]: ").lower().strip()
    if user_input in ('y', 'yes'):
      return True
    elif user_input in ('n', 'no'):
      return False
    else:
      console.print("Invalid option. Please enter 'Y' or 'N'.")

def initialize_argparser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser()

  subparsers = parser.add_subparsers(
    dest='command', 
    help='Available commands'
  )

  shared_lyrics_format_argument = (
    ( "-M", "--lyrics-format" ), 
    { "type": str, "choices": ["plaintext"], "help": "Lyrics format" }
  )
  shared_output_format_argument_short = (
    ( "--output-format", ),
    { "type": str, "choices": ["console", "json"], "help": "Show parsed lyrics as console output or JSON file" }
  )
  shared_output_filepath = (
    ( "-o", "--output" ),
    { "type": str, "help": "Path to output file" }
  )

  test_string_parser = subparsers.add_parser(
    "str",
    help="Parse a portion of wikitext",
    usage="parse.py str [-h] [-o OUTPUT] wikitext",
    description="Takes in a portion of wikitext as input and returns a set of parsed lyrics as output.\n\nparse.py str wikitext\n\tPrints output to console\n\nparse.py str -o /path/to/output/file.json wikitext\n\tPrints output to a JSON file",
    formatter_class=argparse.RawTextHelpFormatter
  )
  test_string_parser.add_argument(
    "wikitext",
    type=str,
    help="Portion of wikitext"
  )
  test_string_parser.add_argument(
    *shared_lyrics_format_argument[0],
    **shared_lyrics_format_argument[1]
  )
  test_string_parser.add_argument(
    *shared_output_filepath[0],
    **shared_output_filepath[1]
  )
  test_string_parser.add_argument(
    *shared_output_format_argument_short[0],
    **shared_output_format_argument_short[1]
  )

  api_parser = subparsers.add_parser(
    "api",
    help="Fetch lyrics from the Vocaloid Lyrics Wiki API",
    usage="parse.py api [-h] [-t TITLE] [-pid PAGEID [-rid REVID]] [-o OUTPUT] [-ua USERAGENT]",
    description="Queries the API of the Vocaloid Lyrics Wiki and returns a set of parsed lyrics as output.\n\nparse.py api -t TITLE -o /path/to/output/file.json -ua \"Custom user agent - user@mail.com\"\n\tParses lyrics for page with the specified title, prints output to a JSON file\n\nparse.py api -t TITLE -ua \"Custom user agent - user@mail.com\"\n\tParses lyrics for page with the specified title, prints output to console\n\nparse.py api -pid 1234 -ua \"Custom user agent - user@mail.com\"\n\tParses lyrics for page with page ID 1234, prints output to console",
    formatter_class=argparse.RawTextHelpFormatter
  )
  api_parser.add_argument(
    "-t", "--title",
    type=str,
    help="Page title on Vocaloid Lyrics Wiki"
  )
  api_parser.add_argument(
    "-pid", "--pageid",
    type=str,
    help="Numeric Page ID on Vocaloid Lyrics Wiki"
  )
  api_parser.add_argument(
    "-rid", "--revid",
    type=str,
    help="Numeric Revision ID on Vocaloid Lyrics Wiki"
  )
  api_parser.add_argument(
    *shared_lyrics_format_argument[0],
    **shared_lyrics_format_argument[1]
  )
  api_parser.add_argument(
    *shared_output_filepath[0],
    **shared_output_filepath[1]
  )
  api_parser.add_argument(
    *shared_output_format_argument_short[0],
    **shared_output_format_argument_short[1]
  )
  api_parser.add_argument(
    "--api-entrypoint",
    type=str,
    help=f"MediaWiki API Entrypoint. Default: {VLW_LIVE_API_ENTRYPOINT}"
  )
  api_parser.add_argument(
    "-ua", "--user-agent",
    type=str,
    help="Custom user agent"
  )

  xml_parser = subparsers.add_parser(
    "xml",
    help="Iterates through a MediaWiki XML dump",
    usage="parse.py xml [-h] -i FILE_PATH -dir FOLDER_PATH [-f FILENAME] [--output-format {json|sqlite}]",
    description="Iterates through a MediaWiki XML dump and returns a set of parsed lyrics as output.\n\nparse.py xml -i /path/to/dump.xml -dir /path/to/output/folder\n\tSaves the results onto a file named lyrics.db in the output directory\n\nparse.py xml -i /path/to/dump.xml -dir /path/to/output/folder --output-format json\n\tSaves the results onto a file named lyrics-1.json (and lyrics-2.json, and so on) in the output directory\n\nparse.py xml -i /path/to/dump.xml -dir /path/to/output/folder -f custom-name.sqlite\n\tSaves the results to custom-name.sqlite in the output directory\n\nparse.py xml -i /path/to/dump.xml -dir /path/to/output/folder -f custom-name.json\n\tSaves the results to custom-name-1.json (and custom-name-2.json, and so on...) in the output directory\n\nparse.py xml -i /path/to/dump.xml -dir /path/to/output/folder --output-format json -n 100\n\tSaves the results to a JSON file (100 items per JSON file) in the output directory",
    formatter_class=argparse.RawTextHelpFormatter
  )
  xml_parser.add_argument(
    "-i", "--input",
    type=str,
    help="Path to the MediaWiki XML dump file",
    required=True,
  )
  xml_parser.add_argument(
    "-dir", "--directory",
    type=str,
    help="Directory path to where the output JSON/SQLITE files will be saved in",
    required=True,
  )
  xml_parser.add_argument(
    "-f", "--filename",
    type=str,
    help="The name of the JSON/SQLITE file(s). Default: lyrics.{json|db}",
  )
  xml_parser.add_argument(
    *shared_lyrics_format_argument[0],
    **shared_lyrics_format_argument[1]
  )
  xml_parser.add_argument(
    "--output-format",
    type=str, 
    choices=["json", "sqlite"], 
    help="Show parsed lyrics as JSON file or SQLITE database file",
  )
  xml_parser.add_argument(
    "-n", "--batch-size",
    type=int,  
    help="Number of items to add to the JSON/SQLITE database file per insert operation",
  )

  return parser

def main() -> None:
  parser = initialize_argparser()

  args = parser.parse_args()

  command = args.command
  coro = None

  if command is not None and args.lyrics_format is None:
    args.lyrics_format = "plaintext"

  if command == "str":
    coro = parse_lyrics_from_test_string(
      args.wikitext, 
      lyrics_format=args.lyrics_format,
      json_filepath=args.output,
      output_format=args.output_format,
    )
  
  elif command == "api":
    coro = parse_lyrics_from_wiki_api(
      title=args.title,
      pageid=args.pageid,
      revid=args.revid,
      lyrics_format=args.lyrics_format,
      json_filepath=args.output,
      output_format=args.output_format,
      api_entrypoint=args.api_entrypoint or VLW_LIVE_API_ENTRYPOINT,
      user_agent=args.user_agent or CUSTOM_USER_AGENT
    )
  
  elif command == "xml":
    clear_data = True

    if args.output_format is None:
      if args.filename is not None:
        if re.search(r"\.json$", args.filename, re.I) is not None:
          args.output_format = "json"
      args.output_format = args.output_format or "sqlite"
    args.filename = args.filename or get_default_filename(args.output_format)
    
    if args.batch_size is not None and args.batch_size < 0:
      args.batch_size = None

    has_existing_files = check_if_file_exists(
      output_directory=args.directory,
      output_format=args.output_format,
      filename=args.filename,
    )
    if has_existing_files:
      clear_data = confirm_action(f"Existing files in {args.directory} will be overwritten. Are you sure that you'd like to clear the data in these file(s)?")
        
    if args.output_format == "sqlite":
      if clear_data:
        console.print("Clearing existing data...")
        initialize_db(
          output_directory=args.directory, 
          filename=args.filename
        )
      else:
        console.print("Existing data will be kept")
    elif args.output_format == "json" and not clear_data:
      console.print("Terminating early...")
      return
    
    coro = parse_lyrics_from_xml_dump(
      xml_dump_file_path=args.input,
      output_directory=args.directory,
      filename=args.filename,
      lyrics_format=args.lyrics_format,
      output_format=args.output_format,
      batch_size=args.batch_size,
    )

  if coro is not None:
    asyncio.run(coro)

if __name__ == "__main__":
  main()