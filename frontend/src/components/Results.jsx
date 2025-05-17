
import React from 'react'

export default function Results({ summary }) {
  if (!summary) return null
  return (
    <div className="container">
      <h2>Analysis Summary</h2>
      <pre>{JSON.stringify(summary, null, 2)}</pre>
    </div>
  )
}
