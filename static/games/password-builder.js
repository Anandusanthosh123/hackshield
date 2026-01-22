(function(){

/* ELEMENTS */
const pw = document.getElementById("pw");
const generateBtn = document.getElementById("generate");
const saveBtn = document.getElementById("save");
const copyBtn = document.getElementById("copyBtn");
const meterFill = document.getElementById("meter-fill");
const meterText = document.getElementById("meter-text");
const checksEl = document.getElementById("checks");
const crackTimeEl = document.getElementById("crack-time");
const mnemonicEl = document.getElementById("mnemonic");
const feedbackEl = document.getElementById("feedback");
const scoreInput = document.getElementById("score-input");
const themeToggle = document.getElementById("themeToggle");

/* PASSWORD GENERATOR */
function random(arr){ return arr[Math.floor(Math.random()*arr.length)]; }

function generatePassword(){
  const words = ["ocean","ember","matrix","shadow","cipher","galaxy","lunar","anchor","neon"];
  return random(words)+"-"+random(words)+"-"+random(words)+"-"+Math.floor(Math.random()*90+10)+"!";
}

/* CHECK RULES */
function rules(s){
  return {
    length: s.length >= 12,
    lower: /[a-z]/.test(s),
    upper: /[A-Z]/.test(s),
    number: /[0-9]/.test(s),
    symbol: /[^A-Za-z0-9]/.test(s)
  };
}

/* SCORE */
function score(r){
  let pts = 0;
  Object.values(r).forEach(v => pts += v ? 1 : 0);
  return pts;
}

/* CRACK TIME (rough) */
function crackSeconds(s){
  let pool = 0;
  if(/[a-z]/.test(s)) pool+=26;
  if(/[A-Z]/.test(s)) pool+=26;
  if(/[0-9]/.test(s)) pool+=10;
  if(/[^A-Za-z0-9]/.test(s)) pool+=32;
  pool = Math.max(pool,26);

  const entropy = Math.log2(Math.pow(pool,s.length));
  return Math.pow(2,entropy) / 1e9;
}

function niceTime(sec){
  if(sec < 1) return "< 1 sec";
  if(sec < 60) return Math.round(sec)+" sec";
  if(sec < 3600) return Math.round(sec/60)+" min";
  if(sec < 86400) return Math.round(sec/3600)+" hrs";
  if(sec < 31536000) return Math.round(sec/86400)+" days";
  return Math.round(sec/31536000)+" yrs";
}

/* MNEMONIC */
function mnemonicFor(s){
  if(s.includes("-")){
    return s.split("-").map(w => w[0].toUpperCase()).join(" • ");
  }
  return s.split("").slice(0,6).join(" ");
}

/* UI UPDATE */
function update(){
  const val = pw.value;

  const c = rules(val);
  const pts = score(c);
  const pct = (pts/5)*100;

  meterFill.style.width = pct+"%";
  meterFill.style.background = pct > 60 ? "var(--good)" : "var(--neon)";

  const labels = ["Very weak","Weak","Okay","Good","Strong","Excellent"];
  meterText.textContent = labels[pts];

  checksEl.querySelectorAll("[data-key]").forEach(div=>{
    div.classList.toggle("pass", c[div.dataset.key]);
  });

  crackTimeEl.textContent = niceTime(crackSeconds(val || "a"));
  mnemonicEl.textContent = mnemonicFor(val || "");

  scoreInput.value = pts * 10;
}

/* EVENTS */
pw.addEventListener("input", update);

generateBtn.addEventListener("click", ()=>{
  pw.value = generatePassword();
  update();
});

copyBtn.addEventListener("click", ()=>{
  navigator.clipboard.writeText(pw.value);
  showCopyBadge();
});

saveBtn.addEventListener("click", ()=>{
  feedbackEl.textContent = "Saving…";

  /* Submit to Django */
  fetch("",{
    method:"POST",
    headers:{
      "X-CSRFToken": getCookie("csrftoken"),
      "Content-Type":"application/x-www-form-urlencoded"
    },
    body:new URLSearchParams({ score: scoreInput.value })
  })
  .then(()=> window.location.href="/games/")
  .catch(()=> feedbackEl.textContent = "Network error");
});

/* THEME TOGGLE */
themeToggle.addEventListener("change", ()=>{
  document.body.classList.toggle("theme-red", themeToggle.checked);
});

/* COPY BADGE ANIMATION */
function showCopyBadge(){
  let badge = document.querySelector(".copy-badge");
  if(!badge){
    badge = document.createElement("div");
    badge.className = "copy-badge";
    badge.textContent = "Copied!";
    document.body.appendChild(badge);
  }
  badge.classList.add("show");
  setTimeout(()=> badge.classList.remove("show"), 1500);
}

/* CSRF helper */
function getCookie(name){
  const m = document.cookie.split("; ").find(r=>r.startsWith(name+"="));
  return m ? decodeURIComponent(m.split("=")[1]) : "";
}

/* INIT */
update();
document.getElementById("themeToggle").addEventListener("change", e => {
    if (e.target.checked) {
        document.body.classList.add("red-mode");
        localStorage.setItem("pb-theme", "red");
    } else {
        document.body.classList.remove("red-mode");
        localStorage.setItem("pb-theme", "purple");
    }
});

})();
