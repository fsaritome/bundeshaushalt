"""Baut data/themen.json und data/jahre.json aus den amtlichen Dateien von bundeshaushalt.de.

Nur Python-Standardbibliothek. Aufruf aus dem Repo-Hauptordner:

    python pipeline/haushalt.py            # laden, rechnen, prüfen, schreiben
    python pipeline/haushalt.py --check    # nur rechnen und mit den vorhandenen Dateien vergleichen

Quellen und Regeln stehen in pipeline/quellen.json. Das Skript bricht ab (Exit-Code 1), wenn
eine Datei nicht lesbar ist, ein Titel keinem Thema zugeordnet werden kann oder eine Kontrollsumme
nicht stimmt. Dann wird nichts geschrieben.
"""
import csv
import hashlib
import io
import json
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CACHE = ROOT / "pipeline" / ".cache"
CFG = json.loads((ROOT / "pipeline" / "quellen.json").read_text(encoding="utf-8"))
BASE = "https://www.bundeshaushalt.de/static/daten/"
UA = {"User-Agent": "bundeshaushalt-dashboard-datenabgleich (github.com/fsaritome/bundeshaushalt)"}


def fail(msg):
    print("FEHLER: " + msg, file=sys.stderr)
    sys.exit(1)


NICHT_ERREICHBAR = 3  # Exit-Code: Quelle nicht erreichbar (kein Datenfehler)


def fail_net(msg):
    print("NICHT ERREICHBAR: " + msg, file=sys.stderr)
    sys.exit(NICHT_ERREICHBAR)


def fetch(rel, probe=False):
    """Lädt eine Datei (mit Zwischenspeicher), gibt (bytes, sha256) zurück, None wenn es sie nicht gibt.
    probe=True: Suche nach noch nicht veröffentlichten Jahren; dauerhafte Serverfehler gelten dann als 'noch nicht da'."""
    CACHE.mkdir(parents=True, exist_ok=True)
    local = CACHE / rel.replace("/", "_")
    if not local.exists():
        body = None
        for attempt in range(5):
            req = urllib.request.Request(BASE + rel, headers=UA)
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    body = r.read()
                break
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return None
                if e.code in (429, 500, 502, 503, 504) and attempt < (1 if probe else 4):
                    wait = 15 * (attempt + 1)
                    print(f"  {rel}: HTTP {e.code}, neuer Versuch in {wait} s", file=sys.stderr)
                    time.sleep(wait)
                    continue
                if probe:
                    print(f"  WARNUNG: {rel}: HTTP {e.code}, als nicht vorhanden behandelt", file=sys.stderr)
                    return None
                fail_net(f"{rel}: HTTP {e.code} von bundeshaushalt.de (nach {attempt + 1} Versuchen)")
            except urllib.error.URLError as e:
                if attempt < 4:
                    time.sleep(15 * (attempt + 1))
                    continue
                fail_net(f"{rel}: {e.reason}")
        # Die Website liefert für fehlende Dateien teils eine HTML-Seite statt 404.
        if body[:200].lstrip().lower().startswith((b"<!doctype html", b"<html")):
            return None
        local.write_bytes(body)
    body = local.read_bytes()
    return body, hashlib.sha256(body).hexdigest()


def num(s):
    s = (s or "").strip().replace(".", "").replace(",", ".")
    if s.endswith("-"):  # ältere Dateien schreiben negative Beträge mit nachgestelltem Minus
        s = "-" + s[:-1]
    return float(s) if s else 0.0


def is_anlage(kapitel_text, kapitel_nr=""):
    """Anlagen zum Haushaltsplan (Kapitel xx90–xx99, Text 'Anlage …'): Wirtschaftspläne der
    Sondervermögen, EU-Eigenmittel und Haushalte nachgeordneter Anstalten. Sie gehören nicht zum
    Kernhaushalt (Kontrolle: Summe 2026 = Haushaltsgesetz). Die XML-Dateien nennen keinen Kapiteltext,
    dort entscheidet die Nummer."""
    if (kapitel_text or "").strip().lower().startswith("anlage"):
        return True
    nr = (kapitel_nr or "").strip()
    return len(nr) == 4 and nr[2] == "9"


def read_soll(body):
    """Soll-CSV -> Liste (art 'E'/'A', titel, funktion, betrag in Tsd. €)."""
    text = body.decode("utf-8-sig", errors="strict")
    rows = list(csv.reader(io.StringIO(text), delimiter=";"))
    head = [h.strip().lower() for h in rows[0]]

    def col(*names):
        for n in names:
            if n in head:
                return head.index(n)
        fail("Spalte fehlt in Soll-Datei: " + "/".join(names) + " (gefunden: " + ", ".join(head) + ")")

    i_art = col("einnahmen-ausgaben", "einahmen-ausgaben")
    i_tit, i_fkt, i_soll = col("titel"), col("funktion"), col("soll")
    i_ktx, i_kap, i_epl = col("kapitel-text"), col("kapitel"), col("einzelplan")
    out = []
    for r in rows[1:]:
        if len(r) <= i_soll or not r[i_tit].strip():
            continue
        kap = r[i_kap].strip()
        kap = kap if len(kap) == 4 else r[i_epl].strip().zfill(2) + kap.zfill(2)
        if is_anlage(r[i_ktx], kap):
            continue
        out.append((r[i_art].strip().upper(), r[i_tit].strip(), r[i_fkt].strip().zfill(3), num(r[i_soll])))
    return out


