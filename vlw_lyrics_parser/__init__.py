from typing import Final

from rich.console import Console
import traceback
console = Console()

from dotenv import load_dotenv
load_dotenv()

# printing constants
JSON_INDENTATION: Final = 2

from .io.save_output_sqlite import initialize_db
from .pipeline.test_string_to_html_to_lyrics import pipeline as parse_lyrics_from_test_string
from .pipeline.wiki_api_to_lyrics import pipeline as parse_lyrics_from_wiki_api
from .pipeline.xml_to_html_to_lyrics import pipeline as parse_lyrics_from_xml_dump