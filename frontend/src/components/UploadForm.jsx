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
    <form onSubmit={handleSubmit} className="container" aria-label="Upload Strava ZIP" style={{animation:'fadein 0.7s cubic-bezier(.4,0,.2,1)'}}>
      <h2 style={{display:'flex', alignItems:'center', gap:'0.5rem'}}>
        <span>Upload Strava Export</span>
        <span style={{display:'inline-flex',verticalAlign:'middle'}}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="14" rx="3"/><path d="M8 21h8"/><path d="M12 17v4"/></svg>
        </span>
      </h2>
      <label htmlFor="strava-zip" style={{fontWeight:600, color:'var(--color-primary)', fontSize:'1.1rem'}}>Select your Strava ZIP file</label>
      <input id="strava-zip" type="file" accept=".zip" onChange={(e)=>setFile(e.target.files[0])} aria-required="true"/>
      <div style={{fontSize:'0.95rem', color:'var(--color-muted)', marginBottom:'1rem'}}>Download your Strava data export as a .zip file and upload it here for instant analysis.</div>
      <button className="button" type="submit" disabled={loading || !file} aria-busy={loading} aria-live="polite">
        {loading ? <span style={{display:'inline-flex',alignItems:'center'}}><span className="spinner" style={{marginRight:8, width:18, height:18, border:'3px solid #fff', borderTop:'3px solid var(--color-primary)', borderRadius:'50%', display:'inline-block', animation:'spin 1s linear infinite'}}></span>Processing...</span> : 'Upload & Analyze'}
      </button>
      <style>{`@keyframes spin { 0% { transform: rotate(0deg);} 100% { transform: rotate(360deg);} } @keyframes fadein { from { opacity: 0; transform: translateY(24px);} to { opacity: 1; transform: none;} }`}</style>
    </form>
  )
}