def read_ist(body):
    """Haushaltsrechnung-XML -> (soll_liste, ist_liste), Beträge in Tsd. €."""
    root = ET.fromstring(body)
    soll, ist = [], []
    core = []
    for kap in root.iter("kapitel"):
        if not is_anlage(kap.findtext("text"), kap.get("nr")):
            core.extend(kap.iter("titel"))
    for t in core:
        art = "E" if t.get("ein-aus-art") == "einnahmen" else "A"
        s, i = t.find("soll"), t.find("ist")
        key = (art, t.get("nr", ""), (t.get("fkt") or "").zfill(3))
        soll.append(key + (num(s.get("wert")) / 1000 if s is not None else 0.0,))
        ist.append(key + (num(i.get("wert")) / 1000 if i is not None else 0.0,))
    return soll, ist


def thema_of(fkt, rules):
    best = None
    for prefix, thema in rules:
        if fkt.startswith(prefix) and (best is None or len(prefix) > len(best[0])):
            best = (prefix, thema)
    return best[1] if best else None


def sum_themen(titel, rules, year, art_label):
    sums, unmapped = {}, {}
    for art, _tit, fkt, v in titel:
        if art != "A":
            continue
        th = thema_of(fkt, rules)
        if th is None:
            unmapped[fkt] = unmapped.get(fkt, 0) + v
            continue
        sums[th] = sums.get(th, 0) + v
    bad = {k: v for k, v in unmapped.items() if abs(v) > 0}
    if bad:
        fail(f"{year} {art_label}: Funktionen ohne Thema: " + ", ".join(f"{k} ({v:,.0f} Tsd. €)" for k, v in sorted(bad.items())))
    return sums


def einnahmen(titel):
    e = {"steuern": 0.0, "kredite": 0.0, "ruecklage": 0.0, "sonstige": 0.0}
    for art, tit, _fkt, v in titel:
        if art != "E":
            continue
        if tit.startswith("0"):
            e["steuern"] += v
        elif tit.startswith("32"):
            e["kredite"] += v
        elif tit.startswith("35"):
            e["ruecklage"] += v
        else:
            e["sonstige"] += v
    return e


def discover(cfg):
    """Findet neue Jahre nach den Namensmustern, die seit 2024 gelten."""
    years = {int(y): dict(v) for y, v in cfg["jahre"].items()}
    # Erst prüfen, ob die Quelle überhaupt erreichbar ist (eine sicher vorhandene Datei),
    # damit ein gesperrter Zugang nicht als "neues Jahr noch nicht veröffentlicht" missverstanden wird.
    fetch(years[max(years)]["soll"])
    nxt = max(years) + 1
    while True:
        soll_rel = cfg["muster"]["soll"].format(jahr=nxt)
        if fetch(soll_rel, probe=True) is None:
            break
        years[nxt] = {"soll": soll_rel}
        nxt += 1
    for y in years:
        if "ist" not in years[y]:
            ist_rel = cfg["muster"]["ist"].format(jahr=y)
            if y < date.today().year and fetch(ist_rel, probe=True) is not None:
                years[y]["ist"] = ist_rel
    return dict(sorted(years.items()))


