"""Baut data/median.json aus der Eurostat-API (Tabelle ilc_di03, ohne Schlüssel abrufbar).

    python pipeline/median.py           # laden, prüfen, schreiben
    python pipeline/median.py --check   # nur vergleichen

Median-Nettoäquivalenzeinkommen, Deutschland, alle Altersgruppen, beide Geschlechter, Euro.
Ein Zeitreihenbruch (Eurostat-Kennzeichen 'b') wird als "bruch": true übernommen.
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "median.json"
API = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/ilc_di03"
       "?geo=DE&statinfo=MED_EI&unit=EUR&age=TOTAL&sex=T&lang=DE")
VIEW = "https://ec.europa.eu/eurostat/databrowser/view/ilc_di03/default/table"
START = 2015


def fail(msg):
    print("FEHLER: " + msg, file=sys.stderr)
    sys.exit(1)


def main():
    check = "--check" in sys.argv
    req = urllib.request.Request(API, headers={"User-Agent": "bundeshaushalt-dashboard-datenabgleich"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    if "value" not in d:
        fail("Unerwartete Antwort von Eurostat: " + json.dumps(d)[:300])
    idx = {i: int(y) for y, i in d["dimension"]["time"]["category"]["index"].items()}
    status = d.get("status", {})
    rows = []
    for k, v in sorted(d["value"].items(), key=lambda kv: idx[int(kv[0])]):
        y = idx[int(k)]
        if y < START:
            continue
        rows.append({"jahr": y, "median_eur": float(v), "bruch": "b" in (status.get(k) or ""),
                     "quelle": "Eurostat ilc_di03 (EU-SILC), Erhebungsjahr", "url": VIEW})
    years = [r["jahr"] for r in rows]
    if years != list(range(START, START + len(rows))):
        fail("Lücke in der Eurostat-Reihe: " + ", ".join(map(str, years)))
    old = {r["jahr"]: r for r in json.loads(PATH.read_text(encoding="utf-8"))}
    diffs = []
    for r in rows:
        o = old.get(r["jahr"])
        if o is None:
            diffs.append(f"median {r['jahr']} neu: {r['median_eur']:.0f} €")
        elif o["median_eur"] != r["median_eur"] or o["bruch"] != r["bruch"]:
            diffs.append(f"median {r['jahr']}: bisher {o['median_eur']:.0f} €, neu {r['median_eur']:.0f} €")
        # Prüfung: plausible Größenordnung, damit ein Formatfehler nicht unbemerkt durchgeht
        if not 10000 < r["median_eur"] < 80000:
            fail(f"Unplausibler Wert {r['jahr']}: {r['median_eur']}")
    print(f"Median: {len(rows)} Jahre ({years[0]}–{years[-1]}), {len(diffs)} Abweichungen")
    for x in diffs:
        print("  " + x)
    if check:
        return
    PATH.write_text("[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n]\n", encoding="utf-8")
    bericht = ROOT / "pipeline" / "bericht.md"
    prev = bericht.read_text(encoding="utf-8") if bericht.exists() else ""
    bericht.write_text(prev + "\nMedianeinkommen: " + (f"{len(diffs)} Änderungen" if diffs else "keine Änderungen") + "\n\n"
                       + "".join("- " + x + "\n" for x in diffs), encoding="utf-8")


if __name__ == "__main__":
    main()
