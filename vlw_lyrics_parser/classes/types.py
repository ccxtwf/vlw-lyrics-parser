from .collection import (
  ParsedLyricsPlaintext, 
  ParsedResultsPlaintext
)
from typing import Literal

LyricFormat = Literal["plaintext", ]
OutputFileFormat = Literal["json", "console"]
MassOutputFileFormat = Literal["json", "sqlite"]

TParsedLyrics = ParsedLyricsPlaintext
TParsedResults = ParsedResultsPlaintext