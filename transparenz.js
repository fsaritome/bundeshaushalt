// Abschnitt „Transparenz“: Gegenproben, Korrekturen, automatische Prüfungen, offene Punkte, Datenstand.
// Alle Inhalte kommen aus data/pruefung.json; Hilfsfunktionen (mk, dash) aus dem Seitenskript.
(function () {
  const datum = (iso) => { const [y, m, d] = iso.split('-'); return Number(d) + '.' + Number(m) + '.' + y; };
  const nf3 = new Intl.NumberFormat('de-DE', { minimumFractionDigits: 3, maximumFractionDigits: 3 });
  const ERG = { gleich: ['übereinstimmend', 'ok'], plausibel: ['plausibel, Unterschiede erklärt', 'mid'], korrigiert: ['nach Korrektur übereinstimmend', 'fix'] };
  const link = (url, text) => { const a = mk('a', '', text); a.href = url; a.target = '_blank'; a.rel = 'noopener'; return a; };
  const P = () => dash.data('pruefung');

  dash.draw('datenstand', (el) => {
    const d = P();
    el.textContent = d.status === 'ok' ? datum(d.data.stand) : '—';
  });

  dash.draw('gegenproben', (el) => {
    const d = P();
    el.replaceChildren();
    if (d.status !== 'ok') return;
    d.data.gegenproben.forEach((g) => {
      const box = mk('div', 'gp');
      const head = mk('div', 'gp-head');
      const [txt, cls] = ERG[g.ergebnis] || [g.ergebnis, 'mid'];
      head.append(mk('b', '', g.bereich), mk('span', 'badge ' + cls, txt));
      const q = mk('div', 'gp-quelle'); q.append(document.createTextNode('Verglichen mit: '), link(g.url, g.quelle));
      const tb = mk('table', 'gp-tab');
      const hr = mk('tr'); ['', 'diese Seite', 'Quelle'].forEach((h) => hr.append(mk('th', '', h)));
      const th = mk('thead'); th.append(hr); tb.append(th);
      const body = mk('tbody');
      g.vergleich.forEach((v) => { const tr = mk('tr'); v.forEach((c) => tr.append(mk('td', '', c))); body.append(tr); });
      tb.append(body);
      const wrap = mk('div', 'tablewrap'); wrap.append(tb);
      box.append(head, q, wrap, mk('p', 'note', g.erklaerung));
      el.append(box);
    });
  });

  dash.draw('themenapi', (el) => {
    const d = P();
    el.replaceChildren();
    if (d.status !== 'ok') return;
    const tb = mk('table');
    const hr = mk('tr'); ['Jahr', 'Summe bundeshaushalt.de', 'Summe diese Seite', 'größte Abweichung je Thema'].forEach((h) => hr.append(mk('th', '', h)));
    const th = mk('thead'); th.append(hr); tb.append(th);
    const body = mk('tbody');
    d.data.themen_api.forEach((r) => {
      const tr = mk('tr');
      tr.append(mk('td', '', r.jahr + (r.wert === 'ist' ? ' Ist' : ' Soll')), mk('td', '', nf3.format(r.api)), mk('td', '', nf3.format(r.seite)), mk('td', r.max > 0.01 ? 'neg' : '', nf3.format(r.max)));
      body.append(tr);
    });
    tb.append(body); el.append(tb);
  });

  dash.draw('korrekturen', (el) => {
    const d = P();
    el.replaceChildren();
    if (d.status !== 'ok') return;
    d.data.korrekturen.forEach((k) => {
      const li = mk('li');
      li.append(mk('b', '', datum(k.datum) + ' · ' + k.was + ': '), document.createTextNode('vorher ' + k.vorher + '; jetzt ' + k.nachher + '. '), mk('span', 'hinweis', 'Gefunden durch: ' + k.anlass + '.'));
      el.append(li);
    });
  });

  const liste = (key) => (el) => {
    const d = P();
    el.replaceChildren();
    if (d.status !== 'ok') return;
    d.data[key].forEach((t) => el.append(mk('li', '', t)));
  };
  dash.draw('automatisch', liste('automatisch'));
  dash.draw('offen', liste('offen'));
})();
