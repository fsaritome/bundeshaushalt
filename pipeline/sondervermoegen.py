"""Baut data/sondervermoegen.json aus den Anlagen zum Haushaltsplan (bundeshaushalt.de).

Die Wirtschaftspläne der Sondervermögen stehen als Kapitel "Anlage …" in den Haushaltsdateien:
im Haushaltsplan (CSV) ab 2023, in der Haushaltsrechnung (XML) nur in einzelnen Jahren. Für die
Haushaltsrechnung fehlen dort die Kapiteltexte, daher kommen die Namen aus dem Plan desselben Jahres.

    python pipeline/sondervermoegen.py          # laden, prüfen, schreiben
    python pipeline/sondervermoegen.py --check  # nur vergleichen

Je Kapitel und Jahr: Ausgaben, davon Zuweisungen an andere Sondervermögen, und die Finanzierung
(Kredite, Zuweisungen aus dem Kernhaushalt, aus anderen Sondervermögen, eigene Einnahmen, Rücklage).
Kontrolle: Was ein Sondervermögen an andere überweist, muss dort als Einnahme ankommen.
"""
import csv
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import haushalt as h  # noqa: E402

PATH = h.DATA / "sondervermoegen.json"
SOLL_AB = 2023  # erst ab diesem Plan enthalten die Haushaltsdateien die Anlagen


def art_of(text):
    """Sondervermögen = Kapitel mit Wirtschaftsplan (dazu gehören auch Fonds, deren Name das Wort
    'Sondervermögen' nicht enthält, z. B. der Wirtschaftsstabilisierungsfonds)."""
    t = norm(text)
    if "Eigenmittel der EU" in t:
        return "eu_eigenmittel"
    if "Wirtschaftsplan" in t or "Sondervermögen" in t or "Transformationsfonds" in t:
        return "sondervermoegen"
    return "weitere"


def norm(text):
    """Geschützte Leerzeichen und Zeilenumbrüche in den amtlichen Texten vereinheitlichen."""
    return re.sub(r"\s+", " ", text or "").strip()


def clean_name(text):
    t = re.sub(r"^Anlage\s*\d*\s*", "", norm(text)).strip()
    t = re.sub(r"^(Wirtschaftsplan|Verwaltungshaushaltsplan)\s+(des|der)\s+", "", t)
    t = re.sub(r"\(\d{4}\)", "", t).replace('"', "").strip(" -")
    t = re.sub(r"^Sondervermögens\s+", "Sondervermögen ", t)
    t = re.sub(r"\s+", " ", t)
    return t[:1].upper() + t[1:]


SV_NAME = r"(das Sondervermögen|den Klima- und Transformationsfonds|dem Sondervermögen|dem Klima- und Transformationsfonds)"


def an_sv_text(text):
    """Ausgabe, die an ein anderes Sondervermögen des Bundes geht (nicht z. B. an den
    Transformationsfonds im Krankenhausbereich, der kein Sondervermögen in den Anlagen ist)."""
    return re.search(r"\ban " + SV_NAME, text) is not None


def von_sv_text(text):
    return re.search(r"\baus " + SV_NAME, text) is not None


def einnahme_typ(titel, text):
    if titel.startswith("32"):
        return "kredite"
    if titel.startswith("35"):
        return "ruecklage"
    if von_sv_text(text):
        return "von_sv"
    if re.search(r"des Bundes\b|Bundeshaushalt|aus dem Haushalt des Bundes", text):
        return "vom_kern"
    return "eigene"


def leer(jahr, wert, kap, name, art):
    return {"jahr": jahr, "wert": wert, "kapitel": kap, "name": name, "art": art, "ausgaben": 0.0, "an_sv": 0.0,
            "an_ruecklage": 0.0, "tilgung": 0.0,
            "kredite": 0.0, "vom_kern": 0.0, "von_sv": 0.0, "eigene": 0.0, "ruecklage": 0.0}


def add(rows, key, base, ea, titel, text, betrag_tsd):
    """Ausgaben: alle Ausgabetitel. Davon getrennt ausgewiesen, weil sie kein Geldabfluss für Aufgaben sind
    (wie in der Abgrenzung des BMF): Zuführungen an Rücklagen (Obergruppe 91) und Tilgungen (Obergruppe 59);
    außerdem Zahlungen an andere Sondervermögen (sonst doppelt gezählt)."""
    r = rows.setdefault(key, base())
    text = norm(text)
    v = betrag_tsd / 1e6  # Mrd. €
    if ea == "A":
        r["ausgaben"] += v
        if titel.startswith("91"):
            r["an_ruecklage"] += v
        elif titel.startswith("59"):
            r["tilgung"] += v
        elif an_sv_text(text):
            r["an_sv"] += v
    else:
        r[einnahme_typ(titel, text)] += v


