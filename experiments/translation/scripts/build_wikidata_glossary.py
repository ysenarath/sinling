"""Look up FLORES phrases in Wikidata and keep those with a Sinhala label (Wikidata is CC0).

For each English phrase found in the FLORES sentences, ask Wikidata for items whose English label
is exactly that phrase and that also have a Sinhala label. When several items share a label, keep
the one linked from the most Wikipedias, which is usually the most notable sense.
"""

import json
import time
import urllib.parse
import urllib.request

from common import GLOSSARY, flores, phrases, write_jsonl

ENDPOINT = "https://query.wikidata.org/sparql"
HEADERS = {
    "Accept": "application/sparql-results+json",
    "User-Agent": "sinling-translation-experiment/0.1 (https://github.com/ysenarath/sinling)",
}
BATCH = 250


def query(labels):
    values = " ".join(json.dumps(label) + "@en" for label in labels)
    sparql = f"""
    SELECT ?label ?si ?item ?links WHERE {{
      VALUES ?label {{ {values} }}
      ?item rdfs:label ?label .
      ?item rdfs:label ?si . FILTER(LANG(?si) = "si")
      ?item wikibase:sitelinks ?links .
    }}"""
    data = urllib.parse.urlencode({"query": sparql}).encode()
    for attempt in range(5):
        try:
            request = urllib.request.Request(ENDPOINT, data=data, headers=HEADERS)
            with urllib.request.urlopen(request, timeout=90) as response:
                return json.load(response)["results"]["bindings"]
        except Exception as e:  # rate limits and timeouts: back off and retry
            wait = 10 * (attempt + 1)
            print(f"  retry in {wait}s: {e}")
            time.sleep(wait)
    raise RuntimeError("Wikidata query kept failing")


candidates = set()
for split in ("dev", "devtest"):
    for sentence in flores(split)[0]:
        for phrase in phrases(sentence):
            candidates.add(phrase)
            candidates.add(phrase.lower())
candidates = sorted(candidates)
print(f"{len(candidates)} candidate phrases")

best = {}
for i in range(0, len(candidates), BATCH):
    for row in query(candidates[i : i + BATCH]):
        label, si, links = (
            row["label"]["value"],
            row["si"]["value"],
            int(row["links"]["value"]),
        )
        item = row["item"]["value"].rsplit("/", 1)[-1]
        if label not in best or links > best[label]["links"]:
            best[label] = {
                "en": label,
                "si": si,
                "source": "wikidata",
                "item": item,
                "links": links,
            }
    if i // BATCH % 20 == 0:
        print(f"  {i + BATCH}/{len(candidates)} looked up, {len(best)} found")
    time.sleep(1)

write_jsonl(
    GLOSSARY / "wikidata_en_si.jsonl", sorted(best.values(), key=lambda r: r["en"])
)
print(f"{len(best)} Wikidata entries written")
