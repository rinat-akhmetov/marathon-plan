import React from 'react'

export default function Results({ summary }) {
  if (!summary) return null
  return (
    <div className="container" style={{marginTop:'2rem', boxShadow:'0 4px 24px rgba(99,102,241,0.10)'}}>
      <h2 style={{color:'#16a34a', fontWeight:700, fontSize:'1.5rem', marginBottom:'1rem'}}>Analysis Summary <span role="img" aria-label="chart">📊</span></h2>
      <pre style={{background:'#f0fdf4', color:'#166534', border:'1px solid #bbf7d0', fontSize:'1.05rem', padding:'1.2rem', borderRadius:'10px'}}>{JSON.stringify(summary, null, 2)}</pre>
    </div>
  )
}
