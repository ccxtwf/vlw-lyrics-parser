from pydantic import BaseModel, Field, computed_field

from typing import Any, List, Dict

class ParsedTranslators(BaseModel):
  """
    A representation of translation credits for a given translator

    `col_id`
    The semantic ID of the column

    `is_official`
    `True` if the translation is officially sourced (edits may
    have been made)

    `translators`
    List of translators that worked on the translation (not 
    including proofreaders & editors)

    `text`
    Free text, representing the written text on VLW
  """
  col_id: str
  is_official: bool
  translators: List[str] = Field(default_factory=list)
  text: str

class ReferenceItem(BaseModel):
  """
    A representation of a `li` item in `ol.references` (the HTML element
    representing a group of references/notes)
    
    `group_name`
    The group name of the <references /> tag.

    `anchor_hash` 
    The hash fragment of the reference item.
    Citations on the wiki page will refer to this `anchor_hash`.

    `counter` 
    The index position of the `li` item in `ol`.

    `text` 
    The text contents of the reference/note.
  """
  group_name: str | None
  anchor_hash: str
  counter: int
  text: str

  def to_plaintext(self) -> str:
    return f"[{self.group_name + " " if self.group_name is not None else ""}{self.counter}] {self.text}"

class ParsedLyricsPlaintext(BaseModel):
  """
    A representation of data for one lyrics table
     - Lyrics are stored as plaintext
     - A lyrics table may have more than one translation
     - A translation may be officially or unofficially sourced.
     - Official translations are marked by {{OfficialEnglishNotify}}.
     - Translations are credited to translators marked by the {{Translator}} template.
     - There may also be translation notes
    
    `headers`
    A list of plaintext strings, representing the text of the column headers

    `_map_ids`
    Key -> Semantic Column ID, e.g. `jp`, `rom`, `en`; 
    Value -> Column header (same as listed in `headers`)

    `data`
    Data representation of the plaintext contents of each table cell,
    belonging to each column

    Key -> Semantic Column ID, e.g. `jp`, `rom`, `en`; 
    Value -> List containing the plaintext contents of each table cell

    `translators`
    Data representation of the translation credits, corresponding to a specific column

    Key -> Semantic Column ID, e.g. `en`
    Value -> List of translators' names and whether the translation is official
  """
  headers: List[str] = Field(default_factory=list)
  table_id: str
  map_ids: Dict[str, str] = Field(default_factory=dict)
  data: Dict[str, List[str]] = Field(default_factory=dict, exclude=True)
  translators: Dict[str, ParsedTranslators] | None = None
  # notes: Dict[str, List[ReferenceItem]]

  def model_post_init(self, __context=None):
    self.data = { id: [] for id in self.map_ids }

  @computed_field
  @property
  def lyrics(self) -> Dict[str, str]:
    return { id: "\n".join(l) for id, l in self.data.items() }

class ParsedResults(BaseModel):
  """
    A representation of data for one wikipage
    One wikipage may have several lyrics tables

    `title`
    The title of the page on Vocaloid Lyrics Wiki

    `vlw_page_id`
    The page id on Vocaloid Lyrics Wiki

    `vdb_page_id`
    The page id on VocaDB

    `table_ids`
    A list of strings corresponding to the semantic IDs of the lyrics tables.
    These semantic IDs comprise the keys to the `lyrics` dictionary.

    `lyrics`
    A list of objects, corresponding to the number of 
    lyrics tables on the given page (note that one lyrics 
    table may have more than one translation)

    Key -> Semantic Table ID, e.g. `1`;
    Value -> Structured `ParsedLyricsPlaintext` object

    `notes`
    Data representation of the references/notes, which may be 
    bound to a specific column

    Key -> Semantic Table ID, e.g. `1`, or `*` if the notes aren't 
    bound to a table;
    Value -> ( 
      Key -> Semantic Column ID, e.g. `jp`, `rom`, `en`, or `*` 
      if the notes aren't bound to a column; 
      Value -> List containing the reference items of each 
      reference group
    )
  """
  title: str
  vlw_page_id: int
  vdb_ids: List[int] = Field(default_factory=list)
  table_ids: List[str] = Field(default_factory=list)
  lyrics: Dict[str, ParsedLyricsPlaintext] = Field(default_factory=dict)
  notes: Dict[str, Dict[str, List[ReferenceItem]]] = Field(default_factory=dict)