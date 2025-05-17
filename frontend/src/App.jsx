import React, { useState } from 'react'
import UploadForm from './components/UploadForm.jsx'
import Results from './components/Results.jsx'

function App() {
  const [summary, setSummary] = useState(null)
  return (
    <div style={{minHeight:'100vh', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'flex-start', background:'none'}}>
      <header style={{width:'100%', padding:'2rem 0 1rem 0', textAlign:'center'}}>
        <span style={{fontWeight:700, fontSize:'2.2rem', color:'#6366f1', letterSpacing:'-1px', fontFamily:'Inter, Segoe UI, sans-serif'}}>Marathon Training Analyzer <span role="img" aria-label="runner">🏃‍♂️</span></span>
        <div style={{color:'#64748b', fontSize:'1.1rem', marginTop:'0.5rem'}}>Upload your Strava export for instant marathon training insights</div>
      </header>
      <UploadForm onComplete={(d)=>setSummary(d.summary)}/>
      <Results summary={summary}/>
    </div>
  )
}

export default App
