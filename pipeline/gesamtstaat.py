"""Baut data/bund_gesamt.json aus der Eurostat-API (ohne Schlüssel abrufbar).

Sektor S1311 "Zentralstaat" der Volkswirtschaftlichen Gesamtrechnungen = Bund mit allen
Sondervermögen und Extrahaushalten (ohne Länder, Gemeinden und Sozialversicherungen).

- gov_10a_exp: Ausgaben nach Aufgabenbereichen (COFOG), Mio. €
- gov_10a_main: Finanzierungssaldo (B9), Mio. €; negativ = Defizit

    python pipeline/gesamtstaat.py           # laden, prüfen, schreiben
    python pipeline/gesamtstaat.py --check   # nur vergleichen
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data" / "bund_gesamt.json"
BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
START = 2015
BEREICHE = ["GF01", "GF02", "GF03", "GF04", "GF05", "GF06", "GF07", "GF08", "GF09", "GF10"]
NAMEN = {
    "TOTAL": "Insgesamt",
    "GF01": "Allgemeine öffentliche Verwaltung (inkl. Zinsen, EU-Beiträge)",
    "GF02": "Verteidigung",
    "GF03": "Öffentliche Ordnung und Sicherheit",
    "GF04": "Wirtschaftliche Angelegenheiten (inkl. Verkehr, Energie)",
    "GF05": "Umweltschutz",
    "GF06": "Wohnungswesen und kommunale Einrichtungen",
    "GF07": "Gesundheitswesen",
    "GF08": "Freizeit, Sport, Kultur und Religion",
    "GF09": "Bildungswesen",
    "GF10": "Soziale Sicherung (inkl. Zuschüsse an die Sozialversicherung)",
}


def fail(msg):
    print("FEHLER: " + msg, file=sys.stderr)
    sys.exit(1)


def get(dataset, query):
    req = urllib.request.Request(BASE + dataset + "?" + query, headers={"User-Agent": "bundeshaushalt-dashboard-datenabgleich"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.load(r)
    if "value" not in d:
        fail(f"{dataset}: unerwartete Antwort: " + json.dumps(d)[:300])
    return d


def cells(d):
    """JSON-stat -> Liste von (Dimensionswerte, Wert)."""
    ids, sizes = d["id"], d["size"]
    cats = {k: {i: c for c, i in d["dimension"][k]["category"]["index"].items()} for k in ids}
    out = []
    for k, v in d["value"].items():
        n, u = int(k), {}
        for dim, s in zip(reversed(ids), reversed(sizes)):
            u[dim] = cats[dim][n % s]
            n //= s
        out.append((u, v))
    return out


def main():
    check = "--check" in sys.argv
    q = f"geo=DE&sector=S1311&unit=MIO_EUR&sinceTimePeriod={START}"
    exp = get("gov_10a_exp", q + "&na_item=TE")
    main_ = get("gov_10a_main", q + "&na_item=B9")
    rows = []
    for u, v in cells(exp):
        c = u["cofog99"]
        if c in NAMEN:
            rows.append({"jahr": int(u["time"]), "reihe": "ausgaben", "bereich": c, "name": NAMEN[c], "mrd": round(v / 1000, 3)})
    for u, v in cells(main_):
        rows.append({"jahr": int(u["time"]), "reihe": "saldo", "bereich": "B9", "name": "Finanzierungssaldo", "mrd": round(v / 1000, 3)})
    rows.sort(key=lambda r: (r["reihe"], r["bereich"], r["jahr"]))
    # Kontrollen: Bereiche ergeben die Summe; keine Jahreslücken
    by = {}
    for r in rows:
        if r["reihe"] == "ausgaben":
            by.setdefault(r["jahr"], {})[r["bereich"]] = r["mrd"]
    for j, b in sorted(by.items()):
        if "TOTAL" not in b or any(x not in b for x in BEREICHE):
            fail(f"{j}: Eurostat-Reihe unvollständig ({', '.join(sorted(b))})")
        s = sum(b[x] for x in BEREICHE)
        if abs(s - b["TOTAL"]) > 0.5:
            fail(f"{j}: Bereiche ergeben {s:.1f}, Summe laut Eurostat {b['TOTAL']:.1f} Mrd. €")
    jahre = sorted(by)
    if jahre != list(range(START, START + len(jahre))):
        fail("Lücke in der Eurostat-Reihe: " + ", ".join(map(str, jahre)))
    old = json.loads(PATH.read_text(encoding="utf-8")) if PATH.exists() else []
    o = {(r["jahr"], r["reihe"], r["bereich"]): r["mrd"] for r in old}
    diffs = [f"bund_gesamt {r['jahr']} {r['bereich']}: bisher {o.get((r['jahr'], r['reihe'], r['bereich']))}, neu {r['mrd']}"
             for r in rows if o.get((r["jahr"], r["reihe"], r["bereich"])) != r["mrd"]]
    print(f"Bund insgesamt (Eurostat S1311): Ausgaben {jahre[0]}–{jahre[-1]}, {len(diffs)} Abweichungen")
    for x in diffs[:40]:
        print("  " + x)
    if check:
        return
    PATH.write_text("[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n]\n", encoding="utf-8")
    bericht = ROOT / "pipeline" / "bericht.md"
    prev = bericht.read_text(encoding="utf-8") if bericht.exists() else ""
    bericht.write_text(prev + "\nBund insgesamt (Eurostat): " + (f"{len(diffs)} Änderungen" if diffs else "keine Änderungen") + "\n\n"
                       + "".join("- " + x + "\n" for x in diffs[:100]), encoding="utf-8")


if __name__ == "__main__":
    main()
