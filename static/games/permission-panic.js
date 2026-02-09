const scenarios = [
  { app: "Flashlight App", perm: "Access Contacts", safe: false, reason: "Flashlights don’t need contacts." },
  { app: "Camera App", perm: "Access Camera", safe: true, reason: "Camera apps need camera access." },
  { app: "Game App", perm: "Read SMS", safe: false, reason: "Games should not read messages." },
  { app: "Notes App", perm: "Access Storage", safe: true, reason: "Notes need storage to save files." },
  { app: "Wallpaper App", perm: "Access Microphone", safe: false, reason: "Wallpaper apps don’t need mic access." },
  { app: "Maps App", perm: "Access Location", safe: true, reason: "Maps require location data." },
  { app: "Calculator", perm: "Access Camera", safe: false, reason: "Calculator has no camera use." },
  { app: "Voice Recorder", perm: "Access Microphone", safe: true, reason: "Recording requires mic access." },
  { app: "Music Player", perm: "Access Contacts", safe: false, reason: "Music doesn’t need contacts." },
  { app: "Cloud Backup", perm: "Access Storage", safe: true, reason: "Backup apps need file access." }
];

let index = 0;
let xp = 0;
let risk = 0;

const appBox = document.getElementById("app-name");
const permBox = document.getElementById("permission");
const xpBox = document.getElementById("xp");
const riskBox = document.getElementById("risk");
const feedback = document.getElementById("feedback");
const riskBar = document.getElementById("risk-bar");

function loadScenario() {
  if (index >= scenarios.length) {
    endGame();
    return;
  }

  const s = scenarios[index];
  appBox.innerText = `📱 ${s.app}`;
  permBox.innerText = `Permission Request: ${s.perm}`;
  feedback.innerText = "";
}

function choose(allow) {
  const s = scenarios[index];
  const correct = allow === s.safe;

  if (correct) {
    xp += 10;
    feedback.innerText = "✅ Correct! " + s.reason;
  } else {
    risk += 15;
    feedback.innerText = "❌ Wrong! " + s.reason;
  }

  xpBox.innerText = xp;
  riskBox.innerText = risk + "%";
  riskBar.style.width = Math.min(risk, 100) + "%";

  index++;
  setTimeout(loadScenario, 1200);
}

function endGame() {
  appBox.innerText = "🎉 Game Completed!";
  permBox.innerText = `You earned ${xp} XP`;

  feedback.innerText =
    risk >= 50
      ? "⚠️ Too many risky permissions."
      : "🛡️ Excellent permission awareness!";

  document.querySelector(".buttons").style.display = "none";

  // ✅ SEND XP TO DJANGO
  document.getElementById("final-score").value = xp;
  document.getElementById("game-complete-form").submit();
}

loadScenario();
