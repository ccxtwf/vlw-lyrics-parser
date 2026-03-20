import argparse

from vlw_lyrics_parser import console
from vlw_lyrics_parser import (
  parse_lyrics_from_test_string,
  parse_lyrics_from_wiki_api,
  parse_lyrics_from_xml_dump
)
from vlw_lyrics_parser.io.save_output_sqlite_plaintext import (
  initialize_db
)

import re
import asyncio
import os

VLW_API_ENTRYPOINT = "https://vocaloidlyrics.miraheze.org/w/api.php"

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
    ( "-f", "--lyrics-format" ), 
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
    usage="main.py str [-h] [-o OUTPUT] wikitext",
    description="Takes in a portion of wikitext as input and returns a set of parsed lyrics as output.\n\nmain.py str wikitext\n\tPrints output to console\n\nmain.py str -o /path/to/output/file wikitext\n\tPrints output to a JSON file",
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
    usage="main.py api [-h] [-t TITLE] [-pid PAGEID [-rid REVID]] [-o OUTPUT] [-ua USERAGENT]",
    description="Queries the API of the Vocaloid Lyrics Wiki and returns a set of parsed lyrics as output.\n\nmain.py api -t TITLE -o /path/to/output/file -ua \"Custom user agent - user@mail.com\"\n\tParses lyrics for page with the specified title, prints output to a JSON file\n\nmain.py api -t TITLE -ua \"Custom user agent - user@mail.com\"\n\tParses lyrics for page with the specified title, prints output to console\n\nmain.py api -pid 1234 -ua \"Custom user agent - user@mail.com\"\n\tParses lyrics for page with page ID 1234, prints output to console",
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
    help=f"MediaWiki API Entrypoint. Default: {VLW_API_ENTRYPOINT}"
  )
  api_parser.add_argument(
    "-ua", "--user-agent",
    type=str,
    help="Custom user agent"
  )

  xml_parser = subparsers.add_parser(
    "xml",
    help="Iterates through a MediaWiki XML dump",
    usage="main.py xml [-h] xml-filepath output-filepath",
    description="Iterates through a MediaWiki XML dump and returns a set of parsed lyrics as output.\n\nmain.py xml /path/to/xml /path/to/output",
    formatter_class=argparse.RawTextHelpFormatter
  )
  xml_parser.add_argument(
    "xml-filepath",
    type=str,
    help="Path to the MediaWiki XML dump file",
  )
  xml_parser.add_argument(
    "output-filepath",
    type=str,
    help="Path to the output JSON/SQLITE file",
  )
  xml_parser.add_argument(
    *shared_lyrics_format_argument[0],
    **shared_lyrics_format_argument[1]
  )
  xml_parser.add_argument(
    "--output-format",
    type=str, 
    choices=["json", "sqlite"], 
    help="Show parsed lyrics as JSON file or SQLITE file"
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
      api_entrypoint=args.api_entrypoint or VLW_API_ENTRYPOINT,
      user_agent=args.user_agent
    )
  elif command == "xml":
    is_json = re.search(r"\.json$", str(args.__dict__['output-filepath']), re.I) is not None 
    if args.output_format is None:
      args.output_format = "json" if is_json else "sqlite"
    
    clear_data = True
    if os.path.exists(args.__dict__['output-filepath']):
      clear_data = confirm_action(f"An existing file is detected on {args.__dict__['output-filepath']}. Are you sure that you'd like to clear the data in this file?")
    
    if args.output_format == "json" and not clear_data:
      console.print("Terminating early...")
      return
    if args.output_format == "sqlite":
      if clear_data:
        console.print("Clearing existing data...")
        initialize_db(args.__dict__['output-filepath'])
      else:
        console.print("Existing data will be kept")
    
    coro = parse_lyrics_from_xml_dump(
      xml_dump_file_path=args.__dict__['xml-filepath'],
      output_file_path=args.__dict__['output-filepath'],
      lyrics_format=args.lyrics_format,
      output_format=args.output_format
    )

  if coro is not None:
    asyncio.run(coro)

if __name__ == "__main__":
  main()