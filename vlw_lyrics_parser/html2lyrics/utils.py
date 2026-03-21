from .. import console, traceback

from typing import List

import re

def get_vocadb_ids(iw_links: List[str], external_links: List[str]) -> List[int]:
  """
    Parses the numerical song page IDs of links pointing to VocaDB.

    Parameters:
        iw_links (List[str]):       Sample input:
                                    ["vdb:S/242985", "vdb:  S/242985", "vdb:___S/242985", "vdb:S/242985a"]
        external_links (List[str]): Sample input:
                                    ["https://vocadb.net/S/242985", "https://utaten.net"]
    
    Returns:
        List[int]:                  List of IDs
  """
  res = []
  for iw_link in iw_links:
    m = re.match(r"^vdb[\s_]*:[\s_]*S/(\d+)$", iw_link)
    if m is None:
      continue
    res.append(int(m.group(1)))
  for external_link in external_links:
    m = re.match(r"^https?://vocadb\.net/S/(\d+)$", external_link)
    if m is None:
      continue
    res.append(int(m.group(1)))
  return res