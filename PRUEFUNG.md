# Gegenprobe mit unabhängigen Quellen

Stand: 7. November 2026. Alle Zahlen in Mrd. €. Ziel: Jede Zahlenreihe der Seite einmal mit einer Quelle vergleichen, die nicht unsere Rechnung ist.

## Ergebnis auf einen Blick

| Bereich | Vergleich mit | Ergebnis |
|---|---|---|
| Themen 2015–2025 (Ist), 2026 (Soll) | Funktionen-Ansicht von bundeshaushalt.de (BMF), eigene Neuberechnung | ✅ alle 19 Themen in allen Jahren gleich (Abweichung ≤ 0,003), eine bekannte Ausnahme 2022 (0,071, s. u.) |
| Ausgaben, Steuern, Nettokreditaufnahme 2025 | BMF-Monatsbericht Januar 2026, BMF-Kurzübersicht Februar 2026 | ✅ gleich |
| Soll 2026 | BMF-Kurzübersicht Februar 2026 | ✅ gleich |
| Sondervermögen 2025 (KTF, SVIK) | BMF-Monatsbericht Januar 2026 | ✅ nach Korrektur gleich (s. u.) |
| Defizit Bund insgesamt 2022–2025 | Destatis, Daten zur EU-Haushaltsüberwachung (Stand 21.10.2026) | ✅ gleich |
| Verteidigung | NATO, Defence Expenditure of NATO Countries 2014–2025 | ✅ plausibel, Unterschiede erklärbar |
| Rente | Deutsche Rentenversicherung | ✅ Bundeszuschüsse gleich; Lesehilfe präzisiert |

## Gefundene und behobene Fehler

1. **KTF 2025 zu hoch (37,4 statt 26,6).** In den Ausgaben des Klima- und Transformationsfonds steckte eine „Zuführung an Rücklage“ von 10,8, also Geld, das nicht ausgegeben, sondern zurückgelegt wurde. Das BMF nennt „Programmausgaben im KTF … 26,6 Mrd. Euro“. Korrektur: Zuführungen an Rücklagen (Obergruppe 91) und Tilgungen (Obergruppe 59) zählen nicht mehr als Ausgaben der Sondervermögen, sie werden in der Detailzeile getrennt genannt. Danach stimmen KTF (26,6) und SVIK ohne die Zuweisung an den KTF (14,0, „Bundessäule … 14,0 Mrd. Euro verausgabt“) genau mit dem BMF überein. Sondervermögen 2025 (Ist) insgesamt: 62,4 statt 82,2.
2. **Lesehilfe „Rente“ ungenau.** Dort stand „nur die Zuschüsse des Bundes“. Tatsächlich enthält das Thema auch die Beiträge für Kindererziehungszeiten (19,2), die Erstattung der Grundsicherung im Alter an die Kommunen (11,8), die Knappschaft (4,7) und die Alterssicherung der Landwirte (2,4). Text korrigiert.

## Einzelne Vergleiche

### Themen (Abschnitte 1–3, 6)

bundeshaushalt.de bietet die Ausgaben nach Funktionen über die Schnittstelle der Visualisierung an (`/internalapi/budgetData?…&unit=function`). Daraus wurden die 19 Themen mit derselben Zuordnung (`pipeline/quellen.json`) neu berechnet, unabhängig von den Dateien, aus denen die Seite rechnet.

| Jahr | Summe Schnittstelle | Summe Seite | größte Abweichung je Thema |
|---|---|---|---|
| 2015 Ist | 311,716 | 311,717 | 0,000 |
| 2016 Ist | 317,445 | 317,446 | 0,000 |
| 2017 Ist | 331,039 | 331,036 | 0,003 |
| 2018 Ist | 348,293 | 348,291 | 0,000 |
| 2019 Ist | 357,121 | 357,121 | 0,000 |
| 2020 Ist | 443,432 | 443,431 | 0,000 |
| 2021 Ist | 557,093 | 557,092 | 0,000 |
| 2022 Ist | 481,304 | 481,306 | 0,071 |
| 2023 Ist | 457,663 | 457,664 | 0,000 |
| 2024 Ist | 474,754 | 474,753 | 0,000 |
| 2025 Ist | 495,537 | 495,537 | 0,000 |
| 2026 Soll | 524,540 | 524,540 | 0,000 |

**Bekannte Abweichung 2022:** Ein Titel (Kapitel 0624, Titel 518 02, Mieten im Einheitlichen Liegenschaftsmanagement, 0,07) hat im Haushaltsplan und in der BMF-Ansicht die Funktion 042 (Polizei → „Innere Sicherheit“), in der Haushaltsrechnung die Funktion 014 (→ „Verwaltung“). Die Seite folgt der Haushaltsrechnung. Summen sind gleich.

### Eckwerte 2025 und 2026

| | BMF | Seite |
|---|---|---|
| Ausgaben 2025 (Ist) | 495,5 (vorläufiger Jahresabschluss vom 23.01.2026) | 495,5 |
| Steuereinnahmen 2025 (Ist) | 388,6 | 388,7 |
| Nettokreditaufnahme 2025 (Ist) | 66,9 | 66,9 |
| Ausgaben 2026 (Soll) | 524,5 | 524,5 |
| Nettokreditaufnahme 2026 (Soll) | 98,0 | 98,0 |

