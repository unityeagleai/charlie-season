/* Charlie: Season 1 — Unity's room.
   Cartridges come from episodes.json. Only the chosen episode's video is ever loaded (preload="none"). */
(() => {
  'use strict';
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const stage = $('#stage'), tv = $('#tv'), vid = $('#vid'), shelf = $('#shelf'), list = $('#list');
  const idle = $('#idle'), msg = $('#msg'), slot = $('#slotcart'), roomba = $('#roomba'), bubble = $('#bubble');
  const staticCv = $('#static'), seek = $('#seek'), seekfill = $('#seekfill'), nowtitle = $('#nowtitle');
  const ROOM_W = 400;
  let eps = [], cur = -1, u = 2, staticUntil = 0, staticRAF = 0;

  /* ------------------------------------------------------------ Unity Eagle, player 1: stands on the floor right of the console, under the shelf.
     Sized in whole device pixels per sprite pixel so she stays pixel-crisp; at most 53 room pixels tall (top rows of the file are empty) so she never reaches the shelf. */
  const p1 = $('#p1'), p1tag = $('#p1tag');
  const P1 = { right: 396, foot: 224, maxH: 53,
    full: { src: 'img/unity-eagle.png?v=2', w: 108, h: 144 },        // the 8-bit sprite, 1 file pixel = 1 sprite pixel
    half: { src: 'img/unity-eagle-half.png?v=2', w: 54, h: 72 } };   // same sprite on a 2x coarser grid, for small low-density screens
  function placeP1() {
    if (!p1) return;
    const dpr = window.devicePixelRatio || 1, s = stage.getBoundingClientRect();
    let spr = P1.full, k = Math.floor(P1.maxH * u * dpr / spr.h);
    if (k < 1) { spr = P1.half; k = Math.floor(P1.maxH * u * dpr / spr.h); }
    const img = p1.firstElementChild;
    if (!img.src.endsWith(spr.src)) img.src = spr.src;
    const sp = k >= 1 ? k / dpr : P1.maxH * u / spr.h;          // css px per sprite pixel
    const w = spr.w * sp, h = spr.h * sp;
    // sprite sizes are multiples of 6, so w and h come out in whole css px at 1x, 1.5x, 2x and 3x; snap the corner to a whole css px too
    const snapX = v => Math.round(s.left + v) - s.left;
    const snapY = v => Math.round(s.top + v) - s.top;
    const left = snapX(P1.right * u - w), top = snapY(P1.foot * u - h);
    p1.style.left = left + 'px'; p1.style.top = top + 'px';
    p1.style.width = w + 'px'; p1.style.height = h + 'px';
    p1.style.setProperty('--sp', sp + 'px');
    p1.dataset.k = k;
    p1tag.style.right = (s.width - left + 2 * u) + 'px';
    p1tag.style.top = (top + h * 0.45) + 'px';
  }

  /* ------------------------------------------------------------ scale: 1 room pixel = u css px */
  function resize() {
    u = stage.getBoundingClientRect().width / ROOM_W;
    document.documentElement.style.setProperty('--u', u + 'px');
    document.body.classList.toggle('small', u < 2);
    placeP1();
  }
  new ResizeObserver(resize).observe(stage);
  new ResizeObserver(placeP1).observe($('#app'));   // the stage can move without resizing (episode list appears below it)
  resize();

  /* ------------------------------------------------------------ bleeps (tiny WebAudio square waves, no files) */
  let ac = null;
  function bleep(notes, vol = 0.05, len = 0.07) {
    try {
      ac = ac || new (window.AudioContext || window.webkitAudioContext)();
      if (ac.state === 'suspended') ac.resume();
      let t = ac.currentTime;
      for (const f of notes) {
        const o = ac.createOscillator(), g = ac.createGain();
        o.type = 'square'; o.frequency.value = f;
        g.gain.setValueAtTime(vol, t); g.gain.exponentialRampToValueAtTime(0.0001, t + len);
        o.connect(g).connect(ac.destination); o.start(t); o.stop(t + len + 0.02);
        t += len * 0.9;
      }
    } catch (e) { /* no audio, no problem */ }
  }
  const SFX = {
    insert: () => bleep([392, 523, 784], 0.045, 0.06),
    click: () => bleep([660], 0.035, 0.04),
    eject: () => bleep([523, 330], 0.04, 0.05),
    roomba: () => bleep([523, 659, 784, 659, 1047], 0.04, 0.09),
    p1: () => bleep([784, 988, 1175, 1568], 0.04, 0.07),
  };

  /* ------------------------------------------------------------ TV static */
  const sctx = staticCv.getContext('2d');
  const sImg = sctx.createImageData(staticCv.width, staticCv.height);
  function drawStatic() {
    const d = sImg.data;
    for (let i = 0; i < d.length; i += 4) {
      const v = Math.random() * 255 | 0;
      d[i] = v; d[i + 1] = v; d[i + 2] = v + 18 > 255 ? 255 : v + 18; d[i + 3] = 255;
    }
    sctx.putImageData(sImg, 0, 0);
  }
  let lastS = 0;
  function staticLoop(ts) {
    if (performance.now() > staticUntil) { staticCv.classList.remove('show'); staticRAF = 0; return; }
    if (ts - lastS > 55) { drawStatic(); lastS = ts; }
    staticRAF = requestAnimationFrame(staticLoop);
  }
  function showStatic(ms) {
    staticUntil = Math.max(staticUntil, performance.now() + ms);
    drawStatic(); staticCv.classList.add('show');
    if (!staticRAF) staticRAF = requestAnimationFrame(staticLoop);
  }
  function holdStatic() { showStatic(60000); }
  function endStatic(minLeft = 0) { staticUntil = performance.now() + minLeft; }

  /* ------------------------------------------------------------ cartridges */
  function cartEl(ep, i) {
    const b = document.createElement('button');
    b.className = 'cart';
    b.style.setProperty('--c', ep.color || '#888');
    b.dataset.i = i;
    b.setAttribute('role', 'listitem');
    b.setAttribute('aria-label', `Episode ${ep.number}: ${ep.title}`);
    b.innerHTML = '<span class="grip"></span><span class="label"><span class="num"></span><span class="title"></span></span>';
    $('.num', b).textContent = 'EP' + ep.number;
    $('.title', b).textContent = ep.title;
    b.addEventListener('click', () => insert(i, b));
    return b;
  }
  function render() {
    shelf.innerHTML = ''; list.innerHTML = '';
    eps.forEach((ep, i) => { shelf.appendChild(cartEl(ep, i)); list.appendChild(cartEl(ep, i)); });
  }

  function flyToSlot(fromEl, ep) {
    const a = fromEl.getBoundingClientRect(), b = slot.getBoundingClientRect();
    if (!a.width || matchMedia('(prefers-reduced-motion: reduce)').matches) return Promise.resolve();
    const fly = fromEl.cloneNode(true);
    fly.classList.remove('out');
    fly.classList.add('flycart');
    Object.assign(fly.style, { left: a.left + 'px', top: a.top + 'px', width: a.width + 'px', height: a.height + 'px' });
    document.body.appendChild(fly);
    const s = Math.max(b.width / a.width, 0.12);
    const dx = b.left + b.width / 2 - (a.left + a.width * s / 2), dy = b.top - a.height * s;
    const mid = `translate(${(dx + a.left) / 2 - a.left}px, ${Math.min(a.top, b.top) - a.top - 30 * u}px) scale(${(1 + s) / 2})`;
    const anim = fly.animate([
      { transform: 'translate(0,0) scale(1)', opacity: 1 },
      { transform: mid, opacity: 1, offset: 0.55 },
      { transform: `translate(${dx - a.left}px, ${dy - a.top}px) scale(${s})`, opacity: 1, offset: 0.9 },
      { transform: `translate(${dx - a.left}px, ${b.top - a.top}px) scale(${s})`, opacity: 0 },
    ], { duration: 620, easing: 'ease-in-out' });
    return anim.finished.catch(() => {}).then(() => fly.remove());
  }

  function markOut(i) {
    $$('.cart').forEach(c => c.classList.toggle('out', +c.dataset.i === i));
  }

  /* ------------------------------------------------------------ playback */
  function setTitle() {
    const ep = eps[cur];
    nowtitle.innerHTML = '';
    nowtitle.append(ep ? `EP ${ep.number} · ${ep.title.toUpperCase()}` : 'CHARLIE · SEASON 1 ');
    if (!ep) { const s = document.createElement('span'); s.textContent = 'pick a cartridge'; nowtitle.append(s); }
    $('.fstitle').textContent = ep ? `EP ${ep.number} · ${ep.title.toUpperCase()}` : '';
    document.title = ep ? `EP ${ep.number}: ${ep.title} · Charlie: Season 1` : "Charlie: Season 1 · Unity's Room";
    if (ep && 'mediaSession' in navigator) {
      try { navigator.mediaSession.metadata = new MediaMetadata({ title: ep.title, artist: 'Charlie', album: `Season 1 · Episode ${ep.number}` }); } catch (e) {}
    }
  }
  function showMsg(a, b) { $('#msg1').textContent = a; $('#msg2').textContent = b || ''; msg.hidden = false; }
  function hideMsg() { msg.hidden = true; }

  function unload() {
    vid.pause();
    vid.removeAttribute('src');
    vid.load();             // frees the previous episode's buffer
  }

  function insert(i, fromEl) {
    if (!eps.length) return;
    i = (i + eps.length) % eps.length;
    const ep = eps[i];
    SFX.insert();
    const shelfCart = $(`#shelf .cart[data-i="${i}"]`);
    if (document.body.classList.contains('small') && fromEl && fromEl.closest('#list')) {
      stage.scrollIntoView({ behavior: 'smooth', block: 'start' });
      fromEl = shelfCart;
    }
    if (!fromEl || fromEl.closest('#tv') || fromEl.closest('#bar')) fromEl = shelfCart;
    if (cur >= 0 && cur !== i) SFX.eject();
    slot.classList.remove('in');
    const flight = flyToSlot(fromEl || shelfCart, ep);
    cur = i;
    markOut(i);
    setTitle();
    hideMsg();
    idle.hidden = true;
    tv.classList.add('on');
    holdStatic();
    seekfill.style.width = '0';
    // load and start right here in the tap handler, so every browser counts it as a user gesture
    unload();
    vid.src = ep.video;
    const p = vid.play();
    if (p && p.catch) p.catch(err => {
      if (err && err.name === 'NotAllowedError') { endStatic(); showMsg('READY', 'TAP TO PLAY'); }
    });
    flight.then(() => {
      const b = $('b', slot);
      slot.style.setProperty('--c', ep.color || '#888');
      b.dataset.n = ep.number;
      void slot.offsetWidth;
      slot.classList.add('in');
    });
    updatePlayBtns();
  }

  function toggle() {
    if (cur < 0) return insert(0);
    SFX.click();
    if (vid.ended) { vid.currentTime = 0; }
    if (vid.paused) { hideMsg(); vid.play().catch(() => showMsg('READY', 'TAP TO PLAY')); }
    else vid.pause();
  }
  function step(d) { insert(cur < 0 ? (d > 0 ? 0 : eps.length - 1) : cur + d); }

  function updatePlayBtns() {
    const playing = cur >= 0 && !vid.paused && !vid.ended;
    $$('.playbtn').forEach(b => {
      b.firstChild.nodeValue = playing ? '❚❚' : '▶';
      const sm = $('small', b); if (sm) sm.textContent = playing ? 'PAUSE' : 'PLAY';
    });
  }

  vid.addEventListener('playing', () => { endStatic(250); hideMsg(); updatePlayBtns(); });
  vid.addEventListener('waiting', () => { if (!vid.paused) showStatic(400); });
  vid.addEventListener('pause', () => { updatePlayBtns(); if (!vid.ended && cur >= 0 && vid.currentTime > 0) showMsg('PAUSED', 'TAP TO PLAY'); });
  vid.addEventListener('play', updatePlayBtns);
  vid.addEventListener('ended', () => {
    updatePlayBtns(); showStatic(700);
    const last = cur === eps.length - 1;
    showMsg(`END OF EP ${eps[cur].number}`, last ? 'MORE SOON. PRESS PLAY TO REWATCH' : 'PRESS NEXT FOR THE NEXT ONE');
  });
  vid.addEventListener('error', () => {
    if (!vid.getAttribute('src')) return;
    endStatic(); showMsg('TAPE ERROR', 'TAP TO TRY AGAIN');
    msg.dataset.retry = '1';
  });
  vid.addEventListener('timeupdate', () => {
    if (!vid.duration) return;
    const pc = vid.currentTime / vid.duration * 100;
    seekfill.style.width = pc + '%';
    seek.setAttribute('aria-valuenow', Math.round(pc));
  });

  // tap the screen: play/pause (or start episode 1)
  idle.addEventListener('click', () => insert(0));
  msg.addEventListener('click', () => {
    if (msg.dataset.retry) { delete msg.dataset.retry; insert(cur); return; }
    toggle();
  });
  vid.addEventListener('click', toggle);

  // seek bar
  function seekTo(e) {
    if (cur < 0 || !vid.duration) return;
    const r = seek.getBoundingClientRect();
    const x = Math.min(Math.max((e.clientX - r.left) / r.width, 0), 1);
    vid.currentTime = x * vid.duration;
  }
  let seeking = false;
  seek.addEventListener('pointerdown', e => { seeking = true; seek.setPointerCapture(e.pointerId); seekTo(e); });
  seek.addEventListener('pointermove', e => { if (seeking) seekTo(e); });
  seek.addEventListener('pointerup', () => { seeking = false; });
  seek.addEventListener('keydown', e => {
    if (cur < 0 || !vid.duration) return;
    if (e.key === 'ArrowRight') { vid.currentTime = Math.min(vid.duration, vid.currentTime + 5); e.preventDefault(); e.stopPropagation(); }
    if (e.key === 'ArrowLeft') { vid.currentTime = Math.max(0, vid.currentTime - 5); e.preventDefault(); e.stopPropagation(); }
  });

  /* ------------------------------------------------------------ fullscreen (the TV, with its scanlines) */
  function isFull() { return document.fullscreenElement || document.webkitFullscreenElement; }
  function full() {
    SFX.click();
    if (isFull()) { (document.exitFullscreen || document.webkitExitFullscreen).call(document); return; }
    if (tv.requestFullscreen) tv.requestFullscreen().catch(() => nativeFull());
    else if (tv.webkitRequestFullscreen) tv.webkitRequestFullscreen();
    else nativeFull();
  }
  function nativeFull() { if (cur >= 0 && vid.webkitEnterFullscreen) vid.webkitEnterFullscreen(); }
  let hideT = 0;
  function pokeBar() {
    tv.classList.remove('hidebar');
    clearTimeout(hideT);
    hideT = setTimeout(() => { if (isFull() && !vid.paused) tv.classList.add('hidebar'); }, 3000);
  }
  tv.addEventListener('pointermove', () => { if (isFull()) pokeBar(); });
  tv.addEventListener('pointerdown', () => { if (isFull()) pokeBar(); });
  ['fullscreenchange', 'webkitfullscreenchange'].forEach(ev => document.addEventListener(ev, () => {
    tv.classList.remove('hidebar');
    if (isFull()) { tv.style.setProperty('--u', Math.min(innerWidth / 107, innerHeight / 69) + 'px'); pokeBar(); }
    else tv.style.removeProperty('--u');
  }));

  /* ------------------------------------------------------------ buttons + keys */
  const ACTS = { play: toggle, next: () => step(1), prev: () => step(-1), full };
  $$('[data-act]').forEach(b => b.addEventListener('click', e => { e.stopPropagation(); ACTS[b.dataset.act](); }));
  document.addEventListener('keydown', e => {
    if (e.target.closest && e.target.closest('button, #seek') && (e.key === 'Enter' || e.key === ' ')) return;
    if (e.key === ' ' || e.key === 'k') { e.preventDefault(); toggle(); }
    else if (e.key === 'ArrowRight' || e.key === 'n') step(1);
    else if (e.key === 'ArrowLeft' || e.key === 'p') step(-1);
    else if (e.key === 'f') full();
  });

  /* ------------------------------------------------------------ the crowned Roomba wanders (light: one small element) */
  const HOME = [52, 177];
  const TRIPS = [
    [[52, 177], [80, 196], [120, 206], [168, 204], [200, 206], [168, 212], [110, 206], [70, 194], [52, 177]],
    [[52, 177], [90, 200], [140, 212], [186, 210], [150, 200], [100, 198], [52, 177]],
    [[52, 177], [70, 190], [130, 196], [140, 214], [96, 214], [64, 196], [52, 177]],
  ];
  const LINES = ['BEEP.', 'ALL HAIL ME', 'I ATE A CABLE', 'NO PUSH TO MAIN', 'BEEP BOOP', 'CRUMBS DETECTED'];
  let trip = null, tripN = 0;
  function roombaTrip() {
    if (document.hidden || trip || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const pts = TRIPS[tripN++ % TRIPS.length];
    const frames = pts.map(([x, y]) => ({ transform: `translate(${(x - HOME[0]) * u}px, ${(y - HOME[1]) * u}px)` }));
    let dist = 0;
    for (let k = 1; k < pts.length; k++) dist += Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]);
    const dur = dist * 90;
    trip = roomba.animate(frames, { duration: dur, easing: 'linear' });
    // face the way it is going
    let acc = 0;
    const turns = [];
    for (let k = 1; k < pts.length; k++) {
      turns.push(setTimeout(() => roomba.classList.toggle('left', pts[k][0] < pts[k - 1][0]), acc / dist * dur));
      acc += Math.hypot(pts[k][0] - pts[k - 1][0], pts[k][1] - pts[k - 1][1]);
    }
    trip.finished.catch(() => {}).then(() => { turns.forEach(clearTimeout); roomba.classList.remove('left'); trip = null; });
  }
  function schedule() { setTimeout(() => { roombaTrip(); schedule(); }, 18000 + Math.random() * 16000); }
  setTimeout(roombaTrip, 4000);
  schedule();
  roomba.addEventListener('click', () => {
    SFX.roomba();
    roomba.classList.remove('spin'); void roomba.offsetWidth; roomba.classList.add('spin');
    const r = roomba.getBoundingClientRect(), s = stage.getBoundingClientRect();
    bubble.textContent = LINES[Math.random() * LINES.length | 0];
    bubble.style.left = (r.left - s.left + r.width / 2) + 'px';
    bubble.style.top = (r.top - s.top - 2 * u) + 'px';
    bubble.classList.add('show');
    clearTimeout(bubble._t);
    bubble._t = setTimeout(() => bubble.classList.remove('show'), 1800);
  });
  addEventListener('resize', () => { if (trip) trip.cancel(); placeP1(); });

  /* ------------------------------------------------------------ player 1 select: tap Unity Eagle */
  const P1_LINES = ['1P READY!', 'PRESS START', 'EAGLE MODE', 'GLITCH ON'];
  let p1n = 0;
  p1.addEventListener('click', () => {
    SFX.p1();
    p1.classList.remove('go'); void p1.offsetWidth; p1.classList.add('go');
    const r = p1.getBoundingClientRect(), s = stage.getBoundingClientRect();
    bubble.textContent = P1_LINES[p1n++ % P1_LINES.length];
    bubble.style.left = Math.min(r.left - s.left + r.width / 2, s.width - bubble.offsetWidth / 2 - 2 * u) + 'px';
    bubble.style.top = (r.top - s.top - 1 * u) + 'px';
    bubble.classList.add('show');
    clearTimeout(bubble._t);
    bubble._t = setTimeout(() => bubble.classList.remove('show'), 1800);
  });
  p1.addEventListener('animationend', () => p1.classList.remove('go'));

  /* ------------------------------------------------------------ load the episode list */
  fetch('episodes.json', { cache: 'no-cache' })
    .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(data => {
      eps = (Array.isArray(data) ? data : data.episodes || [])
        .filter(e => e && e.video && e.title)
        .sort((a, b) => (+a.number || 0) - (+b.number || 0));
      render();
      setTitle();
    })
    .catch(() => { idle.hidden = true; showMsg('NO CARTRIDGES', 'episodes.json did not load'); });
})();
