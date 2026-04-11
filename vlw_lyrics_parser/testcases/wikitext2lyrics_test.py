import pytest
from ..transformers.wikitext2lyrics.index import parse
from .transformer_test_cases import testcases

@pytest.mark.parametrize("case", testcases)
def test_parse_wikitext2lyrics(case):
  res = parse(
    title=case.page_title,
    page_id=0,
    contents=case.page_contents,
    lyrics_format="plaintext"
  )
  assert res.table_ids == case.expected.table_ids
  for table_id in res.table_ids:
    got_lyrics = res.lyrics[table_id]
    expected_lyrics = case.expected.lyrics[table_id]
    assert got_lyrics.headers == expected_lyrics.headers
    assert got_lyrics.data == expected_lyrics.data
    assert got_lyrics.translators == expected_lyrics.translators
  assert res.notes == case.expected.notes