import React, { useState } from 'react'
import UploadForm from './components/UploadForm.jsx'
import Results from './components/Results.jsx'

function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme)
}

function App() {
  const [summary, setSummary] = useState(null)
  const [dark, setDark] = useState(false)
  const handleToggle = () => {
    setDark((d) => {
      setTheme(!d ? 'dark' : '');
      return !d
    })
  }
  return (
    <div style={{minHeight:'100vh', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'flex-start', background:'none'}}>
      <header style={{width:'100%', padding:'2rem 0 1rem 0', textAlign:'center', position:'relative'}}>
        <span style={{fontWeight:700, fontSize:'2.2rem', color:'var(--color-primary)', letterSpacing:'-1px', fontFamily:'Inter, Segoe UI, sans-serif'}}>Marathon Training Analyzer <span style={{verticalAlign:'middle'}}><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 17l6-6 4 4 6-6"/><circle cx="7" cy="17" r="1.5"/><circle cx="14" cy="11" r="1.5"/><circle cx="20" cy="7" r="1.5"/></svg></span></span>
        <div style={{color:'var(--color-muted)', fontSize:'1.1rem', marginTop:'0.5rem'}}>Upload your Strava export for instant marathon training insights</div>
        <button aria-label="Toggle dark mode" onClick={handleToggle} style={{position:'absolute', top:24, right:32, background:'none', border:'none', cursor:'pointer', padding:0}}>
          {dark ? (
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2m0 18v2m11-11h-2M3 12H1m16.95 7.07l-1.41-1.41M6.34 6.34L4.93 4.93m12.02 0l-1.41 1.41M6.34 17.66l-1.41 1.41"/></svg>
          ) : (
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#6366f1" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1111.21 3a7 7 0 109.79 9.79z"/></svg>
          )}
        </button>
      </header>
      <UploadForm onComplete={(d)=>setSummary(d.summary)}/>
      <Results summary={summary}/>
    </div>
  )
}

export default App
