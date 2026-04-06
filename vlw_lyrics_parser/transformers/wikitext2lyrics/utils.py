from ...libs.wikitextprocessor.src.wikitextprocessor import Wtp

from pathlib import Path

def get_template_cache_path() -> Path:
  template_cache_dir_path = Path.cwd() / "data"
  if template_cache_dir_path.is_dir() and not template_cache_dir_path.exists():
    template_cache_dir_path.mkdir()
  return template_cache_dir_path / "vlw-templates.db"

wtp: Wtp | None = None

def setup_template_overrides(wtp: Wtp) -> None:
  """
    We do this to get over some unavoidable quirks with template parameter 
    substitution (which is to say some quirks with #loop, #while, #dowhile, #var)

    Hacky solution
  """
  def setup_translator_override(wtp: Wtp) -> None:
    wtp.warning("Setting up an override for template {{Translator}}")
    template_body = []
    for i in range(1, 6, 1):
      tvar = "{{{" + str(i) + "|}}}"
      tvardn = "{{{display-" + str(i) + "|}}}"
      storevarname = "__tl_link_" + str(i)
      template_body.append(
        "{{#if:" + tvar + "|" + 
          "{{#vardefine:" + storevarname + "|" + 
            "[[:Category:Tracking/Translator/" + tvar + 
              "{{!}}" + 
              "{{#if:" + tvardn + "|" + tvardn + "|" + tvar + "}}" + 
            "]]" + 
            "{{#if:" + tvar + "|" + "{{cat|Tracking/Translator/" + tvar + "}}" + "}}" + 
          "}}" + 
        "}}"
      )
    template_body.append("""{{Lyrics column anchor
  |table-id={{{anchor-table|}}}|col-id={{{anchor-col|}}}
  |{{DataWrap
    |class=vlw-translators
    |data-array={{DataWrapElements|{{{1|}}}|{{{2|}}}|{{{3|}}}|{{{4|}}}|{{{5|}}}|size=5}}
    |content='''English translation {{#if:{{{lang|}}}|of {{{lang}}}&nbsp;}}{{#if:{{{from|}}}|from|by}} {{#invoke:String|list|{{#var:__tl_link_1}}|{{#var:__tl_link_2}}|{{#var:__tl_link_3}}|{{#var:__tl_link_4}}|{{#var:__tl_link_5}}}}{{#if:{{{editors|}}}|, with edits by {{{editors}}}}}{{#if:{{{proofreaders|}}}|, proofread by {{{proofreaders}}}}}{{#if:{{{append|}}}|, {{{append|}}}}}'''
  }}}}""")
    
    wtp.add_page(
      title="Template:Translator",
      namespace_id=10,
      model="wikitext",
      need_pre_expand=False,
      body="".join(template_body)
    )
    
  setup_translator_override(wtp)

def get_wikitext_processor() -> "Wtp":
  """Get wikitextprocessor singleton"""
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
  setup_template_overrides(wtp)
  return wtp