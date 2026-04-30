from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Stockage en mémoire ---
projets = []
votes = {}        # { projet_id: { votant_id: note } }
actif_id = None   # projet actuellement soumis au vote

# --- Modèles ---
class ProjetIn(BaseModel):
    nom: str
    description: Optional[str] = ""

class ActifIn(BaseModel):
    id: Optional[str] = None

class VoteIn(BaseModel):
    votant: str
    note: int

# --- Routes API ---

@app.get("/projets")
def get_projets():
    return projets

@app.post("/projets")
def add_projet(data: ProjetIn):
    p = {"id": str(uuid.uuid4())[:8], "nom": data.nom, "description": data.description or ""}
    projets.append(p)
    return projets

@app.delete("/projets/{pid}")
def delete_projet(pid: str):
    global actif_id
    found = next((p for p in projets if p["id"] == pid), None)
    if not found:
        raise HTTPException(404)
    projets.remove(found)
    votes.pop(pid, None)
    if actif_id == pid:
        actif_id = None
    return projets

@app.get("/actif")
def get_actif():
    if not actif_id:
        return None
    p = next((p for p in projets if p["id"] == actif_id), None)
    return p

@app.post("/actif")
def set_actif(data: ActifIn):
    global actif_id
    actif_id = data.id
    return {"ok": True}

@app.get("/votes/{pid}")
def get_votes(pid: str, votant: Optional[str] = None):
    pvotes = votes.get(pid, {})
    if votant:
        return {"vote": pvotes.get(votant)}
    notes = list(pvotes.values())
    total = len(notes)
    avg = round(sum(notes) / total, 1) if total > 0 else 0
    rep = {}
    for n in notes:
        rep[str(n)] = rep.get(str(n), 0) + 1
    return {"total": total, "moyenne": avg, "repartition": rep}

@app.post("/votes/{pid}")
def post_vote(pid: str, data: VoteIn):
    if data.note < 1 or data.note > 5:
        raise HTTPException(400, "Note invalide")
    if pid not in votes:
        votes[pid] = {}
    votes[pid][data.votant] = data.note
    return {"ok": True}

@app.post("/reset")
def reset():
    global actif_id
    votes.clear()
    actif_id = None
    return {"projets": projets}

# --- Interface HTML ---

HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Vote Projets</title>
<script src="https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f0f2f5;color:#333;min-height:100vh}
header{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;padding:16px;text-align:center}
header h1{font-size:1.4em;font-weight:700}
header p{font-size:.85em;opacity:.85;margin-top:4px}
.container{max-width:720px;margin:0 auto;padding:20px 16px}
.card{background:#fff;padding:24px;border-radius:16px;box-shadow:0 2px 12px rgba(0,0,0,.07);margin:14px 0}
.card h2{font-size:1.1em;font-weight:700;margin-bottom:14px;color:#444}
input,textarea{width:100%;padding:11px 14px;border:2px solid #e5e7eb;border-radius:10px;font-size:.95em;font-family:inherit;transition:border .2s}
input:focus,textarea:focus{outline:none;border-color:#667eea}
textarea{resize:vertical;min-height:56px;margin-top:8px}
.btn{display:block;width:100%;padding:13px;border:none;border-radius:10px;font-size:1em;font-weight:600;cursor:pointer;margin:8px 0;transition:opacity .2s,transform .1s}
.btn:active{transform:scale(.98)}
.btn-green{background:#22c55e;color:#fff}
.btn-blue{background:#3b82f6;color:#fff}
.btn-red{background:#ef4444;color:#fff}
.btn-outline{background:#fff;color:#667eea;border:2px solid #667eea}
.btn:disabled{opacity:.45;cursor:not-allowed}
.btn-small{width:auto;padding:7px 14px;font-size:.82em;border-radius:8px}
/* Étoiles */
.stars{display:flex;justify-content:center;gap:8px;margin:22px 0 16px}
.star{font-size:3.4em;cursor:pointer;color:#d1d5db;user-select:none;transition:color .15s,transform .1s;-webkit-tap-highlight-color:transparent}
.star:active{transform:scale(1.25)}
.star.selected{color:#facc15}
/* Projet actif admin */
.actif-card{background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff;padding:22px;border-radius:12px;text-align:center;margin:10px 0}
.actif-card h3{font-size:1.6em;font-weight:700;color:#fff}
.actif-card p{color:#dcfce7;margin-top:6px}
/* Stats */
.stat-box{background:#f8fafc;padding:14px;border-radius:10px;margin:8px 0;text-align:center}
.stat-box .big{font-size:2.2em;font-weight:800;color:#3b82f6}
.stat-box .label{font-size:.82em;color:#888;margin-bottom:4px}
.repartition{display:flex;justify-content:center;gap:14px;flex-wrap:wrap;margin-top:10px}
.rep-item{text-align:center;font-size:.9em}
.rep-item .rep-star{font-size:1.2em;color:#facc15}
.rep-item .rep-count{font-weight:700;font-size:1.1em}
/* Liste projets */
.projet-item{padding:14px 16px;border:2px solid #e5e7eb;border-radius:10px;margin:8px 0;cursor:pointer;display:flex;justify-content:space-between;align-items:center;transition:border .2s,background .2s}
.projet-item:hover{border-color:#a5b4fc}
.projet-item.active{border-color:#22c55e;background:#f0fdf4}
.projet-item .nom{font-weight:600;font-size:.95em}
.projet-item .desc{font-size:.82em;color:#888;margin-top:2px}
/* QR + lien */
.qr-wrap{background:linear-gradient(135deg,#667eea,#764ba2);padding:22px;border-radius:14px;text-align:center;color:#fff}
.qr-wrap h2{color:#fff;margin-bottom:6px}
.qr-wrap p{color:#e0e7ff;font-size:.88em;margin-bottom:12px}
#qrcode{background:#fff;padding:10px;border-radius:10px;display:inline-flex;justify-content:center;margin:10px 0}
.url-box{background:rgba(255,255,255,.15);color:#fff;padding:10px 14px;border-radius:8px;word-break:break-all;font-family:monospace;font-size:.82em;margin:10px 0}
/* Votant */
.vote-header{background:linear-gradient(135deg,#667eea,#764ba2);padding:24px;border-radius:14px;text-align:center;color:#fff;margin-bottom:14px}
.vote-header h2{color:#fff;font-size:1.5em}
.vote-header p{color:#e0e7ff;margin-top:6px}
.attente{text-align:center;padding:60px 20px;color:#94a3b8}
.attente .icon{font-size:4em;margin-bottom:12px}
.message{padding:12px;border-radius:8px;text-align:center;font-weight:600;margin:10px 0}
.message.success{background:#dcfce7;color:#166534}
@media(max-width:600px){.star{font-size:2.7em}.container{padding:12px 10px}}
/* Onglets admin */
.tabs{display:flex;gap:6px;margin-bottom:16px}
.tab{flex:1;padding:9px;border:2px solid #e5e7eb;border-radius:10px;background:#fff;font-weight:600;font-size:.88em;cursor:pointer;text-align:center;transition:all .2s}
.tab.active{background:#667eea;color:#fff;border-color:#667eea}
.tab-content{display:none}
.tab-content.active{display:block}
</style>
</head>
<body>
<header>
  <h1>📊 Vote Projets Étudiants</h1>
  <p id="headerSub"></p>
</header>

<!-- ADMIN -->
<div id="adminPanel" style="display:none">
  <div class="container">

    <div class="qr-wrap">
      <h2>📱 QR Code Votants</h2>
      <p>Partagez ce lien — accessible depuis n'importe où</p>
      <div id="qrcode"></div>
      <div class="url-box" id="voterUrl"></div>
      <button class="btn btn-outline" style="background:#fff;border:none;color:#667eea;width:auto;padding:10px 22px" onclick="copierLien()">📋 Copier le lien</button>
    </div>

    <div class="tabs">
      <div class="tab active" onclick="showTab('tabVote')">🗳️ Vote en cours</div>
      <div class="tab" onclick="showTab('tabProjets')">📋 Projets</div>
      <div class="tab" onclick="showTab('tabAjouter')">➕ Ajouter</div>
    </div>

    <div id="tabVote" class="tab-content active">
      <div class="card">
        <h2>Projet soumis au vote</h2>
        <div id="projetActifInfo" style="text-align:center;padding:30px;color:#94a3b8">
          <div style="font-size:3em">⏳</div>
          <p style="margin-top:8px">Aucun projet sélectionné<br><small>Allez dans "Projets" pour en activer un</small></p>
        </div>
        <div id="projetActifCard" style="display:none"></div>
        <div id="statsBox" style="display:none">
          <div style="display:flex;gap:10px;margin-top:14px">
            <div class="stat-box" style="flex:1"><div class="label">Votes reçus</div><div class="big" id="statTotal">0</div></div>
            <div class="stat-box" style="flex:1"><div class="label">Note moyenne</div><div class="big" id="statMoyenne">-</div></div>
          </div>
          <div class="repartition" id="repartition"></div>
        </div>
      </div>
    </div>

    <div id="tabProjets" class="tab-content">
      <div class="card">
        <h2>Projets enregistrés</h2>
        <div id="listeProjets"></div>
        <button class="btn btn-red" style="margin-top:16px" onclick="resetVotes()">🗑️ Réinitialiser tous les votes</button>
      </div>
    </div>

    <div id="tabAjouter" class="tab-content">
      <div class="card">
        <h2>Nouveau projet</h2>
        <input type="text" id="inputNom" placeholder="Nom du projet (ex : Projet Alpha)">
        <textarea id="inputDesc" placeholder="Description (optionnelle)"></textarea>
        <button class="btn btn-blue" onclick="ajouterProjet()" style="margin-top:10px">➕ Ajouter</button>
      </div>
    </div>

  </div>
</div>

<!-- VOTANT -->
<div id="voterPanel" style="display:none">
  <div class="container">
    <div id="voterAttente" class="attente">
      <div class="icon">⏳</div>
      <h2>En attente...</h2>
      <p style="margin-top:8px;font-size:.9em">L'organisateur va lancer un vote</p>
    </div>
    <div id="voterVote" style="display:none">
      <div class="vote-header">
        <h2 id="voterProjetNom"></h2>
        <p id="voterProjetDesc"></p>
      </div>
      <div class="card" style="text-align:center">
        <p style="font-weight:600;font-size:1.05em;color:#555">Votre note</p>
        <div class="stars" id="starsContainer">
          <span class="star" data-value="1">★</span>
          <span class="star" data-value="2">★</span>
          <span class="star" data-value="3">★</span>
          <span class="star" data-value="4">★</span>
          <span class="star" data-value="5">★</span>
        </div>
        <button id="btnVote" class="btn btn-green" disabled onclick="envoyerVote()">Choisissez une note</button>
        <div id="voterMessage" class="message" style="display:none"></div>
      </div>
    </div>
  </div>
</div>

<script>
var votantId = 'v_' + Date.now() + '_' + Math.random().toString(36).substr(2,6);
var selectedNote = null, monVote = null, projets = [], projetActifId = null;
var urlParams = new URLSearchParams(window.location.search);
var modeVotant = urlParams.get('mode') === 'vote';
var isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent) || window.innerWidth < 768;

if (modeVotant || isMobile) {
  document.getElementById('voterPanel').style.display = 'block';
  document.getElementById('headerSub').textContent = 'Interface votant';
  initVotant();
} else {
  document.getElementById('adminPanel').style.display = 'block';
  document.getElementById('headerSub').textContent = 'Interface organisateur';
  initAdmin();
}

// --- TABS ---
function showTab(id) {
  document.querySelectorAll('.tab-content').forEach(function(el){ el.classList.remove('active'); });
  document.querySelectorAll('.tab').forEach(function(el){ el.classList.remove('active'); });
  document.getElementById(id).classList.add('active');
  event.target.classList.add('active');
}

// --- ADMIN ---
function initAdmin() {
  var voterUrl = window.location.origin + window.location.pathname + '?mode=vote';
  document.getElementById('voterUrl').textContent = voterUrl;
  if (typeof QRCode !== 'undefined') {
    new QRCode(document.getElementById('qrcode'), { text: voterUrl, width: 180, height: 180 });
  }
  chargerProjets();
  chargerActif();
  setInterval(function(){ chargerActif(); rafraichirStats(); }, 3000);
}

function chargerProjets() {
  fetch('/projets').then(function(r){ return r.json(); }).then(function(data){ projets = data; afficherProjets(); });
}

function chargerActif() {
  fetch('/actif').then(function(r){ return r.json(); }).then(function(data){
    var newId = data ? data.id : null;
    if (newId !== projetActifId) { projetActifId = newId; mettreAJourProjetActif(); }
  });
}

function afficherProjets() {
  var c = document.getElementById('listeProjets');
  if (!projets || projets.length === 0) {
    c.innerHTML = '<p style="text-align:center;color:#94a3b8;padding:20px">Aucun projet — ajoutez-en un via l\'onglet ➕</p>';
    return;
  }
  c.innerHTML = projets.map(function(p) {
    var isActif = p.id === projetActifId;
    return '<div class="projet-item' + (isActif ? ' active' : '') + '" onclick="selectionnerProjet(\'' + p.id + '\')">'
      + '<div><div class="nom">' + (isActif ? '🟢 ' : '') + p.nom + '</div>'
      + (p.description ? '<div class="desc">' + p.description + '</div>' : '') + '</div>'
      + '<button class="btn btn-red btn-small" onclick="event.stopPropagation();supprimerProjet(\'' + p.id + '\')">✕</button>'
      + '</div>';
  }).join('');
}

function ajouterProjet() {
  var n = document.getElementById('inputNom').value.trim();
  if (!n) return alert('Le nom est requis');
  fetch('/projets', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ nom: n, description: document.getElementById('inputDesc').value.trim() }) })
    .then(function(r){ return r.json(); })
    .then(function(data){ projets = data; document.getElementById('inputNom').value = ''; document.getElementById('inputDesc').value = ''; afficherProjets(); });
}

function selectionnerProjet(id) {
  fetch('/actif', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ id: id }) })
    .then(function(){ projetActifId = id; mettreAJourProjetActif(); afficherProjets(); });
}

function supprimerProjet(id) {
  if (!confirm('Supprimer ce projet ?')) return;
  fetch('/projets/' + id, { method: 'DELETE' }).then(function(r){ return r.json(); }).then(function(data){
    projets = data;
    if (projetActifId === id) { projetActifId = null; }
    mettreAJourProjetActif(); afficherProjets();
  });
}

function mettreAJourProjetActif() {
  var info = document.getElementById('projetActifInfo');
  var card = document.getElementById('projetActifCard');
  var stats = document.getElementById('statsBox');
  if (!projetActifId) { info.style.display='block'; card.style.display='none'; stats.style.display='none'; return; }
  var p = projets.find(function(x){ return x.id === projetActifId; });
  if (!p) { projetActifId = null; mettreAJourProjetActif(); return; }
  info.style.display = 'none';
  card.style.display = 'block';
  stats.style.display = 'block';
  card.innerHTML = '<div class="actif-card"><h3>' + p.nom + '</h3>' + (p.description ? '<p>' + p.description + '</p>' : '') + '</div>';
  rafraichirStats();
}

function rafraichirStats() {
  if (!projetActifId) return;
  fetch('/votes/' + projetActifId).then(function(r){ return r.json(); }).then(function(data){
    document.getElementById('statTotal').textContent = data.total || 0;
    document.getElementById('statMoyenne').textContent = data.moyenne || '-';
    var rep = '';
    [5,4,3,2,1].forEach(function(n){
      rep += '<div class="rep-item"><div class="rep-star">★' + n + '</div><div class="rep-count">' + (data.repartition[n] || 0) + '</div></div>';
    });
    document.getElementById('repartition').innerHTML = rep;
  });
}

function resetVotes() {
  if (!confirm('Réinitialiser TOUS les votes ?')) return;
  fetch('/reset', { method: 'POST' }).then(function(r){ return r.json(); }).then(function(data){
    projets = data.projets; projetActifId = null; afficherProjets(); mettreAJourProjetActif();
  });
}

function copierLien() {
  var u = document.getElementById('voterUrl').textContent;
  navigator.clipboard.writeText(u).then(function(){ alert('Lien copié !'); });
}

// --- VOTANT ---
function initVotant() {
  document.querySelectorAll('.star').forEach(function(s){
    s.addEventListener('click', function(){
      if (monVote !== null) return;
      selectedNote = parseInt(this.dataset.value);
      mettreAJourEtoiles(selectedNote);
      var btn = document.getElementById('btnVote');
      btn.disabled = false;
      btn.textContent = 'Envoyer : ' + selectedNote + ' ★';
    });
  });
  verifierProjetActif();
  setInterval(verifierProjetActif, 3000);
}

function mettreAJourEtoiles(note) {
  document.querySelectorAll('.star').forEach(function(s){
    s.classList.toggle('selected', parseInt(s.dataset.value) <= note);
  });
}

function verifierProjetActif() {
  fetch('/actif').then(function(r){ return r.json(); }).then(function(projet){
    if (!projet || !projet.id) {
      document.getElementById('voterAttente').style.display = 'block';
      document.getElementById('voterVote').style.display = 'none';
      monVote = null; return;
    }
    document.getElementById('voterAttente').style.display = 'none';
    document.getElementById('voterVote').style.display = 'block';
    document.getElementById('voterProjetNom').textContent = projet.nom;
    document.getElementById('voterProjetDesc').textContent = projet.description || '';
    fetch('/votes/' + projet.id + '?votant=' + votantId).then(function(r){ return r.json(); }).then(function(data){
      monVote = (data.vote !== null && data.vote !== undefined) ? data.vote : null;
      if (monVote !== null) {
        mettreAJourEtoiles(monVote);
        var btn = document.getElementById('btnVote');
        btn.disabled = true;
        btn.textContent = '✅ Voté : ' + monVote + ' ★';
        var msg = document.getElementById('voterMessage');
        msg.style.display = 'block';
        msg.className = 'message success';
        msg.textContent = 'Merci pour votre vote !';
      } else {
        selectedNote = null;
        mettreAJourEtoiles(0);
        var btn = document.getElementById('btnVote');
        btn.disabled = true;
        btn.textContent = 'Choisissez une note';
        document.getElementById('voterMessage').style.display = 'none';
      }
    });
  });
}

function envoyerVote() {
  if (!selectedNote || monVote !== null) return;
  fetch('/actif').then(function(r){ return r.json(); }).then(function(projet){
    if (!projet || !projet.id) return;
    fetch('/votes/' + projet.id, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ votant: votantId, note: selectedNote }) })
      .then(function(){
        monVote = selectedNote;
        var btn = document.getElementById('btnVote');
        btn.disabled = true;
        btn.textContent = '✅ Voté : ' + selectedNote + ' ★';
        var msg = document.getElementById('voterMessage');
        msg.style.display = 'block';
        msg.className = 'message success';
        msg.textContent = 'Merci pour votre vote !';
      });
  });
}
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
def index():
    return HTML
