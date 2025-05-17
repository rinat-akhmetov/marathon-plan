import React from 'react'

export default function Results({ summary }) {
  if (!summary) return null
  return (
    <div className="container" style={{marginTop:'2rem', boxShadow:'0 4px 24px rgba(99,102,241,0.10)', animation:'fadein 0.7s cubic-bezier(.4,0,.2,1)'}}>
      <h2 style={{color:'var(--color-success)', fontWeight:700, fontSize:'1.5rem', marginBottom:'1rem', display:'flex', alignItems:'center', gap:'0.5rem'}}>
        <span>Analysis Summary</span>
        <span style={{display:'inline-flex',verticalAlign:'middle'}}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="12" width="3.5" height="8" rx="1.5"/><rect x="9.25" y="8" width="3.5" height="12" rx="1.5"/><rect x="15.5" y="4" width="3.5" height="16" rx="1.5"/></svg>
        </span>
      </h2>
      <pre style={{background:'var(--color-pre-bg)', color:'var(--color-pre-text)', border:'1px solid var(--color-pre-border)', fontSize:'1.05rem', padding:'1.2rem', borderRadius:'10px'}}>{JSON.stringify(summary, null, 2)}</pre>
      <style>{`@keyframes fadein { from { opacity: 0; transform: translateY(24px);} to { opacity: 1; transform: none;} }`}</style>
    </div>
  )
}
