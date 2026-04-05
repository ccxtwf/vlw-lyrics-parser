from ...libs.wikitextprocessor.src.wikitextprocessor import Wtp

from pathlib import Path

def get_template_cache_path() -> Path:
  template_cache_dir_path = Path.cwd() / "data"
  if template_cache_dir_path.is_dir() and not template_cache_dir_path.exists():
    template_cache_dir_path.mkdir()
  return template_cache_dir_path / "vlw-templates.db"

wtp: Wtp | None = None

def get_wikitext_processor() -> "Wtp":
  global wtp
  if wtp is not None:
    return wtp
  wtp = Wtp(
    db_path=get_template_cache_path(),
    quiet=True,
  )
  if wtp.is_template_store_outdated():
    wtp.note("Template store is out-of-date. Repopulating from the live wiki...")
    wtp.repopulate_templates()
  return wtp