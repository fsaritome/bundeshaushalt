// Abschnitt 4 „Das ganze Bild“, Umfang-Kasten und Lesehilfe.
// Nutzt die Hilfsfunktionen aus dem Seitenskript (mk, mrd, signed, spct, pf, nf1, colored, colorOf, dash, d3).
(function () {
  const SV_SPALTEN = [
    { jahr: 2023, wert: 'soll', label: '2023 geplant' },
    { jahr: 2024, wert: 'soll', label: '2024 geplant' },
    { jahr: 2025, wert: 'soll', label: '2025 geplant' },
    { jahr: 2025, wert: 'ist', label: '2025 tatsächlich' },
    { jahr: 2026, wert: 'soll', label: '2026 geplant' }
  ];
  const kurz = (name) => name.replace(/^Sondervermögen\s+/, '').replace(/\s*-\s*Anlage.*$/, '');

  dash.calc('sv_jahre', {
    inputs: ['sondervermoegen', 'jahre'], title: 'Sondervermögen je Jahr',
    description: 'Je Jahr und Wertart: Ausgaben der Sondervermögen ohne Zahlungen zwischen Sondervermögen (netto), Finanzierung, EU-Eigenmittel und Kernhaushalt zum Vergleich.',
    fn: (sv, jahre) => {
      const spalten = [];
      const groesse = new Map();
      // neueste verfügbare Spalten zuerst bestimmen, dann in zeitlicher Reihenfolge ausgeben
      const vorhanden = new Set(sv.map((r) => r.jahr + r.wert));
      SV_SPALTEN.filter((s) => vorhanden.has(s.jahr + s.wert)).forEach((s) => {
        const rows = sv.filter((r) => r.jahr === s.jahr && r.wert === s.wert);
        const fonds = rows.filter((r) => r.art === 'sondervermoegen').map((r) => ({ ...r, netto: r.ausgaben - r.an_sv - (r.an_ruecklage || 0) - (r.tilgung || 0) }))
          .filter((r) => r.netto > 0.0005).sort((a, b) => b.netto - a.netto);
        fonds.forEach((f) => groesse.set(f.kapitel, Math.max(groesse.get(f.kapitel) || 0, f.netto)));
        const j = jahre.find((x) => x.jahr === s.jahr) || {};
        const eu = d3.sum(rows.filter((r) => r.art === 'eu_eigenmittel'), (r) => r.ausgaben);
        spalten.push({ ...s, key: s.jahr + '-' + s.wert, fonds, summe: d3.sum(fonds, (f) => f.netto),
          kredite: d3.sum(fonds, (f) => f.kredite), vom_kern: d3.sum(fonds, (f) => f.vom_kern), eu,
          kern: s.wert === 'ist' ? j.ausgaben_ist : j.ausgaben_soll });
      });
      const reihenfolge = [...groesse.entries()].sort((a, b) => b[1] - a[1]).map(([k]) => k);
      const namen = new Map(sv.map((r) => [r.kapitel, r.name]));
      return { spalten, fonds: reihenfolge.map((k, i) => ({ kapitel: k, name: kurz(namen.get(k)), idx: i })) };
    }
  });

  dash.calc('gesamt_vergleich', {
    inputs: ['bund_gesamt', 'jahre'], title: 'Kernhaushalt und Bund insgesamt',
    description: 'Je Jahr: Ausgaben Kernhaushalt (Ist) und Bund insgesamt (Eurostat S1311), Nettokreditaufnahme Kernhaushalt und Finanzierungsdefizit Bund insgesamt.',
    fn: (bg, jahre) => {
      const total = new Map(bg.filter((r) => r.reihe === 'ausgaben' && r.bereich === 'TOTAL').map((r) => [r.jahr, r.mrd]));
      const saldo = new Map(bg.filter((r) => r.reihe === 'saldo').map((r) => [r.jahr, r.mrd]));
      return jahre.filter((j) => j.ausgaben_ist != null).map((j) => ({
        jahr: j.jahr, kern: j.ausgaben_ist, gesamt: total.get(j.jahr) ?? null,
        nka: j.kredite_ist, defizit: saldo.has(j.jahr) ? -saldo.get(j.jahr) : null
      }));
    }
  });

  dash.calc('cofog', {
    inputs: ['bund_gesamt'], title: 'Bund insgesamt nach Aufgabenbereichen',
    description: 'Je COFOG-Bereich: Verlauf, letzter Wert und Veränderung seit 2015 (Eurostat S1311).',
    fn: (bg) => {
      const rows = bg.filter((r) => r.reihe === 'ausgaben' && r.bereich !== 'TOTAL');
      const by = d3.group(rows, (r) => r.bereich);
      return [...by.entries()].map(([b, rs]) => {
        rs = rs.slice().sort((x, y) => x.jahr - y.jahr);
        const first = rs[0], last = rs[rs.length - 1];
        return { bereich: b, name: last.name, reihe: rs.map((r) => ({ jahr: r.jahr, mrd: r.mrd })), jahr: last.jahr, wert: last.mrd,
          start: first.mrd, startJahr: first.jahr, pct: first.mrd ? last.mrd / first.mrd - 1 : null };
      }).sort((a, b) => b.wert - a.wert);
    }
  });

  const spalte = (d, jahr, wert) => d.spalten.find((s) => s.jahr === jahr && s.wert === wert);
  const fondsWert = (s, kap) => { const f = s && s.fonds.find((x) => x.kapitel === kap); return f ? f.netto : null; };

  // Umfang-Kasten
  dash.draw('svsumme', (el) => {
    const d = dash.data('sv_jahre');
    if (d.status !== 'ok') { el.textContent = '—'; return; }
    const s = d.data.spalten[d.data.spalten.length - 1];
    el.textContent = s ? mrd(s.summe) + ' (' + s.label.replace(' geplant', '') + ')' : '—';
  });
  dash.draw('eusumme', (el) => {
    const d = dash.data('sv_jahre');
    if (d.status !== 'ok') { el.textContent = '—'; return; }
    const s = spalte(d.data, 2025, 'ist') || d.data.spalten[d.data.spalten.length - 1];
    el.textContent = s ? s.label.replace(' tatsächlich', '') + ': ' + mrd(s.eu) : '—';
  });

  // Lesehilfe je Thema (kurze Fassung erscheint auch in den Detailzeilen)
  const SV_KAP = { verteidigung: '1491', klima: '6092', verkehr: '6093' };
  const KURZ = {
    familie: 'Kindergeld, Kinderfreibetrag und Ehegattensplitting laufen über die Steuer und fehlen hier; Kitas zahlen vor allem Länder und Gemeinden.',
    rente: 'Zuschüsse und Beiträge des Bundes an die Rentenversicherung (u. a. für Kindererziehungszeiten), Erstattung der Grundsicherung im Alter, Knappschaft und Alterssicherung der Landwirte; nicht die Renten insgesamt (die zahlt die Rentenversicherung).',
    verwaltung: 'Enthält die Pensionen früherer Bundesbeamter, darunter den Zuschuss an die Postbeamtenversorgungskasse.',
    gesundheit: 'Nur Ausgaben des Bundes; Kranken- und Pflegeversicherung sind eigene Haushalte.',
    grundsicherung: 'Enthält auch Leistungen für Kinder in Haushalten mit Bürgergeld.',
    finanz: 'Enthält Buchungsposten wie Zuweisungen an Sondervermögen, Rücklagen und globale Mehr- oder Minderausgaben.'
  };
  const svSatz = (thema) => {
    const d = dash.data('sv_jahre');
    if (d.status !== 'ok' || !SV_KAP[thema]) return null;
    const s = spalte(d.data, 2025, 'ist'), p = spalte(d.data, 2026, 'soll');
    const f = d.data.fonds.find((x) => x.kapitel === SV_KAP[thema]);
    if (!f) return null;
    const a = fondsWert(s, f.kapitel), b = fondsWert(p, f.kapitel);
    const teile = [];
    if (a != null) teile.push('2025 tatsächlich ' + mrd(a));
    if (b != null) teile.push('2026 geplant ' + mrd(b));
    const extra = thema === 'verkehr' ? ' (finanziert neben Verkehr u. a. Zuweisungen an den Klima- und Transformationsfonds, Krankenhäuser und Investitionen von Ländern und Gemeinden)' : '';
    return 'Ohne das Sondervermögen „' + f.name + '“' + extra + (teile.length ? ': ' + teile.join(', ') : '') + ', siehe Abschnitt 4.';
  };
  window.themenHinweis = (thema) => svSatz(thema) || KURZ[thema] || null;
  window.addHinweis = (el, thema) => {
    const t = window.themenHinweis(thema);
    if (t) el.append(mk('span', 'hinweis', ' · Hinweis: ' + t));
  };

  const LESE = [
    ['verteidigung', 'Verteidigung'], ['klima', 'Energie, Klima & Umwelt'], ['verkehr', 'Verkehr & digitale Netze'],
    ['familie', 'Familie & Kinder'], ['rente', 'Rente & Alterssicherung'], ['gesundheit', 'Gesundheit & Pflege'],
    ['grundsicherung', 'Bürgergeld, Grundsicherung & Arbeitsmarkt'], ['verwaltung', 'Politische Führung & Verwaltung'],
    ['finanz', 'Finanzwirtschaft']
  ];
  dash.draw('lesehilfe', (el) => {
    el.replaceChildren();
    LESE.forEach(([th, name]) => {
      const t = window.themenHinweis(th);
      if (!t) return;
      const li = mk('li'); li.append(mk('b', '', name + ': '), document.createTextNode(t)); el.append(li);
    });
  });

  // Sondervermögen je Jahr
  const fondsFarbe = (i) => colorOf(i + 3);
  let svPick = null;
  dash.draw('svlegende', (el) => {
    const d = dash.data('sv_jahre');
    el.replaceChildren();
    if (d.status !== 'ok') return;
    d.data.fonds.forEach((f) => { const s = mk('span', 'lgx'); const i = mk('i'); i.style.background = fondsFarbe(f.idx); s.append(i, document.createTextNode(f.name)); el.append(s); });
    const s = mk('span', 'lgx'); const i = mk('i'); i.style.background = 'var(--cds-chart-muted)'; s.append(i, document.createTextNode('Kernhaushalt zum Vergleich')); el.append(s);
  });
  dash.draw('svchart', (el) => {
    const d = dash.data('sv_jahre');
    el.replaceChildren();
    if (d.status !== 'ok') return;
    const max = d3.max(d.data.spalten, (s) => Math.max(s.summe, s.kern || 0)) || 1;
    d.data.spalten.forEach((s) => {
      const row = mk('div', 'sb-row sv-row');
      row.append(mk('div', 'sb-y', s.label));
      const wrap = mk('div', 'sb-wrap');
      wrap.append(mk('div', 'sb-top', 'Sondervermögen ' + mrd(s.summe) + (s.kredite ? ' · davon Kredite ' + mrd(s.kredite) : '')));
      const bar = mk('div', 'sb-bar'); bar.style.width = (100 * s.summe / max) + '%';
      s.fonds.forEach((f) => {
        const fi = d.data.fonds.find((x) => x.kapitel === f.kapitel);
        const seg = mk('div', 'sb-seg'); seg.style.width = (100 * f.netto / s.summe) + '%'; seg.style.background = fondsFarbe(fi.idx);
        seg.title = f.name + ': ' + mrd(f.netto);
        seg.addEventListener('click', () => { svPick = { key: s.key, kapitel: f.kapitel }; dash.draw('svdetail'); });
        bar.append(seg);
      });
      const kern = mk('div', 'sb-bar sv-kern'); kern.style.width = (100 * (s.kern || 0) / max) + '%';
      const kseg = mk('div', 'sb-seg'); kseg.style.width = '100%'; kseg.style.background = 'var(--cds-chart-muted)'; kern.append(kseg);
      wrap.append(bar, kern, mk('div', 'sv-kern-label', 'Kernhaushalt ' + mrd(s.kern)));
      row.append(wrap); el.append(row);
    });
  });
  dash.draw('svdetail', (el) => {
    const d = dash.data('sv_jahre');
    el.replaceChildren();
    if (d.status !== 'ok' || !svPick) { el.textContent = '—'; return; }
    const s = d.data.spalten.find((x) => x.key === svPick.key);
    const f = s && s.fonds.find((x) => x.kapitel === svPick.kapitel);
    if (!f) { el.textContent = '—'; return; }
    const teile = [['über Kredite', f.kredite], ['aus Rücklage', f.ruecklage], ['eigene Einnahmen', f.eigene], ['aus dem Kernhaushalt', f.vom_kern], ['von anderen Sondervermögen', f.von_sv]]
      .filter(([, v]) => Math.abs(v) >= 0.0005).map(([n, v]) => n + ' ' + mrd(v));
    el.append(mk('b', '', kurz(f.name) + ', ' + s.label + ': ' + mrd(f.netto)));
    const ohne = [[f.an_sv, 'an andere Sondervermögen'], [f.an_ruecklage, 'Zuführung an Rücklage'], [f.tilgung, 'Tilgung']]
      .filter(([v]) => v && Math.abs(v) >= 0.0005).map(([v, n]) => mrd(v) + ' ' + n);
    if (ohne.length) el.append(document.createTextNode(' (ohne ' + ohne.join(', ') + ')'));
    if (teile.length) el.append(document.createTextNode(' · finanziert ' + teile.join(', ')));
    el.append(document.createTextNode(' · ' + pf.format(f.netto / s.kern) + ' des Kernhaushalts'));
  });

  // Kernhaushalt und Bund insgesamt
  let gPick = null;
  const paar = (el, rows, keyA, keyB, onPick, sel, diverging) => {
    const max = d3.max(rows, (r) => Math.max(Math.abs(r[keyA] || 0), Math.abs(r[keyB] || 0))) || 1;
    rows.forEach((r) => {
      const block = mk('div', 'vj-block clickable' + (sel === r.jahr ? ' sel-row' : ''));
      block.addEventListener('click', () => onPick(r.jahr));
      block.append(mk('div', 'vj-year', String(r.jahr)));
      [[keyA, 'Kernhaushalt', dash.colors[0]], [keyB, 'Bund insgesamt', dash.colors[4]]].forEach(([k, name, c]) => {
        const v = r[k];
        const line = mk('div', 'vj-line');
        line.append(mk('span', 'vj-n', name));
        const tr = mk('div', 'hb-track vj-track');
        if (v != null) {
          const bar = mk('div', 'hb-bar'); bar.style.background = c;
          if (diverging) { const w = 50 * Math.abs(v) / max; bar.style.width = w + '%'; bar.style.left = v < 0 ? (50 - w) + '%' : '50%'; tr.append(bar, mk('div', 'hb-mid')); }
          else { bar.style.left = '0'; bar.style.width = (100 * v / max) + '%'; tr.append(bar); }
        }
        line.append(tr, mk('span', 'vj-v', v == null ? 'n. v.' : nf1.format(v)));
        block.append(line);
      });
      el.append(block);
    });
  };
  dash.draw('gesamtchart', (el) => {
    const d = dash.data('gesamt_vergleich');
    el.replaceChildren();
    if (d.status !== 'ok') return;
    paar(el, d.data.filter((r) => r.gesamt != null), 'kern', 'gesamt', (j) => { gPick = gPick === j ? null : j; dash.draw('gesamtchart'); dash.draw('gesamtdetail'); }, gPick, false);
  });
  dash.draw('gesamtdetail', (el) => {
    const d = dash.data('gesamt_vergleich');
    el.replaceChildren();
    if (d.status !== 'ok') { el.textContent = '—'; return; }
    const rows = d.data.filter((r) => r.gesamt != null);
    const r = rows.find((x) => x.jahr === gPick) || rows[rows.length - 1];
    if (!r) { el.textContent = '—'; return; }
    el.append(mk('b', '', r.jahr + ': '), document.createTextNode('Kernhaushalt ' + mrd(r.kern) + ' · Bund insgesamt ' + mrd(r.gesamt) + ' · Unterschied ' + mrd(r.gesamt - r.kern) + ' (' + pf.format(r.gesamt / r.kern - 1) + ')'));
  });

  // Aufgabenbereiche
  let cPick = null;
  dash.draw('cofogchart', (el) => {
    const d = dash.data('cofog');
    el.replaceChildren();
    if (d.status !== 'ok') return;
    const max = d3.max(d.data, (r) => r.wert) || 1;
    d.data.forEach((r) => {
      const row = mk('div', 'hb-row clickable' + (cPick === r.bereich ? ' sel-row' : ''));
      row.addEventListener('click', () => { cPick = cPick === r.bereich ? null : r.bereich; dash.draw('cofogchart'); dash.draw('cofogdetail'); });
      const top = mk('div', 'hb-top');
      const v = mk('span', 'v', mrd(r.wert) + ' ');
      if (r.pct != null) v.append(colored(spct(r.pct) + ' seit ' + r.startJahr, r.pct));
      top.append(mk('span', 'n', r.name), v);
      const tr = mk('div', 'hb-track'); const bar = mk('div', 'hb-bar');
      bar.style.left = '0'; bar.style.width = (100 * r.wert / max) + '%'; bar.style.background = dash.colors[4];
      tr.append(bar); row.append(top, tr); el.append(row);
    });
  });
  dash.draw('cofogdetail', (el) => {
    const d = dash.data('cofog');
    el.replaceChildren();
    if (d.status !== 'ok') { el.textContent = '—'; return; }
    const r = d.data.find((x) => x.bereich === cPick);
    if (!r) { el.textContent = d.data.length ? 'Stand: ' + d.data[0].jahr + '. Tippe auf einen Bereich.' : '—'; return; }
    el.append(mk('b', '', r.name + ': '), document.createTextNode(r.reihe.map((x) => x.jahr + ' ' + nf1.format(x.mrd)).join(' · ') + ' Mrd. €'));
  });

  // Neue Schulden
  let sPick = null;
  dash.draw('schuldenchart', (el) => {
    const d = dash.data('gesamt_vergleich');
    el.replaceChildren();
    if (d.status !== 'ok') return;
    paar(el, d.data, 'nka', 'defizit', (j) => { sPick = sPick === j ? null : j; dash.draw('schuldenchart'); dash.draw('schuldendetail'); }, sPick, true);
  });
  dash.draw('schuldendetail', (el) => {
    const d = dash.data('gesamt_vergleich');
    el.replaceChildren();
    if (d.status !== 'ok') { el.textContent = '—'; return; }
    const r = d.data.find((x) => x.jahr === sPick);
    if (!r) { el.textContent = '—'; return; }
    el.append(mk('b', '', r.jahr + ': '), document.createTextNode('Nettokreditaufnahme Kernhaushalt ' + mrd(r.nka) + ' · ' +
      (r.defizit == null ? 'Bund insgesamt: noch keine Angabe' : (r.defizit >= 0 ? 'Finanzierungsdefizit Bund insgesamt ' + mrd(r.defizit) : 'Überschuss Bund insgesamt ' + mrd(-r.defizit)))));
  });
})();
