import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

function App() {
  const [form, setForm] = useState({
    home_price: 500000,
    down_payment: 100000,
    annual_interest_rate: 6.5,
    term_years: 30,
    monthly_income: 12000
  })
  const [result, setResult] = useState(null)
  const [quotes, setQuotes] = useState([])

  const fetchQuotes = async () => {
    const res = await fetch(`${API_BASE}/api/mortgage/quotes`)
    setQuotes(await res.json())
  }

  useEffect(() => {
    fetchQuotes().catch(console.error)
  }, [])

  const onSubmit = async (e) => {
    e.preventDefault()
    const res = await fetch(`${API_BASE}/api/mortgage/quote`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(Object.fromEntries(Object.entries(form).map(([k, v]) => [k, Number(v)])))
    })
    const data = await res.json()
    setResult(data)
    fetchQuotes().catch(console.error)
  }

  return (
    <main style={{maxWidth: 900, margin: '40px auto', fontFamily: 'Arial'}}>
      <h1>Mortgage Quote Portal (Azure Ready)</h1>
      <form onSubmit={onSubmit} style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12}}>
        {Object.entries(form).map(([key, value]) => (
          <label key={key}>
            {key.replaceAll('_', ' ')}
            <input
              type="number"
              value={value}
              step="any"
              onChange={(e) => setForm({...form, [key]: e.target.value})}
              style={{display: 'block', width: '100%'}}
            />
          </label>
        ))}
        <button type="submit" style={{gridColumn: '1 / -1'}}>Calculate & Save Quote</button>
      </form>
      {result && (
        <section>
          <h2>Latest Quote</h2>
          <p>Monthly Payment: ${result.monthly_payment}</p>
          <p>Debt-To-Income: {result.debt_to_income}%</p>
        </section>
      )}
      <section>
        <h2>Saved Quotes</h2>
        <ul>
          {quotes.map((q) => (
            <li key={q.id}>#{q.id} - ${q.monthly_payment} ({q.debt_to_income}% DTI)</li>
          ))}
        </ul>
      </section>
    </main>
  )
}

createRoot(document.getElementById('root')).render(<App />)
