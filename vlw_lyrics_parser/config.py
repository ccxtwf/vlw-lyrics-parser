from os import getenv

def __get_numeric_env_variable(key: str, default: int):
  v = getenv(key)
  if v is not None and v.isnumeric():
    return int(v)
  return default

VLW_LIVE_API_ENTRYPOINT = "https://vocaloidlyrics.miraheze.org/w/api.php"

WIKITEXT2HTML_PARSER_API_ENTRYPOINT = getenv("WIKITEXT2HTML_PARSER_API_ENTRYPOINT", "")

CUSTOM_USER_AGENT = getenv("CUSTOM_USER_AGENT", "Custom User Agent")

MAX_PAGES_TO_UNPACK = __get_numeric_env_variable("MW_XML_UNPACK_MAX_NUM_PAGES", 20)
JSON_DUMP_BATCH_SIZE = __get_numeric_env_variable("JSON_DUMP_BATCH_SIZE", 100)
SQL_INSERT_BATCH_SIZE = __get_numeric_env_variable("SQL_INSERT_BATCH_SIZE", 50)