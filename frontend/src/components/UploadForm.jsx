
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
    <form onSubmit={handleSubmit} className="container">
      <h2>Upload Strava Export (.zip)</h2>
      <input type="file" accept=".zip" onChange={(e)=>setFile(e.target.files[0])}/>
      <button className="button" type="submit" disabled={loading}>
        {loading ? 'Processing...' : 'Upload & Analyze'}
      </button>
    </form>
  )
}
