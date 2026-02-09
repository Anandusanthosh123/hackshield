document.addEventListener("DOMContentLoaded", function () {

  const domainEl = document.getElementById("domain");
  const cluesEl = document.getElementById("clues");
  const roundEl = document.getElementById("round");
  const totalEl = document.getElementById("total");
  const scoreEl = document.getElementById("score");
  const msgEl = document.getElementById("message");

  const btnSafe = document.getElementById("btn-safe");
  const btnScam = document.getElementById("btn-scam");

  const scoreForm = document.getElementById("score-form");
  const scoreInput = document.getElementById("score-input");

  const questions = [
    { domain: "apple.com", safe: true, clues: "Official Apple website." },
    { domain: "paypal-secure-login.net", safe: false, clues: "Fake PayPal login." },
    { domain: "microsoft.com", safe: true, clues: "Trusted Microsoft domain." },
    { domain: "google.com", safe: true, clues: "Well-known Google service." },
    { domain: "github.com", safe: true, clues: "Official GitHub domain." },
    { domain: "bank-alert-login.co", safe: false, clues: "Impersonation attempt." },
    { domain: "secure-facebook.net", safe: false, clues: "Fake alert." },
    { domain: "bankofamerica-login.com", safe: false, clues: "Fake bank domain." }
  ];

  let i = 0;
  let score = 0;
  let locked = false;

  totalEl.textContent = questions.length;

  function load() {
    const q = questions[i];
    domainEl.textContent = q.domain;
    cluesEl.textContent = q.clues;
    roundEl.textContent = i + 1;
    msgEl.textContent = "";
    locked = false;
  }

  function answer(choice) {
    if (locked) return;
    locked = true;

    if (questions[i].safe === choice) {
      score++;
      scoreEl.textContent = score;
      msgEl.textContent = "✔ Correct";
    } else {
      msgEl.textContent = "✘ Incorrect";
    }

    setTimeout(() => {
      i++;
      if (i === questions.length) {
        finish();
      } else {
        load();
      }
    }, 800);
  }

  function finish() {
    btnSafe.disabled = true;
    btnScam.disabled = true;

    const xp = score * 10;

    domainEl.textContent = "Game Complete";
    cluesEl.textContent = `Final Score: ${score} / ${questions.length}`;
    msgEl.textContent = `+${xp} XP earned`;

    scoreInput.value = xp;

    setTimeout(() => {
      scoreForm.submit();
    }, 1200);
  }

  btnSafe.onclick = () => answer(true);
  btnScam.onclick = () => answer(false);

  load();
});
