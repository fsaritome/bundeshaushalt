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
| `data/median.json` | Median-Nettoäquivalenzeinkommen | Eurostat ilc_di03 (EU-SILC), 2025 Destatis |
| `data/preise.json` | Verbraucherpreisindex, 2020 = 100 | Statistisches Bundesamt |
| `data/preise_kategorien.json` | Preise 2025 nach Bereichen | Statistisches Bundesamt, Pressemitteilung vom 16.01.2026 |
| `data/konsum.json` | Konsumausgaben je Haushalt und Monat | Statistisches Bundesamt (Laufende Wirtschaftsrechnungen, EVS) |
| `data/belege.json` | Alle Quellen mit Link und Prüfsumme | – |

Kontrolle: Die Summe aller Haushaltstitel 2026 ergibt exakt die Gesamtsumme im Haushaltsgesetz 2026 (524.540.138 Tsd. €). Die amtlichen Dateien wurden über das offene Projekt [Bundeshaushaltstracker](https://github.com/eis2k/Bundeshaushaltstracker) bezogen, das ihre Prüfsummen festhält.

Hinweise: Kernhaushalt ohne Sondervermögen. Das Kindergeld erscheint nicht als Ausgabe, weil es über die Steuer verrechnet wird. 2020 gibt es einen Bruch in der Einkommensreihe.

## Lokal ansehen

```
python3 -m http.server
```

und dann `http://localhost:8000` öffnen.

## Quellen und Lizenzen

- **Bundeshaushalt:** Quelle: Bundesministerium der Finanzen, [bundeshaushalt.de](https://www.bundeshaushalt.de); Abgleich mit dem Haushaltsgesetz 2026 ([gesetze-im-internet.de](https://www.gesetze-im-internet.de/hg_2026/anlage.html)).
- **Aufbereitung der amtlichen Dateien:** bezogen über das offene Projekt [Bundeshaushaltstracker](https://github.com/eis2k/Bundeshaushaltstracker) (eis2k). Vielen Dank.
- **Entwurf 2027:** Deutscher Bundestag (bundestag.de, hib, mitmischen.de); ergänzend Bundesrechnungshof (über Table.Media), KfW Research, Subventionsbericht der Bundesregierung (berichtet vom VDIV).
- **Statistisches Bundesamt:** © Statistisches Bundesamt (Destatis), 2026, [Datenlizenz Deutschland – Namensnennung – Version 2.0](https://www.govdata.de/dl-de/by-2-0). VPI-Jahreswerte zusammengestellt vom AGV, EVS-Werte berichtet vom VDIV.
- **Eurostat:** ilc_di03 (EU-SILC), © Europäische Union, Weiterverwendung gemäß der [Eurostat-Urheberrechtsrichtlinie](https://ec.europa.eu/eurostat/about-us/policies/copyright); abgerufen über [DBnomics](https://db.nomics.world).
- **Software:** [D3.js](https://d3js.org) (© Mike Bostock, ISC-Lizenz), über cdnjs.

Unabhängiges Projekt, von keiner der genannten Stellen herausgegeben oder unterstützt. Themenzuordnung, Indizes und Veränderungen sind eigene Berechnungen.

## Lizenz

Code: MIT, © 2026 Ferit Sari Tomé. Die Daten stammen aus den oben genannten Quellen und unterliegen deren Nutzungsbedingungen.
