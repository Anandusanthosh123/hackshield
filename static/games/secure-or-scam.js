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

  // Example dataset (you can replace with your own)
  const data = [
    { domain: "apple.com", safe: true, clues: "Official Apple domain.\nSSL valid.\nNo urgency." },
    { domain: "paypal-secure-login.net", safe: false, clues: "Odd domain.\nUrgent wording.\nAsks for credentials." },
    { domain: "microsoft.com", safe: true, clues: "Trusted worldwide domain." }
  ];

  let index = 0;
  let score = 0;

  function loadRound() {
    const item = data[index];
    domainEl.textContent = item.domain;
    cluesEl.textContent = item.clues;

    explainEl.classList.add("hidden");
    explainEl.classList.remove("show");

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
    explainEl.classList.remove("hidden");
    explainEl.classList.add("show");

    setTimeout(() => {
      index++;
      if (index >= data.length) {
        finishGame();
      } else {
        loadRound();
      }
    }, 1200);
  }

  function finishGame() {
    scoreInput.value = score * 10;

    fetch(window.location.pathname, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      body: new URLSearchParams({ score: scoreInput.value })
    }).then(() => (window.location.href = "/games/"));
  }

  function getCookie(name) {
    const match = document.cookie.split("; ").find(c => c.startsWith(name + "="));
    return match ? decodeURIComponent(match.split("=")[1]) : "";
  }

  btnSafe.addEventListener("click", () => handleChoice(true));
  btnScam.addEventListener("click", () => handleChoice(false));

  loadRound();

})();
