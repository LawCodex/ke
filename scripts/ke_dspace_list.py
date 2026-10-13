"""List items of a DSpace 7 scope (collection/community) on libraryir.parliament.go.ke -> JSON lines."""
import json, sys, time, requests
UA = "LawCodex/1.0 (+https://github.com/LawCodex)"
BASE = "https://libraryir.parliament.go.ke/server/api"
S = requests.Session(); S.headers["User-Agent"] = UA

def items(scope):
    page = 0
    while True:
        r = S.get(BASE + "/discover/search/objects", params={"scope": scope, "dsoType": "ITEM", "size": 100, "page": page}, timeout=120)
        r.raise_for_status()
        sr = r.json()["_embedded"]["searchResult"]
        for o in sr["_embedded"]["objects"]:
            it = o["_embedded"]["indexableObject"]
            yield {"uuid": it["uuid"], "handle": it.get("handle"), "name": it["name"],
                   "meta": {k: [x["value"] for x in v] for k, v in it["metadata"].items() if k != "dc.description.provenance"}}
        page += 1
        if page >= sr["page"]["totalPages"]:
            break
        time.sleep(1.5)

if __name__ == "__main__":
    out = open(sys.argv[2], "w")
    for it in items(sys.argv[1]):
        out.write(json.dumps(it) + "\n")
