from typing import List, Dict

class ParsedLyricsPlaintext:
  headers: List[str]
  data: Dict[str, List[str]]

  def __init__(self, headers: List[str]):
    self.headers = headers
    self.data = { header: [] for header in headers }

class ParsedResults:
  title: str
  vlw_page_id: int
  vdb_ids: List[int]
  lyrics: List[ParsedLyricsPlaintext]

  def __init__(self, title: str, vlw_page_id: int, vdb_ids: List[int], lyrics: List[ParsedLyricsPlaintext]):
    self.title = title
    self.vlw_page_id = vlw_page_id
    self.vdb_ids = vdb_ids
    self.lyrics = lyrics