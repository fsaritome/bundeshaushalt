# Übergabe: Bundeshaushalt-Dashboard „Wohin fließt das Geld des Bundes?“

Gestaltet von Ferit Sari Tomé zusammen mit Claude. Stand: 07.11.2026.

## Auftrag für Claude Code

1. Inhalt dieses Ordners in das bestehende, öffentliche Repo `github.com/fsaritome/bundeshaushalt` pushen (Branch `main`). Das Repo wurde auf GitHub angelegt und hat evtl. schon einen ersten Commit: vorher `git pull --rebase` bzw. zusammenführen, nichts überschreiben.
2. GitHub Pages aktivieren: Quelle `main`, Ordner `/ (root)`. Ziel-URL: https://fsaritome.github.io/bundeshaushalt/
3. Prüfen, dass die Seite lädt (alle Abschnitte zeichnen, Antippen zeigt Details, keine Konsolenfehler).
4. Commits mit Autor Ferit Sari Tomé; Copyright und Nennung „Gestaltet von Ferit Sari Tomé zusammen mit Claude“ beibehalten.

Lokal testen: `python3 -m http.server` im Ordner, dann http://localhost:8000 (die Seite lädt die JSON-Dateien per `fetch`, direktes Öffnen der HTML-Datei per `file://` funktioniert daher nicht).

## Was gebaut wurde

Eine neutrale, nachprüfbare Übersicht über den Bundeshaushalt 2015–2026, auf Deutsch, mobilfreundlich, alles antippbar. Grün = gestiegen, Rot = gesunken (ausdrücklich keine Bewertung).

Abschnitte von `index.html`:

1. **Alle Jahre gestapelt:** ein Balken je Jahr, aufgeteilt in alle 19 Themen (keine Sammelkategorie „Übrige“, das war ausdrücklich nicht gewünscht). Legende hebt ein Thema hervor, Antippen eines Balkenstücks zeigt Betrag, Anteil, Veränderung seit 2015 und zum Vorjahr. Umschalter Mrd. € / Anteil 100 %.
2. **Jedes Thema über alle Jahre:** eine Zeile pro Thema, Jahre als Säulen nebeneinander (Säule grün = mehr als Vorjahr, rot = weniger). Umschalter eigene Skala (Verlauf) / gleiche Skala (Größe).
3. **Was sich verändert hat:** divergierende Balken, Veränderung je Thema von 2015 bis zum letzten Jahr, antippbar.
4. **Haushalt im Vergleich zum mittleren Einkommen:**
   - Kacheln: Veränderung seit 2015 von Bundesausgaben, Steuern, Medianeinkommen, Preisen und Realeinkommen.
   - Liniendiagramm Index 2015 = 100 (Ausgaben, Steuern, Medianeinkommen, Preise), antippbar.
   - Veränderung zum Vorjahr als divergierende Balken je Jahr.
   - „Warum sich alles teurer anfühlt“: Preisanstieg 2020–2025 nach Bereichen.
   - „Ausgaben eines Haushalts pro Monat“ (Durchschnitt; einen Median veröffentlicht Destatis nicht).
5. **Alle Zahlen:** Heatmap-Tabelle Thema × Jahr, grün/rot nach Veränderung seit 2015, Zelle antippbar.
6. **Quellen und Methode** mit allen Belegen.

Globaler Schalter oben: „Geplant (Soll), 2015–2026“ oder „Tatsächlich (Ist), 2015–2025“; **Standard ist Tatsächlich**.

## Technik

- Reines HTML/CSS/JS, keine Build-Schritte. d3 v7 vom CDN (cdnjs).
- `dash-shim.js`: kleine Laufzeit, die die Daten aus `data/` lädt und die API bereitstellt, die der Seitencode nutzt: `dash.data(id)`, `dash.calc(id, {inputs, fn})`, `dash.draw(name, fn)`, `dash.onData`, `dash.params/setParams`, `dash.colors`. Ein Element mit `data-draw="name"` wird von der gleichnamigen Zeichenfunktion gefüllt.
- Alle abgeleiteten Zahlen (Anteile, Differenzen, Indizes) entstehen in `dash.calc`-Funktionen im Seitenskript, nicht als feste Zahlen im HTML.
- Hell/Dunkel-Modus über `prefers-color-scheme`.
- Getestet in jsdom: alle Abschnitte zeichnen, alle Klick-Details funktionieren, keine Fehler.

## Daten (`data/`)

