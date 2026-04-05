from .types import LyricFormat
from typing import get_args

class ReadXmlException(Exception):
  pass

class ReadMediawikiException(Exception):
  pass

class FileWriteExceededMaxAttemptsException(IOError):
  pass

class LyricsFormatNotImplementedException(NotImplementedError):
  def __init__(self) -> None:
    super().__init__(f"'lyrics_format' argument can only accept one of the following values: {get_args(LyricFormat)}")