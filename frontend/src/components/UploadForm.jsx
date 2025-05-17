import React, { useState, useRef } from 'react'
import { uploadZip } from '../api'

export default function UploadForm({ onComplete }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const fileInputRef = useRef()
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
  const handleFileChange = (e) => {
    const selected = e.target.files[0]
    if (selected && !selected.name.toLowerCase().endsWith('.zip')) {
      setError('Only .zip archives are allowed.')
      setFile(null)
      e.target.value = ''
      return
    }
    setError('')
    setFile(selected)
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
      <div style={{display:'flex', alignItems:'center', gap:'1rem', margin:'1.2rem 0'}}>
        <input
          id="strava-zip"
          ref={fileInputRef}
          type="file"
          accept=".zip"
          onChange={handleFileChange}
          aria-required="true"
          style={{display:'none'}}
        />
        <button
          type="button"
          className="button"
          style={{padding:'0.6rem 1.2rem', fontSize:'1rem', background:'var(--color-btn-bg)', color:'var(--color-primary)', border:'1.5px solid var(--color-btn-border)'}}
          onClick={() => fileInputRef.current && fileInputRef.current.click()}
          tabIndex={0}
        >
          <span style={{display:'inline-flex', alignItems:'center', gap:'0.5rem'}}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 16V4"/><path d="M8 8l4-4 4 4"/><rect x="4" y="16" width="16" height="4" rx="2"/></svg>
            {file ? 'Change file' : 'Choose file'}
          </span>
        </button>
        <span style={{fontSize:'1rem', color:file ? 'var(--color-success)' : 'var(--color-muted)', minWidth:0, wordBreak:'break-all'}}>
          {file ? file.name : 'No file selected'}
        </span>
      </div>
      {error && <div style={{color:'var(--color-accent)', fontWeight:500, marginBottom:'0.5rem'}}>{error}</div>}
      <div style={{fontSize:'0.95rem', color:'var(--color-muted)', marginBottom:'1rem'}}>Download your Strava data export as a .zip file and upload it here for instant analysis.</div>
      <button className="button" type="submit" disabled={loading || !file} aria-busy={loading} aria-live="polite">
        {loading ? <span style={{display:'inline-flex',alignItems:'center'}}><span className="spinner" style={{marginRight:8, width:18, height:18, border:'3px solid #fff', borderTop:'3px solid var(--color-primary)', borderRadius:'50%', display:'inline-block', animation:'spin 1s linear infinite'}}></span>Processing...</span> : 'Upload & Analyze'}
      </button>
      <style>{`@keyframes spin { 0% { transform: rotate(0deg);} 100% { transform: rotate(360deg);} } @keyframes fadein { from { opacity: 0; transform: translateY(24px);} to { opacity: 1; transform: none;} }`}</style>
    </form>
  )
}
