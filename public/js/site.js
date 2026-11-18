/* Défilement du site : cadran de l'accueil, scènes épinglées, apparitions, navigation. */
(() => {
  'use strict';

  const root = document.documentElement;
  const body = document.body;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const stacked = matchMedia('(max-width: 899px), (max-height: 560px)');
  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => Array.from(c.querySelectorAll(s));
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));

  /* ------------------------------------------------------------ cadran de l'accueil */
  const hero = $('#accueil');
  const needle = $('#needle');
  const gradTicks = $$('.g-tick');
  const MAX = 8;
  const IDLE = 1.1;
  const REDLINE = 7.4;
  let rev = 0;
  let revTarget = IDLE;
  let intro = true;
  let chasing = false;

  function setRev(v) {
    rev = v;
    if (needle) needle.style.transform = `rotate(${-135 + (v / MAX) * 270}deg)`;
    gradTicks.forEach((t) => t.classList.toggle('on', v > 0.02 && parseFloat(t.dataset.v) <= v + 0.001));
  }

  function chase() {
    if (intro) return;
    const d = revTarget - rev;
    if (Math.abs(d) < 0.004) {
      setRev(revTarget);
      chasing = false;
      return;
    }
    setRev(rev + d * 0.18);
    requestAnimationFrame(chase);
  }

  function sweep() {
    if (reduce) {
      intro = false;
      setRev(IDLE);
      return;
    }
    const up = 1300;
    const hold = 140;
    const down = 1000;
    const ease = (t) => 1 - Math.pow(1 - t, 3);
    const t0 = performance.now();
    function frame(now) {
      const t = now - t0;
      if (t < up) setRev(REDLINE * ease(t / up));
      else if (t < up + hold) setRev(REDLINE);
      else if (t < up + hold + down) setRev(REDLINE + (IDLE - REDLINE) * ease((t - up - hold) / down));
      else {
        intro = false;
        setRev(IDLE);
        update();
        return;
      }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  /* Le nom s'adapte à la largeur disponible : pratique si ton nom est long. */
  function fitName() {
    const h = $('.name');
    if (!h) return;
    h.style.fontSize = '';
    h.classList.add('name--final');
    /* Sur grand écran, le nom s'arrête avant le compteur (avec une marge de 32 px). */
    let room = h.parentElement.clientWidth;
    const g = $('.gauge');
    if (g && window.innerWidth >= 900) {
      const libre = g.getBoundingClientRect().left - h.getBoundingClientRect().left - 32;
      if (libre > 200) room = Math.min(room, libre);
    }
    const words = $$('.name__w', h);
    const widest = () => Math.max(...words.map((w) => w.getBoundingClientRect().width));
    let size = parseFloat(getComputedStyle(h).fontSize);
    let guard = 0;
    while (widest() > room && size > 28 && guard++ < 60) {
      size *= 0.94;
      h.style.fontSize = size + 'px';
    }
    h.classList.remove('name--final');
  }

  function startHero() {
    fitName();
    void hero.offsetWidth; // fige l'état de départ (nom étroit) pour que la transition parte de là
    hero.classList.add('is-live');
    sweep();
  }

  const fontsReady = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
  Promise.race([fontsReady, new Promise((r) => setTimeout(r, 900))]).then(startHero);

  /* ------------------------------------------------------------ scènes épinglées */
  const pins = $$('[data-pin]').map((el) => {
    const o = { el, kind: el.dataset.pin, cur: 0 };
    if (o.kind === 'passions') {
      o.items = $$('.passion', el);
      o.ticks = $$('.tick', el);
    } else if (o.kind === 'route') {
      o.track = $('.track', el);
    }
    return o;
  });

  function updatePin(o, vh) {
    const rect = o.el.getBoundingClientRect();
    if (rect.bottom < -vh || rect.top > vh * 2) return;
    const total = o.el.offsetHeight - vh;
    const p = total > 0 ? clamp(-rect.top / total) : 0;
    o.el.style.setProperty('--p', p.toFixed(4));

    if (o.kind === 'passions') {
      const n = o.items.length;
      const i = Math.min(n - 1, Math.floor(p * n));
      if (i !== o.cur) {
        o.items[o.cur].classList.remove('is-active');
        o.ticks[o.cur].classList.remove('is-active');
        o.items[i].classList.add('is-active');
        o.ticks[i].classList.add('is-active');
        o.cur = i;
      }
    } else if (o.kind === 'route') {
      const vp = o.track.parentElement;
      const gut = parseFloat(getComputedStyle(vp).paddingLeft) || 0;
      const shift = Math.max(0, o.track.scrollWidth + 2 * gut - vp.clientWidth);
      const q = clamp((p - 0.05) / 0.9);
      o.track.style.transform = `translate3d(${(-q * shift).toFixed(1)}px,0,0)`;
    }
  }

  function resetPins() {
    pins.forEach((o) => {
      o.el.style.removeProperty('--p');
      if (o.track) o.track.style.transform = '';
    });
  }

  /* ------------------------------------------------------------ boucle de défilement */
  let ticking = false;
  function onScroll() {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(update);
    }
  }

  function update() {
    ticking = false;
    const y = window.scrollY;
    const vh = window.innerHeight;
    const doc = root.scrollHeight - vh;
    root.style.setProperty('--prog', doc > 0 ? clamp(y / doc).toFixed(4) : 0);

    const hp = clamp(y / (hero.offsetHeight * 0.9));
    hero.style.setProperty('--hp', hp.toFixed(3));
    if (!intro) {
      revTarget = IDLE + hp * (REDLINE - IDLE);
      if (!chasing) {
        chasing = true;
        requestAnimationFrame(chase);
      }
    }

    if (stacked.matches) return;
    pins.forEach((o) => updatePin(o, vh));
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      fitName();
      update();
    }, 120);
  });
  stacked.addEventListener('change', () => {
    resetPins();
    update();
  });

  /* ------------------------------------------------------------ ton de la scène, navigation, apparitions */
  const sections = $$('main > section[data-tone]');
  const railLinks = $$('.rail a');

  const toneObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        body.dataset.tone = e.target.dataset.tone;
        railLinks.forEach((a) => a.classList.toggle('is-current', a.dataset.s === e.target.id));
      });
    },
    { rootMargin: '-45% 0px -54% 0px' }
  );
  sections.forEach((s) => toneObserver.observe(s));

  const revealObserver = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        e.target.classList.add('is-in');
        obs.unobserve(e.target);
      });
    },
    { rootMargin: '0px 0px -15% 0px' }
  );
  sections.forEach((s) => revealObserver.observe(s));

  /* Les repères de la scène « Ce que j'aime » font défiler jusqu'à la bonne passion. */
  $$('.tick').forEach((btn) => {
    btn.addEventListener('click', () => {
      const el = btn.closest('[data-pin]');
      const n = $$('.passion', el).length;
      const i = Number(btn.dataset.i);
      const top = el.getBoundingClientRect().top + window.scrollY;
      const total = el.offsetHeight - window.innerHeight;
      window.scrollTo({ top: top + (total * (i + 0.5)) / n, behavior: reduce ? 'auto' : 'smooth' });
    });
  });

  update();
})();