def build():
    rules = [(p, th) for th, ps in CFG["themen"].items() for p in ps["funktionen"]]
    names = {th: v["name"] for th, v in CFG["themen"].items()}
    years = discover(CFG)
    themen, jahre, belege = [], [], []
    for y, src in years.items():
        ist = None
        if "ist" not in src:
            got = fetch(src["soll"])
            if got is None:
                fail(f"{y}: Soll-Datei nicht gefunden: {src['soll']}")
            soll = read_soll(got[0])
            belege.append({"jahr": y, "art": "Soll (Haushaltsplan)", "url": BASE + src["soll"], "sha256": got[1]})
        else:
            got_i = fetch(src["ist"])
            if got_i is None:
                fail(f"{y}: Ist-Datei nicht gefunden: {src['ist']}")
            # Die Haushaltsrechnung enthält das endgültige Soll einschließlich aller Nachtragshaushalte.
            soll, ist = read_ist(got_i[0])
            belege.append({"jahr": y, "art": "Soll und Ist (Haushaltsrechnung)", "url": BASE + src["ist"], "sha256": got_i[1]})
        ts = sum_themen(soll, rules, y, "Soll")
        ti = sum_themen(ist, rules, y, "Ist") if ist else None
        for th in CFG["themen"]:
            themen.append({"jahr": y, "thema": th, "name": names[th], "soll": round(ts.get(th, 0) / 1e6, 3),
                           "ist": round(ti.get(th, 0) / 1e6, 3) if ti else None})
        es = einnahmen(soll)
        ei = einnahmen(ist) if ist else None
        row = {"jahr": y, "ausgaben_soll": round(sum(ts.values()) / 1e6, 3),
               "ausgaben_ist": round(sum(ti.values()) / 1e6, 3) if ti else None,
               "einnahmen_soll": round(sum(es.values()) / 1e6, 3),
               "einnahmen_ist": round(sum(ei.values()) / 1e6, 3) if ei else None}
        for k in ("steuern", "kredite", "ruecklage", "sonstige"):
            row[k + "_soll"] = round(es[k] / 1e6, 3)
            row[k + "_ist"] = round(ei[k] / 1e6, 3) if ei else None
        jahre.append(row)
        # Kontrolle: Gesamtsumme laut Haushaltsgesetz, wo bekannt (Tsd. €)
        soll_tsd = sum(ts.values())
        ref = CFG.get("kontrollen", {}).get(str(y))
        if ref and abs(soll_tsd - ref) > 1:
            fail(f"{y}: Summe aller Ausgabetitel {soll_tsd:,.0f} Tsd. € ≠ Haushaltsgesetz {ref:,.0f} Tsd. €")
    return themen, jahre, belege


def merge_jahre(new, old):
    """Behält Jahre und Felder, die nicht aus den Dateien kommen (z. B. 2027 Regierungsentwurf)."""
    by = {r["jahr"]: r for r in old}
    for r in new:
        by[r["jahr"]] = {**by.get(r["jahr"], {}), **r}
    return [by[k] for k in sorted(by)]


def compare(label, new, old, keys, fields, tol=0.0015):
    o = {tuple(r[k] for k in keys): r for r in old}
    diffs = []
    for r in new:
        k = tuple(r[x] for x in keys)
        if k not in o:
            diffs.append(f"{label} neu: {k}")
            continue
        for f in fields:
            a, b = r.get(f), o[k].get(f)
            if (a is None) != (b is None) or (a is not None and abs(a - b) > tol):
                diffs.append(f"{label} {k} {f}: bisher {b}, neu {a}")
    return diffs


def main():
    check = "--check" in sys.argv
    themen, jahre, belege = build()
    old_t = json.loads((DATA / "themen.json").read_text(encoding="utf-8"))
    old_j = json.loads((DATA / "jahre.json").read_text(encoding="utf-8"))
    jahre_m = merge_jahre(jahre, old_j)
    diffs = compare("themen", themen, old_t, ("jahr", "thema"), ("soll", "ist"))
    diffs += compare("jahre", jahre, old_j, ("jahr",), [k for k in jahre[0] if k != "jahr"])
    print(f"{len(themen)} Themen-Werte, {len(jahre)} Jahre, {len(diffs)} Abweichungen zu den bisherigen Dateien")
    for d in (diffs if check else diffs[:60]):
        print("  " + d)
    if check:
        return
    write_rows(DATA / "themen.json", themen)
    write_rows(DATA / "jahre.json", jahre_m)
    update_belege(belege)
    report(diffs)


def write_rows(path, rows):
    """Eine Zeile je Datensatz, damit Änderungen im Pull Request gut lesbar sind."""
    path.write_text("[\n" + ",\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n]\n", encoding="utf-8")


def update_belege(dateien):
    """Trägt Prüfsumme und Abrufdatum der geladenen Dateien in data/belege.json ein, neue Dateien hinten an."""
    path = DATA / "belege.json"
    belege = json.loads(path.read_text(encoding="utf-8"))
    by_url = {b["url"]: b for b in belege}
    heute = date.today().isoformat()
    for d in dateien:
        b = by_url.get(d["url"])
        if b is None:
            b = {"jahr": d["jahr"], "art": d["art"], "url": d["url"], "abgerufen": "", "sha256": None,
                 "hinweis": "Amtliche Datei des Bundesfinanzministeriums (bundeshaushalt.de)",
                 "nr": max(x["nr"] for x in belege) + 1}
            belege.append(b)
        if b.get("sha256") != d["sha256"]:
            b["sha256"] = d["sha256"]
            b["abgerufen"] = heute
        elif not b.get("abgerufen"):
            b["abgerufen"] = heute
    write_rows(path, belege)


def report(diffs):
    """Kurzbericht für den Pull Request (pipeline/bericht.md, nicht im Repo)."""
    lines = ["Haushaltsdaten: " + (f"{len(diffs)} geänderte Werte" if diffs else "keine Änderungen"), ""]
    lines += ["- " + d for d in diffs[:200]]
    (ROOT / "pipeline" / "bericht.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
