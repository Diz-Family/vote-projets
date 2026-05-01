'use client'
import { useState, useEffect, useRef } from 'react'

export default function Home() {
  const [mode, setMode] = useState(null)
  const [projets, setProjets] = useState([])
  const [projetActif, setProjetActif] = useState(null)
  const [nouveauNom, setNouveauNom] = useState('')
  const [nouvelleDesc, setNouvelleDesc] = useState('')
  const [stats, setStats] = useState({total:0, moyenne:0, repartition:{}})
  const [selectedNote, setSelectedNote] = useState(null)
  const [voted, setVoted] = useState(false)
  const [message, setMessage] = useState('')
  const [voterId] = useState('v_' + Math.random().toString(36).substr(2,9))
  const pollingRef = useRef(null)

  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const isMobile = /Android|iPhone|iPad|iPod/i.test(navigator.userAgent) || window.innerWidth < 768
    if (urlParams.get('mode') === 'vote' || isMobile) {
      setMode('voter')
    } else {
      setMode('admin')
    }
  }, [])

  useEffect(() => {
    if (mode === 'admin') {
      chargerProjets()
      pollingRef.current = setInterval(() => { chargerProjetActif(); if (projetActif) chargerStats() }, 2000)
    }
    if (mode === 'voter') {
      pollingRef.current = setInterval(() => { chargerProjetActif() }, 2000)
    }
    return () => { if (pollingRef.current) clearInterval(pollingRef.current) }
  }, [mode, projetActif])

  const chargerProjets = async () => {
    const res = await fetch('/api/projets')
    setProjets(await res.json())
  }
  const chargerProjetActif = async () => {
    const res = await fetch('/api/actif')
    const data = await res.json()
    setProjetActif(data)
    if (mode === 'voter' && data) {
      const v = await fetch('/api/vote-check?projet=' + data.id + '&voter=' + voterId)
      const vd = await v.json()
      if (vd.voted) { setVoted(true); setSelectedNote(vd.note) }
      else { setVoted(false); setSelectedNote(null) }
    }
  }
  const chargerStats = async () => {
    if (!projetActif) return
    const res = await fetch('/api/stats?projet=' + projetActif.id)
    setStats(await res.json())
  }

  if (mode === 'voter') {
    return (
      <div>
        <div style={{background:'linear-gradient(135deg,#6C5CE7,#A29BFE)',color:'#fff',padding:'16px',textAlign:'center',fontSize:'1.3em',fontWeight:'bold'}}>📱 Vote Étudiant</div>
        <div style={{maxWidth:'500px',margin:'0 auto',padding:'16px'}}>
          {!projetActif ? (
            <div style={{background:'#fff',padding:'40px',borderRadius:'16px',textAlign:'center'}}>
              <div style={{fontSize:'4em'}}>⏳</div>
              <h2>En attente...</h2>
              <p style={{color:'#999'}}>L'organisateur va lancer un vote</p>
            </div>
          ) : (
            <div>
              <div style={{background:'#00B894',color:'#fff',padding:'24px',borderRadius:'16px',textAlign:'center',marginBottom:'16px'}}>
                <h2 style={{margin:0}}>{projetActif.nom}</h2>
                {projetActif.description && <p>{projetActif.description}</p>}
              </div>
              <div style={{background:'#fff',padding:'20px',borderRadius:'16px',textAlign:'center'}}>
                <p style={{fontWeight:'bold',fontSize:'1.1em'}}>Votre note :</p>
                <div style={{display:'flex',justifyContent:'center',gap:'12px',margin:'20px 0'}}>
                  {[5,4,3,2,1].map(n => (
                    <span key={n} onClick={() => !voted && setSelectedNote(n)} style={{fontSize:'2.8em',cursor:voted?'default':'pointer',color:selectedNote&&n<=selectedNote?'#FFD700':'#ddd',userSelect:'none'}}>★</span>
                  ))}
                </div>
                <button onClick={async () => {
                  if (!projetActif || !selectedNote || voted) return
                  await fetch('/api/vote', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({projet:projetActif.id,voter:voterId,note:selectedNote})})
                  setVoted(true)
                  setMessage('✅ Vote enregistré !')
                  setTimeout(() => setMessage(''), 3000)
                }} style={{width:'100%',padding:'14px',border:'none',borderRadius:'12px',fontSize:'1.1em',fontWeight:'bold',background:voted||!selectedNote?'#ccc':'#00B894',color:'#fff',cursor:voted||!selectedNote?'not-allowed':'pointer'}} disabled={!selectedNote||voted}>
                  {voted ? `✅ Déjà voté : ${selectedNote}⭐` : selectedNote ? `Voter ${selectedNote}⭐` : 'Choisissez une note'}
                </button>
                {message && <p style={{color:'#00B894',fontWeight:'bold',marginTop:'10px'}}>{message}</p>}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div>
      <div style={{background:'linear-gradient(135deg,#6C5CE7,#A29BFE)',color:'#fff',padding:'16px',textAlign:'center',fontSize:'1.3em',fontWeight:'bold'}}>📊 Vote Projets - Admin</div>
      <div style={{maxWidth:'700px',margin:'0 auto',padding:'16px'}}>
        <div style={{background:'linear-gradient(135deg,#6C5CE7,#A29BFE)',color:'#fff',padding:'20px',borderRadius:'16px',textAlign:'center',marginBottom:'16px'}}>
          <h2 style={{margin:0}}>📱 Scannez pour voter</h2>
          <div style={{display:'flex',justifyContent:'center',padding:'16px'}}><QrCode url={typeof window!=='undefined'?window.location.origin+'/?mode=vote':''}/></div>
        </div>
        <div style={{background:'#fff',padding:'20px',borderRadius:'16px',marginBottom:'16px'}}>
          <h2>📌 Projet en cours</h2>
          {projetActif ? (
            <div>
              <div style={{background:'#00B894',color:'#fff',padding:'20px',borderRadius:'12px',textAlign:'center'}}>
                <h2 style={{margin:0}}>{projetActif.nom}</h2>
                {projetActif.description && <p>{projetActif.description}</p>}
              </div>
              <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:'12px',marginTop:'12px'}}>
                <div style={{background:'#f5f5f5',padding:'16px',borderRadius:'12px',textAlign:'center'}}><div>Votes</div><div style={{fontSize:'2em',fontWeight:'bold',color:'#6C5CE7'}}>{stats.total}</div></div>
                <div style={{background:'#f5f5f5',padding:'16px',borderRadius:'12px',textAlign:'center'}}><div>Moyenne</div><div style={{fontSize:'2em',fontWeight:'bold',color:'#6C5CE7'}}>{stats.moyenne||'-'}</div></div>
              </div>
              <div style={{textAlign:'center',marginTop:'12px'}}>
                {[5,4,3,2,1].map(n => <span key={n} style={{margin:'0 8px'}}>⭐{n}: <b>{stats.repartition?.[n]||0}</b></span>)}
              </div>
            </div>
          ) : <p style={{textAlign:'center',color:'#999',padding:'30px'}}>⏳ Aucun projet sélectionné</p>}
        </div>
        <div style={{background:'#fff',padding:'20px',borderRadius:'16px',marginBottom:'16px'}}>
          <h2>➕ Ajouter un projet</h2>
          <input id="nomProjet" placeholder="Nom du projet" style={{width:'100%',padding:'12px',border:'2px solid #ddd',borderRadius:'10px',fontSize:'1em',marginBottom:'8px',boxSizing:'border-box'}} />
          <input id="descProjet" placeholder="Description (optionnelle)" style={{width:'100%',padding:'12px',border:'2px solid #ddd',borderRadius:'10px',fontSize:'1em',marginBottom:'8px',boxSizing:'border-box'}} />
          <button onClick={async () => {
            const n=document.getElementById('nomProjet').value.trim()
            if(!n) return alert('Nom requis')
            await fetch('/api/projets',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({nom:n,description:document.getElementById('descProjet').value.trim()})})
            document.getElementById('nomProjet').value=''
            document.getElementById('descProjet').value=''
            chargerProjets()
          }} style={{width:'100%',padding:'14px',background:'#6C5CE7',color:'#fff',border:'none',borderRadius:'12px',fontSize:'1em',fontWeight:'bold',cursor:'pointer'}}>➕ Ajouter</button>
        </div>
        <div style={{background:'#fff',padding:'20px',borderRadius:'16px',marginBottom:'16px'}}>
          <h2>📋 Projets ({projets.length}/50)</h2>
          {projets.map(p => (
            <div key={p.id} onClick={() => definirActif(p.id)} style={{padding:'14px',border:'2px solid '+(projetActif?.id===p.id?'#00B894':'#ddd'),borderRadius:'12px',marginBottom:'8px',cursor:'pointer',display:'flex',justifyContent:'space-between',alignItems:'center',background:projetActif?.id===p.id?'#e6fff5':'#fff'}}>
              <div><strong>{p.nom}</strong>{p.description&&<div><small style={{color:'#666'}}>{p.description}</small></div>}</div>
              <span onClick={(e) => {e.stopPropagation();supprimerProjet(p.id)}} style={{cursor:'pointer',fontSize:'1.5em',color:'#FF6B6B'}}>×</span>
            </div>
          ))}
          {projets.length===0 && <p style={{textAlign:'center',color:'#999'}}>Aucun projet</p>}
        </div>
        <button onClick={async () => {if(confirm('Réinitialiser TOUS les votes ?')){await fetch('/api/reset',{method:'POST'});chargerProjets();setProjetActif(null);setStats({total:0,moyenne:0,repartition:{}})}}} style={{width:'100%',padding:'14px',background:'#FF6B6B',color:'#fff',border:'none',borderRadius:'12px',fontSize:'1em',fontWeight:'bold',cursor:'pointer'}}>🗑️ Réinitialiser tous les votes</button>
      </div>
    </div>
  )

  async function definirActif(id) {
    await fetch('/api/actif',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id})})
    chargerProjetActif()
    chargerProjets()
  }
  async function supprimerProjet(id) {
    if(!confirm('Supprimer ?')) return
    await fetch('/api/projets/'+id,{method:'DELETE'})
    chargerProjets()
    chargerProjetActif()
  }
}

function QrCode({ url }) {
  const ref = useRef(null)
  useEffect(() => {
    if (ref.current && url) {
      const script = document.createElement('script')
      script.src = 'https://cdn.jsdelivr.net/npm/qrcodejs@1.0.0/qrcode.min.js'
      script.onload = () => { ref.current.innerHTML = ''; new QRCode(ref.current, { text: url, width: 180, height: 180 }) }
      document.head.appendChild(script)
    }
  }, [url])
  return <div ref={ref} style={{background:'#fff',padding:'10px',borderRadius:'8px',display:'inline-block'}}></div>
}
