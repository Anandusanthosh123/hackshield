(function () {

  const domainEl = document.getElementById("domain");
  const cluesEl = document.getElementById("clues");
  const explainEl = document.getElementById("explain");
  const card = document.getElementById("site-card");

  const roundEl = document.getElementById("round");
  const scoreEl = document.getElementById("score");
  const scoreInput = document.getElementById("score-input");

  const btnSafe = document.getElementById("btn-safe");
  const btnScam = document.getElementById("btn-scam");

  const data = [
    { domain: "apple.com", safe: true, clues: "Official Apple domain.\nSSL valid.\nNo urgency." },
    { domain: "paypal-secure-login.net", safe: false, clues: "Odd domain.\nUrgent wording.\nAsks for credentials." },
    { domain: "microsoft.com", safe: true, clues: "Trusted worldwide domain." },
    { domain: "amaz0n-security-alert.com", safe: false, clues: "Misspelled brand name.\nUrgent language." },
    { domain: "github.com", safe: true, clues: "Official GitHub domain.\nTrusted platform." },
    { domain: "netflix-account-verify.net", safe: false, clues: "Account verification scam." },
    { domain: "stackoverflow.com", safe: true, clues: "Legitimate developer community." },
    { domain: "bankofamerica-login.com", safe: false, clues: "Fake bank login page." }
  ];

  let index = 0;
  let score = 0;

  function loadRound() {
    const item = data[index];
    domainEl.textContent = item.domain;
    cluesEl.textContent = item.clues;

    explainEl.textContent = "";
    explainEl.className = "explain";

    card.classList.remove("animate-in");
    void card.offsetWidth;
    card.classList.add("animate-in");

    roundEl.textContent = index + 1;
  }

  function handleChoice(isSafe) {
    const item = data[index];
    const correct = item.safe === isSafe;

    if (correct) {
      score++;
      scoreEl.textContent = score;
    }

    explainEl.textContent = correct
      ? "✔ Correct — you spotted it!"
      : "✘ Incorrect — review the domain carefully.";

    explainEl.classList.add(correct ? "correct" : "wrong");

    setTimeout(() => {
      index++;
      if (index >= data.length) {
        finishGame();
      } else {
        loadRound();
      }
    }, 1100);
  }

  function finishGame() {
    btnSafe.disabled = true;
    btnScam.disabled = true;

    const xpEarned = score * 10;
    scoreInput.value = xpEarned;

    // ✅ Store banner message ONLY (no UI here)
    sessionStorage.setItem(
      "postGameBanner",
      `Game complete! +${xpEarned} XP`
    );

    // ✅ Submit like other games
    document.getElementById("score-form").submit();
  }

  btnSafe.addEventListener("click", () => handleChoice(true));
  btnScam.addEventListener("click", () => handleChoice(false));

  loadRound();

})();
