// static/games/password-cracker-race.js
// Password Cracker Race — improved simulation + explanations
// Pure vanilla JS — no external libs

(function () {
  // ---------- DOM ----------
  const pwListEl = document.getElementById('pw-list');
  const pwCustom = document.getElementById('pw-custom');
  const btnTest = document.getElementById('btn-test');
  const raceArea = document.getElementById('race-area');
  const pwSelectedEl = document.getElementById('pw-selected');
  const hackerFill = document.getElementById('hacker-fill');
  const userFill = document.getElementById('user-fill');
  const entropyEl = document.getElementById('entropy');
  const crackEstEl = document.getElementById('crack-est');
  const verdictEl = document.getElementById('verdict');
  const scoreInput = document.getElementById('score-input');
  const btnRestart = document.getElementById('btn-restart');
  const btnTryAgain = document.getElementById('btn-try-again');

  // ---------- Example passwords (mix of weak to strong) ----------
  const samplePasswords = [
    { pw: 'password', label: 'Very Weak — common word' },
    { pw: 'letmein123', label: 'Weak — short + digits' },
    { pw: 'blue-sky-88', label: 'Medium — passphrase + digits' },
    { pw: 'Tr0ub4dor&3', label: 'Medium-Strong — mixed classes' },
    { pw: 'CorrectHorseBatteryStaple', label: 'Strong — long passphrase' },
    { pw: '7xY!mP$9v#2Q', label: 'Strong — random characters' },
    { pw: 'sunrise-ocean-47!', label: 'Passphrase + symbol' },
    { pw: 'P@ssw0rd!2025', label: 'Common pattern but varied' }
  ];

  // ---------- Helpers ----------
  function el(tag, cl = '') {
    const d = document.createElement(tag);
    if (cl) d.className = cl;
    return d;
  }

  function bitsOfEntropy(password) {
    // approximate pool size by presence of char classes
    let pool = 0;
    if (/[a-z]/.test(password)) pool += 26;
    if (/[A-Z]/.test(password)) pool += 26;
    if (/[0-9]/.test(password)) pool += 10;
    if (/[^A-Za-z0-9]/.test(password)) pool += 32;
    pool = Math.max(pool, 26); // baseline
    // entropy = length * log2(pool)
    const entropy = password.length * Math.log2(pool);
    return Math.round(entropy);
  }

  function secondsToCrack(entropy, guessesPerSec = 1e9) {
    // naive: 2^entropy guesses required (on average half)
    const guesses = Math.pow(2, entropy);
    const seconds = guesses / guessesPerSec;
    return seconds;
  }

  function humanTime(s) {
    if (!isFinite(s) || s > 1e9) return 'Very long (years+)';
    if (s < 1) return '< 1 second';
    if (s < 60) return Math.round(s) + ' sec';
    if (s < 3600) return Math.round(s / 60) + ' min';
    if (s < 86400) return Math.round(s / 3600) + ' hrs';
    if (s < 31536000) return Math.round(s / 86400) + ' days';
    return Math.round(s / 31536000) + ' years';
  }

  // normalize entropy to a 0..100 % strength bar for UI
  function entropyToPercent(e) {
    // rough mapping: 0 bits -> 0%, 60 bits -> ~100%
    const pct = Math.max(0, Math.min(100, Math.round((e / 60) * 100)));
    return pct;
  }

  // choose visible simulation duration (seconds)
  function simulationDuration(secondsToCrack) {
    // If the theoretical crack time is huge, show a long "safe" animation but keep it playable:
    // durations scale: if secondsToCrack < 30 -> use that (fast crack)
    // if between 30 .. 3600 -> cap to 30s for animation but keep estimate shown
    // if >3600 -> cap to 25s but mark as "very long"
    if (!isFinite(secondsToCrack)) return 25;
    if (secondsToCrack <= 30) return Math.max(2, secondsToCrack); // fast attacks shown accurately
    if (secondsToCrack <= 3600) return 30;
    return 25;
  }

  // compute score (0..100). Higher is better.
  function computeScore(entropy, cracked) {
    const base = Math.min(100, Math.round((entropy / 60) * 100));
    return cracked ? Math.max(0, base - 40) : base;
  }

  // ---------- Populate choices ----------
  function renderChoices() {
    pwListEl.innerHTML = '';
    samplePasswords.forEach((row, i) => {
      const item = el('button', 'pw-item');
      item.type = 'button';
      item.setAttribute('data-pw', row.pw);
      item.innerHTML = `<strong>${row.pw}</strong><div class="pw-meta">${row.label}</div>`;
      item.addEventListener('click', () => startRace(row.pw));
      pwListEl.appendChild(item);
    });
  }

  // ---------- Race animation ----------
  let raceTimer = null;
  function startRace(password) {
    // reset UI
    clearInterval(raceTimer);
    raceArea.classList.remove('hidden');
    pwSelectedEl.textContent = password;
    hackerFill.style.width = '0%';
    userFill.style.width = '0%';
    verdictEl.textContent = '';
    scoreInput.value = '0';

    // compute metrics
    const entropy = bitsOfEntropy(password);
    const estSeconds = secondsToCrack(entropy, 1e9); // single fast GPU
    const simDur = simulationDuration(estSeconds) * 1000; // ms

    entropyEl.textContent = entropy;
    crackEstEl.textContent = humanTime(estSeconds);

    // compute UI percentages
    const strengthPct = entropyToPercent(entropy); // user fill percent
    userFill.style.transition = 'width 800ms ease';
    userFill.style.width = strengthPct + '%';

    // Decide whether hacker will succeed during simulated duration.
    // If estimated crack time <= simDur -> hacker will finish early (cracked).
    // Otherwise hacker may not reach 100% visible.
    const willCrackInSim = estSeconds * 1000 <= simDur;

    // Hacker speed: fill percent per ms
    // We want hackerFill to reach 100% in either estSeconds (if estSeconds small) or simDur (if estSeconds large)
    // Convert estSeconds to a target time for the animation:
    const targetMs = Math.min(simDur, estSeconds * 1000);
    // Protect division by zero
    const msForFull = Math.max(500, targetMs);
    // percent per ms
    const pctPerMs = 100 / msForFull;

    // Animation
    const start = performance.now();
    raceTimer = setInterval(() => {
      const now = performance.now();
      const elapsed = now - start;
      const pct = Math.min(100, Math.round(elapsed * pctPerMs));
      hackerFill.style.width = pct + '%';

      // If hacker reached 100% in this animation window -> cracked
      if (pct >= 100) {
        clearInterval(raceTimer);
        const cracked = willCrackInSim || (estSeconds * 1000 <= msForFull);
        showResult(cracked, entropy, estSeconds, password);
      }
    }, 35);

    // If we cap the animation and hacker didn't reach 100%, we still finish after simDur
    setTimeout(() => {
      if (raceTimer) {
        clearInterval(raceTimer);
        // compute visible progress (may be <100)
        const finalPct = parseInt(hackerFill.style.width, 10) || 0;
        const cracked = finalPct >= 100 && willCrackInSim;
        showResult(cracked, entropy, estSeconds, password);
      }
    }, simDur + 50);
  }

  // ---------- show explanations, update score and optionally submit ----------
  function showResult(cracked, entropy, estSeconds, password) {
    // explanations
    let explanation = '';
    if (cracked) {
      explanation = `⚠️ Cracked! Based on the computed entropy (${entropy} bits) and an attacker using a fast GPU, the estimated crack time is ${humanTime(estSeconds)} — short enough to be broken in this simulation.`;
      // give specific actionable tips
      explanation += ' Tip: increase length, prefer unpredictable passphrases or random characters, and avoid common words/patterns.';
    } else {
      explanation = `✅ Held up. Estimated crack time is ${humanTime(estSeconds)} (single-GPU). This password has ${entropy} bits of entropy and is comparatively strong for offline attacks.`;
      explanation += ' Tip: longer passphrases and mixing classes increases entropy.';
    }

    // extra, targeted advice based on weaknesses
    const adv = generateAdvice(password);
    if (adv) explanation += ' ' + adv;

    verdictEl.textContent = explanation;

    // compute score and set hidden field
    const score = computeScore(entropy, cracked);
    scoreInput.value = String(score);

    // show small result badge style
    if (cracked) {
      verdictEl.classList.remove('ok');
      verdictEl.classList.add('warn');
    } else {
      verdictEl.classList.remove('warn');
      verdictEl.classList.add('ok');
    }

    // Auto-submit after a short delay (optional) — here we submit to /games/score by posting the hidden form.
    // If you prefer not to auto-submit, comment out the next two lines.
    setTimeout(() => {
      try {
        document.getElementById('score-form').submit();
      } catch (e) {
        // fallback: just leave the result visible
        console.warn('Submit failed (maybe dev mode):', e);
      }
    }, 1100);
  }

  // generate simple tailored advice
  function generateAdvice(pw) {
    const advs = [];
    if (pw.length < 12) advs.push('Make it longer (12+ chars).');
    if (!/[A-Z]/.test(pw)) advs.push('Add uppercase letters.');
    if (!/[a-z]/.test(pw)) advs.push('Add lowercase letters.');
    if (!/[0-9]/.test(pw)) advs.push('Add numbers.');
    if (!/[^A-Za-z0-9]/.test(pw)) advs.push('Add symbols (e.g. !@#$).');
    if (/password|1234|qwerty|letmein/i.test(pw)) advs.push('Avoid common words or predictable patterns.');
    if (advs.length) return 'Advice: ' + advs.join(' ');
    return '';
  }

  // ---------- Controls ----------
  btnRestart && btnRestart.addEventListener('click', () => {
    // reset UI
    clearInterval(raceTimer);
    hackerFill.style.width = '0%';
    userFill.style.width = '0%';
    raceArea.classList.add('hidden');
    pwSelectedEl.textContent = '';
    entropyEl.textContent = '—';
    crackEstEl.textContent = '—';
    verdictEl.textContent = '';
    scoreInput.value = '0';
  });

  btnTryAgain && btnTryAgain.addEventListener('click', () => {
    // just go back to choices
    clearInterval(raceTimer);
    hackerFill.style.width = '0%';
    userFill.style.width = '0%';
    verdictEl.textContent = '';
    scoreInput.value = '0';
  });

  btnTest && btnTest.addEventListener('click', () => {
    const p = (pwCustom && pwCustom.value || '').trim();
    if (!p) {
      alert('Please type or paste a password to test.');
      return;
    }
    startRace(p);
  });

  // custom Enter key behaviour
  if (pwCustom) {
    pwCustom.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        btnTest.click();
      }
    });
  }

  // ---------- Init ----------
  function init() {
    renderChoices();
  }

  // render sample buttons
  function renderChoices() {
    pwListEl.innerHTML = '';
    samplePasswords.forEach(item => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'pw-choice';
      btn.textContent = item.pw + ' — ' + item.label;
      btn.addEventListener('click', () => startRace(item.pw));
      pwListEl.appendChild(btn);
    });
  }

  // start
  init();

})();
