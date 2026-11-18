/* Les trois outils : lisent le formulaire, interrogent l'API Python (Flask), affichent le résultat. */
(() => {
  'use strict';

  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));

  /* ------------------------------------------------------------ formats français */
  const fmt = (opts) => new Intl.NumberFormat('fr-FR', opts);
  const nfEur0 = fmt({ style: 'currency', currency: 'EUR', maximumFractionDigits: 0 });
  const nfEur2 = fmt({ style: 'currency', currency: 'EUR', minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const nfInt = fmt({ maximumFractionDigits: 0 });
  const nf1 = fmt({ minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const nf2 = fmt({ minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const nfFree = fmt({ maximumFractionDigits: 2 });
  const nfK = fmt({ maximumFractionDigits: 1 });
  const FORMATS = {
    eur0: (v) => nfEur0.format(v),
    eur2: (v) => nfEur2.format(v),
    int: (v) => nfInt.format(v),
    pct1: (v) => nf1.format(v) + ' %',
    num2: (v) => nf2.format(v),
  };
  const eur = (v) => nfEur0.format(v);
  const eurK = (v) => (Math.abs(v) >= 1000 ? nfFree.format(v / 1000) + ' k€' : nfInt.format(v) + ' €');

  /* ------------------------------------------------------------ affichage des chiffres */
  function show(el, value) {
    const f = FORMATS[el.dataset.fmt] || String;
    const from = el._v === undefined ? value : el._v;
    el._v = value;
    cancelAnimationFrame(el._raf);
    if (reduce || from === value) {
      el.textContent = f(value);
      return;
    }
    const t0 = performance.now();
    const step = (now) => {
      const k = Math.min(1, (now - t0) / 450);
      el.textContent = f(from + (value - from) * (1 - Math.pow(1 - k, 3)));
      if (k < 1) el._raf = requestAnimationFrame(step);
    };
    el._raf = requestAnimationFrame(step);
  }

  function fill(scope, data) {
    $$('[data-out]', scope).forEach((el) => {
      const v = data[el.dataset.out];
      if (typeof v === 'number' && isFinite(v)) show(el, v);
    });
  }

  /* ------------------------------------------------------------ barre de répartition + légende */
  function drawBar(scope, name, parts) {
    const bar = $(`[data-bar="${name}"]`, scope);
    const legend = $(`[data-legend="${name}"]`, scope);
    while (bar.children.length < parts.length) bar.appendChild(document.createElement('i'));
    Array.from(bar.children).forEach((seg, i) => {
      const p = parts[i];
      seg.hidden = !p;
      if (!p) return;
      seg.style.flexGrow = String(Math.max(p.value, 0));
      seg.style.background = p.color;
      seg.title = `${p.label}\u00a0: ${eur(p.value)}`;
    });
    legend.textContent = '';
    parts.forEach((p) => {
      const li = document.createElement('li');
      li.className = 'lg';
      li.style.setProperty('--sw', p.color);
      li.textContent = `${p.label}\u00a0: ${eur(p.value)}`;
      legend.appendChild(li);
    });
  }

  /* ------------------------------------------------------------ petits outils SVG */
  const NS = 'http://www.w3.org/2000/svg';
  function el(tag, attrs, text) {
    const n = document.createElementNS(NS, tag);
    Object.entries(attrs || {}).forEach(([k, v]) => n.setAttribute(k, v));
    if (text !== undefined) n.textContent = text;
    return n;
  }
  const poly = (pts) => 'M' + pts.map((p) => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join('L');

  /* Capital remboursé et intérêts payés, cumulés mois après mois. */
  function drawAmort(svg, serie) {
    const W = 600, H = 250, L = 58, R = 12, T = 14, B = 30;
    const n = serie.capital.length;
    const total = serie.capital[n - 1] + serie.interets[n - 1];
    svg.textContent = '';
    if (!n || total <= 0) return;
    const x = (i) => L + ((W - L - R) * i) / n;
    const y = (v) => T + (H - T - B) * (1 - v / total);

    [0, 0.5, 1].forEach((k) => {
      const yy = y(total * k);
      svg.appendChild(el('line', { class: k === 0 ? 'c-axis' : 'c-grid', x1: L, x2: W - R, y1: yy, y2: yy }));
      svg.appendChild(el('text', { class: 'c-txt', x: L - 8, y: yy + 4, 'text-anchor': 'end' }, eurK(total * k)));
    });

    const cap = [[x(0), y(0)]].concat(serie.capital.map((v, i) => [x(i + 1), y(v)]));
    const top = [[x(0), y(0)]].concat(serie.capital.map((v, i) => [x(i + 1), y(v + serie.interets[i])]));
    svg.appendChild(el('path', { class: 'c-b', d: poly(top) + 'L' + cap.slice().reverse().map((p) => `${p[0].toFixed(1)},${p[1].toFixed(1)}`).join('L') + 'Z' }));
    svg.appendChild(el('path', { class: 'c-a', d: poly(cap) + `L${x(n).toFixed(1)},${y(0).toFixed(1)}L${x(0).toFixed(1)},${y(0).toFixed(1)}Z` }));

    [[0, 'start'], [n / 2, 'middle'], [n, 'end']].forEach(([i, anchor]) => {
      svg.appendChild(el('text', { class: 'c-txt', x: x(i), y: H - 8, 'text-anchor': anchor }, i === 0 ? '0' : `${nfInt.format(i)} mois`));
    });
  }

  /* Résultat mensuel selon le nombre de voitures vendues. */
  function drawSeuil(svg, courbe, qExact, qCeil) {
    const W = 600, H = 250, L = 58, R = 14, T = 20, B = 30;
    const xs = courbe.quantites;
    const ys = courbe.resultats;
    const xMax = xs[xs.length - 1];
    const yMin = Math.min(0, ...ys);
    const yMax = Math.max(0, ...ys);
    const span = yMax - yMin || 1;
    const x = (q) => L + ((W - L - R) * q) / xMax;
    const y = (v) => T + (H - T - B) * (1 - (v - yMin) / span);
    const zero = y(0);
    svg.textContent = '';

    const defs = el('defs');
    const above = el('clipPath', { id: 'seuil-above' });
    above.appendChild(el('rect', { x: 0, y: 0, width: W, height: zero }));
    const below = el('clipPath', { id: 'seuil-below' });
    below.appendChild(el('rect', { x: 0, y: zero, width: W, height: H - zero }));
    defs.appendChild(above);
    defs.appendChild(below);
    svg.appendChild(defs);

    const pts = xs.map((q, i) => [x(q), y(ys[i])]);
    const zone = poly(pts) + `L${x(xMax).toFixed(1)},${zero.toFixed(1)}L${x(0).toFixed(1)},${zero.toFixed(1)}Z`;
    svg.appendChild(el('path', { class: 'c-b', d: zone, 'clip-path': 'url(#seuil-below)' }));
    svg.appendChild(el('path', { class: 'c-a', d: zone, 'clip-path': 'url(#seuil-above)', 'fill-opacity': '0.85' }));
    svg.appendChild(el('line', { class: 'c-axis', x1: L, x2: W - R, y1: zero, y2: zero }));
    svg.appendChild(el('path', { class: 'c-line', d: poly(pts) }));

    const mx = x(Math.min(qExact, xMax));
    svg.appendChild(el('line', { class: 'c-mark', x1: mx, x2: mx, y1: T - 6, y2: H - B }));
    const right = mx > W * 0.65;
    svg.appendChild(
      el('text', { class: 'c-txt', x: right ? mx - 8 : mx + 8, y: T + 6, 'text-anchor': right ? 'end' : 'start', style: 'fill:#f5f7f5;font-weight:600' }, `Seuil\u00a0: ${nfInt.format(qCeil)} voitures`)
    );

    const reperes = new Set([0]);
    if (yMin < 0) reperes.add(yMin);
    if (yMax > 0) reperes.add(yMax);
    reperes.forEach((v) => {
      svg.appendChild(el('text', { class: 'c-txt', x: L - 8, y: y(v) + 4, 'text-anchor': 'end' }, eurK(v)));
    });
    [[0, 'start'], [xMax, 'end']].forEach(([q, a]) => {
      svg.appendChild(el('text', { class: 'c-txt', x: x(q), y: H - 8, 'text-anchor': a }, q === 0 ? '0' : `${nfInt.format(q)} voitures`));
    });
  }

  /* ------------------------------------------------------------ lecture et validation du formulaire */
  function readFields(form) {
    const out = {};
    let ok = true;
    $$('.field:not([hidden])', form).forEach((f) => {
      const input = $('input[type="number"], select', f);
      if (!input) return;
      let bad = '';
      if (input.tagName === 'SELECT') {
        out[input.name] = input.value;
      } else {
        const raw = input.value.trim();
        const n = Number(raw);
        if (raw === '' || !isFinite(n)) bad = 'Saisis un nombre.';
        else if (n < Number(input.min) || n > Number(input.max)) bad = `Entre ${nfInt.format(Number(input.min))} et ${nfInt.format(Number(input.max))}.`;
        else out[input.name] = n;
      }
      const msg = $('.field__err', f);
      if (msg) {
        msg.textContent = bad;
        msg.hidden = !bad;
      }
      if (bad) {
        f.setAttribute('data-bad', '');
        ok = false;
      } else {
        f.removeAttribute('data-bad');
      }
    });
    return ok ? out : null;
  }

  async function api(path, params, signal) {
    const res = await fetch(path + '?' + new URLSearchParams(params), { signal, headers: { Accept: 'application/json' } });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.erreur || 'Calcul impossible avec ces valeurs.');
    return data;
  }

  /* Relie un formulaire à sa fonction de calcul : curseurs, saisie, annulation des appels périmés. */
  function tool(name, run) {
    const form = $(`form[data-tool="${name}"]`);
    const cluster = $(`[data-cluster="${name}"]`);
    if (!form || !cluster) return null;
    const err = $('[data-error]', cluster);
    const summary = $('[data-summary]', cluster);
    let timer;
    let controller;
    let seq = 0;

    async function go() {
      const values = readFields(form);
      if (!values) return;
      if (controller) controller.abort();
      controller = new AbortController();
      const mine = ++seq;
      try {
        const res = await run(values, controller.signal, cluster);
        if (mine !== seq) return;
        err.hidden = !(res && res.error);
        err.textContent = res && res.error ? res.error : '';
        cluster.classList.toggle('is-stale', Boolean(res && res.error));
        summary.textContent = res && res.summary ? res.summary : '';
      } catch (e) {
        if (e.name === 'AbortError' || mine !== seq) return;
        err.textContent = e instanceof TypeError ? 'Le calcul est momentanément indisponible. Réessaie dans un instant.' : e.message;
        err.hidden = false;
        summary.textContent = '';
        cluster.classList.add('is-stale');
      }
    }
    const trigger = () => {
      clearTimeout(timer);
      timer = setTimeout(go, 140);
    };

    $$('.range', form).forEach((range) => {
      const num = $('#' + range.dataset.for, form);
      range.addEventListener('input', () => {
        num.value = range.value;
        trigger();
      });
      num.addEventListener('input', () => {
        if (num.value !== '' && isFinite(Number(num.value))) range.value = num.value;
        trigger();
      });
    });
    $$('select', form).forEach((s) => s.addEventListener('change', trigger));
    return { form, cluster, trigger, go };
  }

  /* ------------------------------------------------------------ 1. financement */
  const fin = tool('financement', async (v, signal, cluster) => {
    const mode = $('input[name="mode"]:checked', fin.form).value;
    if (mode === 'prix') {
      const d = await api('/api/financement', { prix: v.prix, apport: v.apport, duree: v.duree, taux: v.taux }, signal);
      fill(cluster, d);
      const chart = $('.chart', cluster);
      const nothing = d.emprunt === 0;
      chart.toggleAttribute('hidden', nothing);
      $('[data-panel="prix"] .legend', cluster).hidden = nothing;
      if (nothing) return { summary: "L'apport couvre le prix du véhicule : aucun crédit n'est nécessaire." };
      drawAmort(chart, d.serie);
      return {
        summary: `Pour ${eur(d.emprunt)} empruntés sur ${v.duree} mois à ${nfFree.format(v.taux)}\u00a0%, la mensualité est de ${nfEur2.format(d.mensualite)}. Le crédit coûte ${eur(d.cout_credit)} d'intérêts.`,
      };
    }
    const d = await api('/api/budget', { revenu: v.revenu, charges: v.charges, endettement: v.endettement, apport: v.apport, duree: v.duree, taux: v.taux }, signal);
    fill(cluster, Object.assign({ apport: v.apport }, d));
    const encours = Math.min(v.charges, v.revenu);
    const reste = Math.max(v.revenu - encours - d.mensualite_max, 0);
    drawBar(cluster, 'revenu', [
      { label: 'Crédits en cours', value: encours, color: 'rgba(245,247,245,.34)' },
      { label: 'Nouvelle mensualité', value: d.mensualite_max, color: 'var(--ambre)' },
      { label: 'Reste du revenu', value: reste, color: 'rgba(245,247,245,.12)' },
    ]);
    if (d.mensualite_max === 0) return { summary: "Les crédits en cours absorbent déjà toute la capacité d'endettement\u00a0: pas de nouvelle mensualité possible." };
    return {
      summary: `Avec ${eur(v.revenu)} de revenu et ${nfInt.format(v.endettement)}\u00a0% d'endettement maximal, la mensualité peut aller jusqu'à ${eur(d.mensualite_max)}. Cela finance un véhicule de ${eur(d.budget_max)}, apport compris.`,
    };
  });

  if (fin) {
    const applyMode = () => {
      const m = $('input[name="mode"]:checked', fin.form).value;
      $$('.field[data-modes]', fin.form).forEach((f) => (f.hidden = !f.dataset.modes.split(' ').includes(m)));
      $$('[data-panel]', fin.cluster).forEach((p) => (p.hidden = p.dataset.panel !== m));
    };
    $$('input[name="mode"]', fin.form).forEach((r) =>
      r.addEventListener('change', () => {
        applyMode();
        fin.go();
      })
    );
    applyMode();
    fin.go();
  }

  /* ------------------------------------------------------------ 2. marge */
  const MODES = {
    pv: { label: 'Prix de vente HT', unit: '€', min: 1, max: 10000000, step: 100, def: 16800, rmin: 5000, rmax: 60000 },
    marge: { label: 'Taux de marge', unit: '%', min: 0.01, max: 1000, step: 0.5, def: 12, rmin: 1, rmax: 60 },
    marque: { label: 'Taux de marque', unit: '%', min: 0.01, max: 99, step: 0.5, def: 11, rmin: 1, rmax: 60 },
  };

  const marge = tool('marge', async (v, signal, cluster) => {
    const mode = $('input[name="mode"]:checked', marge.form).value;
    const d = await api('/api/marge', { mode, pa: v.pa, valeur: v.valeur, tva: v.tva }, signal);
    fill(cluster, d);
    drawBar(cluster, 'prix', [
      { label: "Prix d'achat HT", value: d.pa, color: 'rgba(245,247,245,.34)' },
      { label: 'Marge', value: Math.max(d.marge, 0), color: 'var(--ambre)' },
      { label: 'TVA', value: d.tva_montant, color: 'rgba(245,247,245,.12)' },
    ]);
    if (d.marge < 0) return { summary: "Attention\u00a0: ce prix de vente est inférieur au prix d'achat, la vente se ferait à perte." };
    return {
      summary: `Une voiture achetée ${eur(d.pa)} HT et vendue ${eur(d.pv_ht)} HT (${eur(d.pv_ttc)} TTC) laisse ${eur(d.marge)} de marge\u00a0: ${FORMATS.pct1(d.taux_marge)} de taux de marge et ${FORMATS.pct1(d.taux_marque)} de taux de marque.`,
    };
  });

  if (marge) {
    const main = $('.field[data-main]', marge.form);
    const label = $('label', main);
    const unit = $('.unit', main);
    const num = $('input[type="number"]', main);
    const range = $('.range', main);
    $$('input[name="mode"]', marge.form).forEach((r) =>
      r.addEventListener('change', () => {
        const m = MODES[r.value];
        label.textContent = m.label;
        unit.textContent = m.unit;
        Object.assign(num, { min: m.min, max: m.max, step: m.step, value: m.def });
        Object.assign(range, { min: m.rmin, max: m.rmax, step: m.step, value: m.def });
        marge.go();
      })
    );
    marge.go();
  }

  /* ------------------------------------------------------------ 3. rentabilité */
  const renta = tool('rentabilite', async (v, signal, cluster) => {
    const d = await api('/api/rentabilite', { cf: v.cf, pvu: v.pvu, cvu: v.cvu }, signal);
    const chart = $('.chart', cluster);
    const legend = $('.legend', cluster);
    chart.toggleAttribute('hidden', !d.ok);
    legend.hidden = !d.ok;
    if (!d.ok) return { error: d.message };
    fill(cluster, d);
    $('.readout__unit', cluster).textContent = d.quantite > 1 ? 'voitures par mois' : 'voiture par mois';
    drawSeuil(chart, d.courbe, v.cf / d.mcv_unitaire, d.quantite);
    if (d.quantite === 0) return { summary: 'Sans charges fixes, la première vente est déjà rentable.' };
    return {
      summary: `Chaque voiture vendue laisse ${eur(d.mcv_unitaire)} après ses coûts variables. Il en faut ${nfInt.format(d.quantite)} par mois pour couvrir ${eur(v.cf)} de charges fixes\u00a0: au-delà, la concession gagne de l'argent.`,
    };
  });
  if (renta) renta.go();
})();