| Datei | Inhalt | Quelle |
|---|---|---|
| `themen.json` | Ausgaben je Thema und Jahr 2015–2026, Soll und Ist (Ist bis 2025), Mrd. € | Amtliche Haushaltspläne (Soll) und Haushaltsrechnungen (Ist) des BMF, bundeshaushalt.de, je Titel; über das offene Projekt github.com/eis2k/Bundeshaushaltstracker bezogen (Prüfsummen der Originaldateien in `belege.json`) |
| `jahre.json` | Je Jahr: Ausgaben, Einnahmen, Steuern, Kredite, Rücklagen, sonstige Einnahmen (Soll/Ist); 2027 Regierungsentwurf | wie oben; 2027 laut Deutschem Bundestag |
| `median.json` | Median-Nettoäquivalenzeinkommen 2015–2025, € pro Jahr, Bruch 2020 markiert | Eurostat ilc_di03 (EU-SILC), 2025 Destatis (28.891 €) |
| `preise.json` | Verbraucherpreisindex 2015–2025, 2020 = 100 | Destatis |
| `preise_kategorien.json` | Index 2025 (2020 = 100): gesamt 121,9, Nahrungsmittel 135,9, Haushaltsenergie 146,9, Nettokaltmiete 110,0 | Destatis, Pressemitteilung 16.01.2026 |
| `konsum.json` | Konsumausgaben je Haushalt und Monat (gesamt, Wohnen/Energie, Lebensmittel); 2018 und 2023 aus der EVS | Destatis LWR / EVS |
| `belege.json` | Alle Quellen mit Link, Abrufdatum, Prüfsumme | – |

### Methode

- Kernhaushalt ohne Sondervermögen. Beträge in Mrd. € bzw. Mio. €, deutsche Zahlenformate.
- Themen = Zusammenfassung des amtlichen Funktionenplans; jeder Titel hat genau eine Funktionsnummer, jeder Euro zählt einmal, alle Themen ergeben die Gesamtsumme. Zuordnung: Familie 231/232/237/26/27; Rente 221/222/226/282; Bürgergeld & Arbeitsmarkt 25/211/225/281/285; Gesundheit 224/227/31/284; Sonstiges Soziales 21/223/229/235/236/283/286/287/29; Kriegsfolgen 24; Verteidigung 03; Verkehr 7; Bildung & Forschung 11–16; Kultur 18/19/32; Energie/Klima/Umwelt 33/34/64; Wohnen 4 + 233; Wirtschaft 61–63/65/66/68/69; Landwirtschaft 5; Ausland 02; Sicherheit & Justiz 04/05; Verwaltung 01/06; Zinsen 83; Finanzwirtschaft 81/82/84–89.
- Einnahmen: Steuern = Titel Hauptgruppe 0, Kredite = Titel 32x, Rücklagen = 35x, Rest = sonstige.
- Kontrollen: Summe aller Titel 2026 = 524.540.138 Tsd. € (Haushaltsgesetz 2026, exakt). Nettokreditaufnahme stimmt mit amtlichen Werten (2020 Ist 130,5, 2024 Ist 33,3, 2026 Soll 97,96 Mrd. €).
- Kindergeld erscheint nicht als Ausgabe (wird über die Steuer verrechnet).
- Einkommensreihe: Bruch 2020 (Integration in den Mikrozensus), Erhebungsjahr bezieht sich auf Vorjahreseinkommen.

## Wichtigste Ergebnisse (zur Orientierung)

- Ausgaben tatsächlich 2015 → 2025: 311,7 → 495,5 Mrd. € (+59 %); Steuern +38 %; Medianeinkommen +40 %; Preise +29 %; Realeinkommen +8 % (seit 2019 praktisch null).
- Preise 2020 → 2025: gesamt +22 %, Lebensmittel +36 %, Haushaltsenergie +47 %, Miete Bestand +10 %.
- Haushaltsausgaben je Monat (Durchschnitt): 2017 2.517 € → 2024 3.257 € (+29 %).

## Weitere Version (nur auf claude.ai)

Es gibt zusätzlich ein Dashboard „Bundeshaushalt 2015–2027“ mit Themen-Deep-Dive, Abweichungen (Soll/Ist, eigene Einnahmen/Ausgaben, Steuern geplant/eingenommen), Ministerien, Einzeltiteln ab 50 Mio. € und Posten außerhalb des Kernhaushalts (Sondervermögen, Verpflichtungsermächtigungen, globale Minderausgaben laut Bundesrechnungshof). Es ist nicht Teil dieses Ordners und kann bei Bedarf als zweite Seite ergänzt werden.

## Offene Ideen

- Bevölkerung einbeziehen (Ausgaben pro Kopf).
- Inflationsbereinigte Ansicht der Themen.
- Sozialversicherungen (Rente, Kranken, Pflege) ergänzen.
- 2027 nach Themen, sobald der Haushalt beschlossen und als Datei veröffentlicht ist.
