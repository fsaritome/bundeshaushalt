// Kleine Laufzeit für die Seite: lädt die Daten aus /data, rechnet die Berechnungen und zeichnet die Grafiken.
(function () {
  const DATASETS = ['themen', 'jahre', 'median', 'preise', 'preise_kategorien', 'konsum', 'belege'];
  const store = {};
  const calcs = {};
  const draws = {};
  const onDataFns = [];
  let params = { wert: 'ist', art: 'mrd', skala: 'eigen', fokus: '' };

  const css = getComputedStyle(document.documentElement);
  const colors = [1, 2, 3, 4, 5, 6, 7, 8].map((i) => css.getPropertyValue('--series-' + i).trim() || d3.schemeTableau10[i - 1]);

  function computeCalc(id) {
    const c = calcs[id];
    if (!c) return { status: 'missing', data: [] };
    const inputs = c.inputs.map((i) => dash.data(i));
    if (inputs.some((r) => r.status !== 'ok')) return { status: 'loading', data: [] };
    try {
      return { status: 'ok', data: c.fn(...inputs.map((r) => r.data)) };
    } catch (e) {
      console.error('Berechnung fehlgeschlagen:', id, e);
      return { status: 'error', data: [], message: String(e) };
    }
  }

  function runDraw(name) {
    const fn = draws[name];
    if (!fn) return;
    document.querySelectorAll('[data-draw="' + name + '"]').forEach((el) => {
      if (el.closest('[hidden]')) return;
      try { fn(el); } catch (e) { console.error('Zeichnen fehlgeschlagen:', name, e); }
    });
  }

  function redrawAll() {
    onDataFns.forEach((fn) => { try { fn(); } catch (e) { console.error(e); } });
    Object.keys(draws).forEach(runDraw);
  }

  window.dash = {
    colors,
    data(id) {
      if (store[id]) return store[id];
      if (calcs[id]) return computeCalc(id);
      return { status: 'loading', data: [] };
    },
    calc(id, def) { calcs[id] = def; },
    loader() {},
    draw(name, fn) {
      if (typeof fn === 'function') { draws[name] = fn; return; }
      runDraw(name);
    },
    onData(fn) { onDataFns.push(fn); },
    params() { return Object.assign({}, params); },
    setParams(p) { params = Object.assign({}, params, p); redrawAll(); },
    resetParams() { params = { wert: 'ist', art: 'mrd', skala: 'eigen', fokus: '' }; redrawAll(); },
    setLink(name) { history.replaceState(null, '', '#' + name); },
    refresh() {}
  };

  window.addEventListener('DOMContentLoaded', () => {
    Promise.all(DATASETS.map((id) => fetch('data/' + id + '.json').then((r) => {
      if (!r.ok) throw new Error(id + ': ' + r.status);
      return r.json();
    }).then((data) => { store[id] = { status: 'ok', data }; }).catch((e) => {
      console.error(e);
      store[id] = { status: 'error', data: [], message: String(e) };
    }))).then(redrawAll);
    let w = window.innerWidth;
    window.addEventListener('resize', () => { if (Math.abs(window.innerWidth - w) > 20) { w = window.innerWidth; redrawAll(); } });
  });
})();
