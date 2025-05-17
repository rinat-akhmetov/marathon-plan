import React, { useState } from 'react'
import { uploadZip } from '../api'

export default function UploadForm({ onComplete }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return
    setLoading(true)
    try {
      const data = await uploadZip(file)
      onComplete(data)
    } catch (err) {
      alert(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }
  return (
    <form onSubmit={handleSubmit} className="container" aria-label="Upload Strava ZIP">
      <h2>Upload Strava Export <span role="img" aria-label="zip">📦</span></h2>
      <label htmlFor="strava-zip" style={{fontWeight:600, color:'#6366f1', fontSize:'1.1rem'}}>Select your Strava ZIP file</label>
      <input id="strava-zip" type="file" accept=".zip" onChange={(e)=>setFile(e.target.files[0])} aria-required="true"/>
      <div style={{fontSize:'0.95rem', color:'#64748b', marginBottom:'1rem'}}>Download your Strava data export as a .zip file and upload it here for instant analysis.</div>
      <button className="button" type="submit" disabled={loading} aria-busy={loading} aria-live="polite">
        {loading ? <span style={{display:'inline-flex',alignItems:'center'}}><span className="spinner" style={{marginRight:8, width:18, height:18, border:'3px solid #fff', borderTop:'3px solid #6366f1', borderRadius:'50%', display:'inline-block', animation:'spin 1s linear infinite'}}></span>Processing...</span> : 'Upload & Analyze'}
      </button>
      <style>{`@keyframes spin { 0% { transform: rotate(0deg);} 100% { transform: rotate(360deg);} }`}</style>
    </form>
  )
}