def from_plan(jahr, rel):
    body = h.fetch(rel)
    if body is None:
        h.fail(f"{jahr}: Datei fehlt: {rel}")
    rows_csv = list(csv.reader(io.StringIO(body[0].decode("utf-8-sig")), delimiter=";"))
    head = [x.strip().lower() for x in rows_csv[0]]
    ix = {k: head.index(k) for k in ("einzelplan", "kapitel", "kapitel-text", "titel", "titel-text", "soll")}
    ie = head.index("einnahmen-ausgaben") if "einnahmen-ausgaben" in head else head.index("einahmen-ausgaben")
    out, names = {}, {}
    for r in rows_csv[1:]:
        if len(r) <= ix["soll"]:
            continue
        kap = r[ix["kapitel"]].strip()
        kap = kap if len(kap) == 4 else r[ix["einzelplan"]].strip().zfill(2) + kap.zfill(2)
        ktext = r[ix["kapitel-text"]]
        if not h.is_anlage(ktext, kap):
            continue
        names[kap] = ktext
        add(out, kap, lambda: leer(jahr, "soll", kap, clean_name(ktext), art_of(ktext)), r[ie].strip().upper(),
            r[ix["titel"]].strip(), r[ix["titel-text"]], h.num(r[ix["soll"]]))
    return out, names


def from_rechnung(jahr, rel, names):
    body = h.fetch(rel)
    if body is None:
        h.fail(f"{jahr}: Datei fehlt: {rel}")
    root = ET.fromstring(body[0])
    out = {}
    for kap in root.iter("kapitel"):
        nr = kap.get("nr")
        if not h.is_anlage(None, nr):
            continue
        if nr not in names:
            h.fail(f"{jahr}: Kapitel {nr} in der Haushaltsrechnung, aber nicht im Haushaltsplan {jahr} – Name unbekannt")
        ktext = names[nr]
        for t in kap.iter("titel"):
            ea = "E" if t.get("ein-aus-art") == "einnahmen" else "A"
            i = t.find("ist")
            add(out, nr, lambda: leer(jahr, "ist", nr, clean_name(ktext), art_of(ktext)), ea, t.get("nr", ""),
                t.findtext("text") or "", h.num(i.get("wert")) / 1000 if i is not None else 0.0)
    return out


def check_transfers(rows):
    """Zuweisungen zwischen Sondervermögen müssen sich je Jahr und Wert ausgleichen (±0,05 Mrd. €)."""
    by = {}
    for r in rows:
        if r["art"] != "sondervermoegen":
            continue
        k = (r["jahr"], r["wert"])
        a, e = by.get(k, (0.0, 0.0))
        by[k] = (a + r["an_sv"], e + r["von_sv"])
    for (j, w), (a, e) in sorted(by.items()):
        if abs(a - e) > 0.05:
            h.fail(f"{j} {w}: Sondervermögen zahlen {a:.2f} Mrd. € an andere Sondervermögen, erhalten aber {e:.2f} Mrd. €")


def main():
    check = "--check" in sys.argv
    years = h.discover(h.CFG)
    rows = []
    for y, src in years.items():
        if y < SOLL_AB:
            continue
        plan, names = from_plan(y, src["soll"])
        rows += plan.values()
        if "ist" in src:
            rows += from_rechnung(y, src["ist"], names).values()
    rows = [r for r in rows if abs(r["ausgaben"]) > 0.0005 or abs(r["kredite"]) > 0.0005]
    for r in rows:
        for k in ("ausgaben", "an_sv", "an_ruecklage", "tilgung", "kredite", "vom_kern", "von_sv", "eigene", "ruecklage"):
            r[k] = round(r[k], 3)
    rows.sort(key=lambda r: (r["jahr"], r["wert"], r["art"], -r["ausgaben"]))
    check_transfers(rows)
    old = json.loads(PATH.read_text(encoding="utf-8")) if PATH.exists() else []
    o = {(r["jahr"], r["wert"], r["kapitel"]): r for r in old}
    diffs = []
    for r in rows:
        p = o.get((r["jahr"], r["wert"], r["kapitel"]))
        if p is None:
            diffs.append(f"sondervermögen neu: {r['jahr']} {r['wert']} {r['name']}: {r['ausgaben']:.3f} Mrd. €")
        elif abs(p["ausgaben"] - r["ausgaben"]) > 0.0015 or abs(p["kredite"] - r["kredite"]) > 0.0015:
            diffs.append(f"sondervermögen {r['jahr']} {r['wert']} {r['name']}: bisher {p['ausgaben']}, neu {r['ausgaben']}")
    print(f"Sondervermögen/Anlagen: {len(rows)} Zeilen, {len(diffs)} Abweichungen")
    for d in diffs[:80]:
        print("  " + d)
    if check:
        return
    h.write_rows(PATH, rows)
    bericht = h.ROOT / "pipeline" / "bericht.md"
    prev = bericht.read_text(encoding="utf-8") if bericht.exists() else ""
    bericht.write_text(prev + "\nSondervermögen: " + (f"{len(diffs)} Änderungen" if diffs else "keine Änderungen") + "\n\n"
                       + "".join("- " + d + "\n" for d in diffs[:200]), encoding="utf-8")


if __name__ == "__main__":
    main()
