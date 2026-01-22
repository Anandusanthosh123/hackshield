// spot-the-phish.js (vanilla) — interactive game logic
(() => {
  'use strict';

  /* --------------------- Sample dataset ---------------------
     Replace or extend with server-fed JSON if you like.
     Each email: {id, from, subject, body, links:[], isPhish, reasons: []}
  -----------------------------------------------------------*/
  const EMAILS = [
    {
      id:1,
      from: "support@yourbank-secure.com",
      subject: "Important: Verify your account immediately",
      body: "Dear Customer,\n\nWe detected unusual activity on your account. Verify now: https://yourbank.com.verify.login/validate\n\nSincerely,\nYour Bank",
      links: ["https://yourbank.com.verify.login/validate"],
      isPhish: true,
      reasons: ["suspicious sender domain","malicious link domain","urgent tone"]
    },
    {
      id:2,
      from: "no-reply@github.com",
      subject: "New sign-in to your GitHub account",
      body: "We noticed a new sign-in from a trusted device. If this wasn't you, change your password here: https://github.com/settings/security",
      links: ["https://github.com/settings/security"],
      isPhish: false,
      reasons: ["trusted domain","secure link"]
    },
    {
      id:3,
      from: "it@company.local",
      subject: "Payroll update — confidential attachment",
      body: "Hi,\nSee attached payroll update. Please open the attached file immediately.\n\nThanks,\nIT",
      links: [],
      isPhish: true,
      reasons: ["unexpected attachment request","internal look but suspicious"]
    },
    {
      id:4,
      from: "support@apple.com",
      subject: "Your Apple ID has been locked",
      body: "Your Apple ID was locked due to suspicious activity. Unlock it at https://appleid.apple.com/security (this is safe)",
      links: ["https://appleid.apple.com/security"],
      isPhish: false,
      reasons: ["trusted domain"]
    },
    {
      id:5,
      from: "admin@company-payments.ru",
      subject: "Invoice overdue: Pay now",
      body: "Dear,\nYour invoice is overdue. Pay here: http://pay.company-payments.ru/invoice\n\nRegards",
      links: ["http://pay.company-payments.ru/invoice"],
      isPhish: true,
      reasons:["foreign domain","payment request"]
    },
    // more examples...
  ];

  /* --------------------- state --------------------- */
  const TOTAL_ROUNDS = 10;
  let pool = [];         // shuffled selection
  let round = 0;
  let score = 0;
  let timerHandle = null;
  let timeLeft = 20;     // seconds per round
  const TIME_PER_ROUND = 20;

  /* ---------- Dom refs ---------- */
  const $ = sel => document.querySelector(sel);
  const emailFrom = $('#email-from');
  const emailSubject = $('#email-subject');
  const emailBody = $('#email-body');
  const emailLinks = $('#email-links');
  const feedback = $('#feedback');
  const roundEl = $('#round');
  const totalEl = $('#total');
  const scoreEl = $('#score');
  const timerEl = $('#timer');
  const progressFill = $('#progress-fill');
  const panel = $('#panel');

  const btnReal = $('#btn-real');
  const btnPhish = $('#btn-phish');
  const scoreForm = document.getElementById('score-form');
  const scoreInput = document.getElementById('score-input');

  /* ---------- helpers ---------- */
  function shuffle(arr){
    for(let i=arr.length-1;i>0;i--){
      const j = Math.floor(Math.random()*(i+1));
      [arr[i],arr[j]]=[arr[j],arr[i]];
    }
    return arr;
  }

  function pickPool(){
    const poolCandidates = EMAILS.slice(); // copy
    shuffle(poolCandidates);
    // create pool of TOTAL_ROUNDS or less if dataset small
    pool = poolCandidates.slice(0, Math.min(TOTAL_ROUNDS, poolCandidates.length));
    // if not enough, repeat items (safe fallback)
    while(pool.length < TOTAL_ROUNDS) pool = pool.concat(shuffle(EMAILS.slice()).slice(0, TOTAL_ROUNDS-pool.length));
  }

  function formatLinks(links){
    if(!links || links.length===0) return '';
    emailLinks.innerHTML='';
    links.forEach((lnk,i)=>{
      const a = document.createElement('a');
      a.href = lnk;
      a.target='_blank';
      a.rel='noopener noreferrer';
      a.textContent = (new URL(lnk)).hostname + (i>0? ' • ' : '');
      emailLinks.appendChild(a);
    });
  }

  function renderEmail(item){
    // clear highlight classes
    panel.querySelectorAll('.hilite-bad,.hilite-good').forEach(n=>n.classList.remove('hilite-bad','hilite-good'));
    emailFrom.textContent = item.from;
    emailSubject.textContent = item.subject;
    emailBody.textContent = item.body;
    formatLinks(item.links);
    // small fade animation
    panel.classList.remove('fade-anim'); void panel.offsetWidth;
    panel.classList.add('fade-anim');
    // set accessible live text
  }

  /* ---------- feedback UI ---------- */
  function showFeedback(correct, reasons){
    feedback.innerHTML = '';
    feedback.className = 'feedback ' + (correct ? 'correct' : 'wrong');
    const txt = document.createElement('div');
    txt.innerHTML = correct ? `✅ <strong>Good —</strong> ${reasons.slice(0,2).join(', ')}` :
                               `❌ <strong>Not quite —</strong> ${reasons.slice(0,2).join(', ')}`;
    feedback.appendChild(txt);

    // show reason chips
    const chips = document.createElement('div'); chips.className='reason-list';
    reasons.forEach(r=>{
      const c = document.createElement('div'); c.className='reason'; c.textContent = r; chips.appendChild(c);
    });
    feedback.appendChild(chips);

    // animate panel
    panel.querySelector('.email-card').classList.toggle('show-correct', correct);
    panel.querySelector('.email-card').classList.toggle('show-wrong', !correct);

    // clear highlight after 2s
    setTimeout(()=> {
      panel.querySelector('.email-card').classList.remove('show-correct','show-wrong');
    }, 1400);
  }

  /* ---------- timer ---------- */
  function startTimer(){
    clearInterval(timerHandle);
    timeLeft = TIME_PER_ROUND;
    timerEl.textContent = `${timeLeft}s`;
    timerHandle = setInterval(()=>{
      timeLeft--;
      timerEl.textContent = `${timeLeft}s`;
      if(timeLeft<=0){
        clearInterval(timerHandle);
        onAnswer(null, true); // timed out
      }
    },1000);
  }
  function stopTimer(){ clearInterval(timerHandle); timerEl.textContent='--'; }

  /* ---------- progress ---------- */
  function updateProgress(){
    roundEl.textContent = round;
    totalEl.textContent = TOTAL_ROUNDS;
    scoreEl.textContent = score;
    const pct = Math.round((round/TOTAL_ROUNDS)*100);
    progressFill.style.width = pct+'%';
  }

  /* ---------- answer handling ---------- */
  function onAnswer(chosen, timedOut=false){
    // disable buttons briefly
    btnReal.disabled = true; btnPhish.disabled = true;
    stopTimer();

    const item = pool[round-1];
    let correct = false;
    if(timedOut){
      correct = false;
    } else {
      const userChosePhish = (chosen === 'phish');
      correct = (userChosePhish === Boolean(item.isPhish));
    }

    // scoring: correct +2, wrong -1 (min 0)
    if(correct) score += 2; else score = Math.max(0, score - 1);
    // reveal reasons (explainable)
    const reasons = item.reasons || (item.isPhish ? ['suspicious indicators'] : ['looks safe']);
    showFeedback(correct, reasons);

    // highlight suspicious tokens in the DOM (simple heuristics)
    highlightReasons(item);

    // small confetti on correct
    if(correct) burstConfetti();

    // update UI and proceed to next after delay
    updateProgress();

    // store score hidden input for fallback
    if(scoreInput) scoreInput.value = score;

    setTimeout(()=> {
      // next round
      if(round < TOTAL_ROUNDS){
        round++;
        renderEmail(pool[round-1]);
        btnReal.disabled = false; btnPhish.disabled = false;
        startTimer();
        updateProgress();
        feedback.className = 'feedback'; feedback.innerHTML='';
      } else {
        // finished
        endGame();
      }
    }, 1400);
  }

  /* ---------- highlight heuristics ---------- */
  function highlightReasons(item){
    // highlight sender if suspicious
    const fromText = item.from || '';
    const domMatch = fromText.match(/@(.+)$/);
    if(domMatch){
      const domain = domMatch[1].toLowerCase();
      if(domain.includes('verify')|| domain.includes('secure') || domain.includes('payments') || domain.includes('.ru')){
        // wrap from element
        emailFrom.innerHTML = `<span class="hilite-bad">${emailFrom.textContent}</span>`;
      } else {
        emailFrom.innerHTML = `<span class="hilite-good">${emailFrom.textContent}</span>`;
      }
    }

    // highlight links
    if(item.links && item.links.length){
      emailLinks.querySelectorAll('a').forEach(a=>{
        try{
          const host = new URL(a.href).hostname;
          if(host.includes('github.com') || host.includes('apple.com')) {
            a.classList.add('good-link');
            a.style.boxShadow = 'inset 0 0 0 2px rgba(126,245,184,0.06)';
          } else {
            a.classList.add('bad-link');
            a.style.boxShadow = 'inset 0 0 0 2px rgba(255,120,120,0.04)';
          }
        }catch(e){}
      });
    }
  }

  /* ---------- end game ---------- */
  function endGame(){
    stopTimer();
    // show final modal (simple)
    const finalText = `You scored ${score} / ${TOTAL_ROUNDS*2}`;
    feedback.className = 'feedback correct';
    feedback.innerHTML = `<div><strong>Finished</strong> — ${finalText}</div>`;
    // POST score via form fallback: keep CSRF
    if(scoreForm){
      // set value already set
      try{
        scoreForm.querySelector('[name="score"]').value = score;
        // send fetch to current URL if needed (optional)
        fetch(location.href, {method:'POST', body: new FormData(scoreForm)}).catch(()=>{/*ignore*/});
      }catch(e){}
    }
    // disable controls
    btnReal.disabled = true; btnPhish.disabled = true;
  }

  /* ---------- confetti (very small, no libs) ---------- */
  function burstConfetti(){
    // small DOM confetti using emojis for low overhead
    const frag = document.createDocumentFragment();
    for(let i=0;i<18;i++){
      const el = document.createElement('div');
      el.textContent = (i%2? '✨':'💠');
      el.style.position='fixed';
      el.style.left = (50 + (Math.random()*160-80)) + '%';
      el.style.top = (20 + Math.random()*30) + '%';
      el.style.opacity = '0';
      el.style.fontSize = (10 + Math.random()*18)+'px';
      el.style.pointerEvents='none';
      el.style.transform = `translateY(-10px) scale(.8)`;
      el.style.transition = 'transform .9s cubic-bezier(.2,.9,.3,1), opacity .9s';
      document.body.appendChild(el);
      requestAnimationFrame(()=> {
        el.style.opacity='1';
        el.style.transform = `translateY(${120 + Math.random()*120}px) scale(1) rotate(${Math.random()*60-30}deg)`;
      });
      setTimeout(()=> el.remove(), 1100);
    }
  }

  /* ---------- keyboard shortcuts ---------- */
  document.addEventListener('keydown', (e) => {
    if(e.key === 'r' || e.key === 'R') btnReal.click();
    if(e.key === 'p' || e.key === 'P') btnPhish.click();
    if(e.key === 'Enter'){ /* allow Enter to submit last focused */
      const active = document.activeElement;
      if(active === btnReal) btnReal.click();
      if(active === btnPhish) btnPhish.click();
    }
  });

  /* ---------- init & wire ---------- */
  function attachHandlers(){
    btnReal.addEventListener('click', ()=> onAnswer('real'));
    btnPhish.addEventListener('click', ()=> onAnswer('phish'));
  }

  function startGame(){
    pickPool();
    round = 1; score = 0;
    totalEl.textContent = TOTAL_ROUNDS;
    renderEmail(pool[0]);
    startTimer();
    attachHandlers();
    updateProgress();
  }

  // render and update progress UI initially
  document.addEventListener('DOMContentLoaded', () => {
    try{ startGame(); }catch(e){ console.error(e); }
  });

})();
