# Wohin fließt das Geld des Bundes?

Der Bundeshaushalt 2015–2026, nachprüfbar und neutral aufbereitet: alle Ausgaben des Bundes nach Themen, geplant (Soll) und tatsächlich (Ist), im Vergleich zum mittleren Einkommen, zu den Preisen und zu den Ausgaben der Haushalte.

**Gestaltet von Ferit Sari Tomé zusammen mit Claude.**

## Was die Seite zeigt

1. **Alle Jahre gestapelt:** jedes Jahr als ein Balken, aufgeteilt in alle 19 Themen.
2. **Jedes Thema über alle Jahre:** ein Thema pro Zeile, die Jahre nebeneinander.
3. **Was sich verändert hat:** Zuwachs oder Rückgang je Thema seit 2015.
4. **Haushalt im Vergleich zum mittleren Einkommen:** Bundesausgaben, Steuern, Medianeinkommen und Preise als Index, Veränderung zum Vorjahr, Preisanstieg nach Bereichen und Ausgaben eines Haushalts pro Monat.
5. **Alle Zahlen:** jedes Thema in jedem Jahr als Tabelle.

Grün heißt gestiegen, Rot heißt gesunken. Das ist keine Bewertung.

## Daten

| Datei | Inhalt | Quelle |
|---|---|---|
| `data/themen.json` | Ausgaben je Thema und Jahr, Soll und Ist, Mrd. € | Amtliche Haushaltspläne und Haushaltsrechnungen des Bundesfinanzministeriums ([bundeshaushalt.de](https://www.bundeshaushalt.de/DE/Download-Portal/download-portal.html)), Themen nach dem amtlichen Funktionenplan zusammengefasst |
| `data/jahre.json` | Gesamtausgaben, Steuern, Kredite je Jahr | wie oben; 2027 Regierungsentwurf laut Deutschem Bundestag |
| `data/median.json` | Median-Nettoäquivalenzeinkommen | Eurostat ilc_di03 (EU-SILC); 2025 identisch mit Destatis |
| `data/preise.json` | Verbraucherpreisindex, 2020 = 100 | Statistisches Bundesamt |
| `data/preise_kategorien.json` | Preise 2025 nach Bereichen | Statistisches Bundesamt, Pressemitteilung vom 16.01.2026 |
| `data/konsum.json` | Konsumausgaben je Haushalt und Monat | Statistisches Bundesamt (Laufende Wirtschaftsrechnungen, EVS) |
| `data/belege.json` | Alle Quellen mit Link und Prüfsumme | – |

Kontrolle: Die Summe aller Haushaltstitel 2026 ergibt exakt die Gesamtsumme im Haushaltsgesetz 2026 (524.540.138 Tsd. €). Die amtlichen Dateien wurden zuerst über das offene Projekt [Bundeshaushaltstracker](https://github.com/eis2k/Bundeshaushaltstracker) bezogen, das ihre Prüfsummen festhält; das eigene Skript in `pipeline/` rechnet sie heute direkt nach.

Hinweise:

- **Soll** = endgültiges Soll einschließlich Nachtragshaushalten, wie in der Haushaltsrechnung ausgewiesen; für Jahre ohne Haushaltsrechnung der beschlossene Haushaltsplan. **Ist** = Haushaltsrechnung.
- **Kernhaushalt:** Die Anlagen zum Haushaltsplan (Kapitel xx90–xx99: Sondervermögen, EU-Eigenmittel, nachgeordnete Anstalten) sind nicht enthalten.
- Das Kindergeld erscheint nicht als Ausgabe, weil es über die Steuer verrechnet wird. 2020 gibt es einen Bruch in der Einkommensreihe.

## Daten aktualisieren

Zwei Skripte rechnen die Daten aus den amtlichen Quellen neu:

- `pipeline/haushalt.py`: Haushaltsdateien von bundeshaushalt.de (Quellen in `pipeline/quellen.json`; neue Jahre werden über das Dateimuster `HH_<Jahr>_ALL.csv` bzw. `rechnung_<Jahr>.xml` gefunden). Bricht ab, wenn ein Titel keinem Thema zugeordnet werden kann oder die Kontrollsumme 2026 nicht stimmt.
- `pipeline/median.py`: Medianeinkommen über die Eurostat-Schnittstelle.

Bei Änderungen entsteht ein Pull Request mit einer Liste der geänderten Werte. Online geht erst, was jemand prüft und zusammenführt.

**Haushaltsdaten lokal:** bundeshaushalt.de weist Anfragen von GitHub-Servern ab (HTTP 503). Deshalb lokal ausführen, z. B. nach Veröffentlichung einer neuen Haushaltsrechnung oder eines neuen Haushalts (braucht git, Python 3 und die GitHub-CLI `gh`):

```
bash pipeline/aktualisieren.sh
```

**Automatisch auf GitHub:** Die Action `.github/workflows/daten.yml` läuft am 5. jedes Monats (und per Knopf unter *Actions → Daten aktualisieren → Run workflow*). Sie gleicht das Medianeinkommen ab und versucht die Haushaltsdaten; ist bundeshaushalt.de nicht erreichbar, steht eine Warnung im Lauf, Datenfehler lassen ihn scheitern. Damit sie Pull Requests öffnen darf, muss unter *Settings → Actions → General* „Allow GitHub Actions to create and approve pull requests“ aktiviert sein.

Verbraucherpreise (`preise.json`, `preise_kategorien.json`) und Haushaltsausgaben (`konsum.json`) werden von Hand gepflegt: Destatis stellt sie maschinenlesbar nur über eine Schnittstelle mit Anmeldung bereit.

Lokal prüfen, ohne etwas zu schreiben:

```
python3 pipeline/haushalt.py --check
python3 pipeline/median.py --check
```

Wenn ein neues Haushaltsjahr dazukommt, nennen Seite und Trends die Jahre automatisch, nur Texte mit festen Jahreszahlen (z. B. „2015–2026“ im Kopf) müssen im Pull Request angepasst werden.

## Lokal ansehen

```
python3 -m http.server
```

und dann `http://localhost:8000` öffnen.

## Quellen und Lizenzen

- **Bundeshaushalt:** Quelle: Bundesministerium der Finanzen, [bundeshaushalt.de](https://www.bundeshaushalt.de); Abgleich mit dem Haushaltsgesetz 2026 ([gesetze-im-internet.de](https://www.gesetze-im-internet.de/hg_2026/anlage.html)).
- **Aufbereitung der amtlichen Dateien:** zuerst bezogen über das offene Projekt [Bundeshaushaltstracker](https://github.com/eis2k/Bundeshaushaltstracker) (eis2k). Vielen Dank.
- **Entwurf 2027** (in Daten und Einzelnachweisen, auf der Seite noch nicht als Grafik): Deutscher Bundestag (bundestag.de, hib, mitmischen.de); ergänzend Bundesrechnungshof (über Table.Media), KfW Research, Subventionsbericht der Bundesregierung (berichtet vom VDIV).
- **Statistisches Bundesamt:** © Statistisches Bundesamt (Destatis), 2026, [Datenlizenz Deutschland – Namensnennung – Version 2.0](https://www.govdata.de/dl-de/by-2-0). VPI-Jahreswerte zusammengestellt vom AGV, EVS-Werte berichtet vom VDIV.
- **Eurostat:** ilc_di03 (EU-SILC), © Europäische Union, Weiterverwendung gemäß der [Eurostat-Urheberrechtsrichtlinie](https://ec.europa.eu/eurostat/about-us/policies/copyright); zuerst abgerufen über [DBnomics](https://db.nomics.world), inzwischen direkt über die Eurostat-Schnittstelle.
- **Software:** [D3.js](https://d3js.org) (© Mike Bostock, ISC-Lizenz, siehe `vendor/D3-LICENSE.txt`), Version 7.9.0, liegt in `vendor/`, damit die Seite ohne externe Abrufe funktioniert.

Unabhängiges Projekt, von keiner der genannten Stellen herausgegeben oder unterstützt. Themenzuordnung, Indizes und Veränderungen sind eigene Berechnungen.

## Lizenz

Code: MIT, © 2026 Ferit Sari Tomé. Die Daten stammen aus den oben genannten Quellen und unterliegen deren Nutzungsbedingungen.
