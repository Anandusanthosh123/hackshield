document.addEventListener("DOMContentLoaded", () => {

  const domainEl = document.getElementById("domain");
  const cluesEl = document.getElementById("clues");
  const roundEl = document.getElementById("round");
  const totalEl = document.getElementById("total");
  const scoreEl = document.getElementById("score");
  const explainEl = document.getElementById("explain");
  const card = document.getElementById("site-card");

  const btnSafe = document.getElementById("btn-safe");
  const btnScam = document.getElementById("btn-scam");

  const scoreForm = document.getElementById("score-form");
  const scoreInput = document.getElementById("score-input");

  const data = [
    { domain: "apple.com", safe: true, clues: "Official Apple website." },
    { domain: "paypal-secure-login.net", safe: false, clues: "Fake PayPal login page." },
    { domain: "microsoft.com", safe: true, clues: "Trusted Microsoft domain." },
    { domain: "google.com", safe: true, clues: "Well-known Google service." },
    { domain: "github.com", safe: true, clues: "Official GitHub developer platform." },
    { domain: "bank-alert-login.co", safe: false, clues: "Impersonation attempt." },
    { domain: "secure-facebook.net", safe: false, clues: "Fake security alert." },
    { domain: "bankofamerica-login.com", safe: false, clues: "Fake bank domain." }
  ];

  let index = 0;
  let score = 0;
  let locked = false;

  totalEl.textContent = data.length;

  function showMessage(msg) {
    explainEl.textContent = msg;
    explainEl.style.display = "block";
  }

  function hideMessage() {
    explainEl.style.display = "none";
  }

  function animateCard() {
    card.classList.remove("fade");
    void card.offsetWidth;
    card.classList.add("fade");
  }

  function loadRound() {
    const item = data[index];

    domainEl.textContent = item.domain;
    cluesEl.textContent = item.clues;
    roundEl.textContent = index + 1;

    hideMessage();
    animateCard();
    locked = false;
  }

  function answer(choice) {
    if (locked) return;
    locked = true;

    const correct = data[index].safe === choice;

    if (correct) {
      score++;
      scoreEl.textContent = score;
      showMessage("✔ Correct — you spotted it!");
    } else {
      showMessage("✘ Incorrect — check the domain carefully.");
    }

    setTimeout(() => {
      index++;
      index >= data.length ? finishGame() : loadRound();
    }, 900);
  }

  function finishGame() {
    btnSafe.disabled = true;
    btnScam.disabled = true;

    const xp = score * 10;

    domainEl.textContent = "🎉 Game Complete!";
    cluesEl.innerHTML = `
      Final Score: <strong>${score} / ${data.length}</strong><br>
      <span style="color:#32ffd2;font-weight:bold">+${xp} XP Gained</span>
    `;

    showMessage("Saving your progress…");

    scoreInput.value = xp;

    setTimeout(() => {
      scoreForm.submit();
    }, 1500);
  }

  btnSafe.onclick = () => answer(true);
  btnScam.onclick = () => answer(false);

  loadRound();
});