Hinweis: Im Monatsbericht nennt das BMF für 2025 Ausgaben von 493,3. Laut Fußnote 2 fehlen darin die Tilgungen aus zurückgezahlten Notlagenmitteln und haushaltstechnische Verrechnungen; der vorläufige Jahresabschluss weist 495,5 aus. Die Seite verwendet wie die Haushaltsrechnung die 495,5.

### Sondervermögen 2025 (Abschnitt 4)

| | BMF-Monatsbericht Januar 2026 | Seite |
|---|---|---|
| SVIK, abgeflossen insgesamt | 24,0 | 24,0 (davon 10,0 an den KTF) |
| SVIK ohne Zuweisung an den KTF | 14,0 | 14,0 |
| KTF, Programmausgaben | 26,6 | 26,6 (nach Korrektur) |
| Kreditbestand SVIK Ende 2025 (BMF-Kurzübersicht) | 24,3 | Kredite 2025: 24,0 |

### Defizit Bund insgesamt (Abschnitt 4)

Destatis, „Daten zur EU-Haushaltsüberwachung“, Rechenstand Notifikation vor dem 1. Oktober 2026, Teilsektor Bund (S1311):

| | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|
| Destatis | −110,94 | −91,52 | −60,95 | −85,27 |
| Seite (Eurostat) | −110,94 | −91,52 | −60,95 | −85,27 |

Ältere Pressemeldungen nennen für 2025 noch 79,6 (erste Berechnung, Destatis Februar 2026). Die 85,4 aus der Pressemitteilung vom April 2026 stammen aus der Finanzstatistik (andere Abgrenzung) und liegen nur zufällig nahe am heutigen Wert.

### Verteidigung

| | 2015 | 2019 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|
| Kernhaushalt, Thema Verteidigung (Ist) | 33,4 | 41,9 | 46,6 | 51,6 | 55,5 | 57,1 |
| Bund insgesamt, COFOG Verteidigung (Eurostat) | 29,2 | 37,9 | 42,6 | 46,7 | 53,3 | 59,3 |
| NATO-Definition | 35,9 | 46,9 | 52,4 | 58,3 | 67,6 | 86,6 (Schätzung) |

Die Reihenfolge ist erklärbar: Die NATO zählt auch das Sondervermögen Bundeswehr (2024 geplant 19,8), Versorgungsausgaben und verteidigungsbezogene Posten anderer Ressorts mit. Die Volkswirtschaftliche Gesamtrechnung bucht Rüstungsgüter erst bei Lieferung, nicht bei Zahlung, und ordnet Versorgung der Sozialen Sicherung zu. Für 2025 weist die NATO für Deutschland noch keinen Wert aus.

### Rente

Die Seite enthält 2025 (Ist) 48,21 + 32,10 + 12,87 = **93,18** an Bundeszuschüssen zur allgemeinen Rentenversicherung (Kapitel 1102, Titel 636 81, 636 83, 636 82). Die Deutsche Rentenversicherung nennt für 2025 „93,2 Milliarden Euro“. Dazu kommen 19,20 Beiträge für Kindererziehungszeiten (Titel 636 84), die die Rentenversicherung als Beiträge, nicht als Zuschüsse zählt.

## Nicht geprüft

- Sondervermögen vor 2023 und als Ist vor 2025: Die amtlichen Dateien enthalten sie nicht; die Seite zeigt diese Jahre nur über Eurostat („Bund insgesamt“).
- Medianeinkommen, Preise, Konsumausgaben: Diese Werte stammen bereits direkt aus Eurostat und Destatis und wurden beim ersten Abgleich Wert für Wert geprüft (alle gleich).
- Die erklärenden Texte (Lesehilfe, Umfang-Kasten) sollte zusätzlich eine fachkundige Person lesen.

## Quellen

- BMF-Monatsbericht Januar 2026, „Abschluss des Bundeshaushalts, des KTF und des SVIK 2025“: https://www.bundesfinanzministerium.de/Monatsberichte/Ausgabe/2026/01/Inhalte/Kapitel-2-Analysen/2-1-abschluss-bundeshaushalt-ktf-svik-2025.html
- BMF, Kurzübersicht Haushalts- und Finanzdaten Februar 2026: https://www.bundesfinanzministerium.de/Content/DE/Standardartikel/Themen/Oeffentliche_Finanzen/Wirtschafts_und_Finanzdaten/Kurzuebersicht_Haushalts_und_Finanzdaten/2026-02-20-kurzuebersicht-februar-2026.html
- bundeshaushalt.de, Schnittstelle der Visualisierung: https://www.bundeshaushalt.de/internalapi/budgetData?year=2025&account=expenses&quota=actual&unit=function
- Destatis, Daten zur EU-Haushaltsüberwachung: https://www.destatis.de/DE/Themen/Wirtschaft/Volkswirtschaftliche-Gesamtrechnungen-Inlandsprodukt/Tabellen/eu-stabilitaetspakt-defizit-deutschland.html
- Destatis, Pressemitteilung Nr. 060 (Februar 2026): https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/02/PD26_060_813.html
- Destatis, Pressemitteilung Nr. 117 (April 2026): https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/04/PD26_117_711.html
- NATO, Defence Expenditure of NATO Countries (2014–2025), Tabelle 1: https://www.nato.int/content/dam/nato/webready/documents/finance/def-exp-2025-en.pdf
- Deutsche Rentenversicherung Mitteldeutschland, Bericht der Vorsitzenden des Vorstands, 08.12.2025: https://www.deutsche-rentenversicherung.de/Mitteldeutschland/DE/Ueber-uns/Selbstverwaltung/Reden/2025_12_VV_Rede_VoVo
