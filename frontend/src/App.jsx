
import React, { useState } from 'react'
import UploadForm from './components/UploadForm.jsx'
import Results from './components/Results.jsx'

function App() {
  const [summary, setSummary] = useState(null)
  return (
    <>
      <UploadForm onComplete={(d)=>setSummary(d.summary)}/>
      <Results summary={summary}/>
    </>
  )
}

export default App
