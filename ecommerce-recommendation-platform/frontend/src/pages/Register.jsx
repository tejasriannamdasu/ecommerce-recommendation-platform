import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../api/AuthContext.jsx'

export default function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', username: '', password: '' })
  const [error, setError] = useState('')

  const onSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await register(form.email, form.username, form.password)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed.')
    }
  }

  return (
    <div className="max-w-sm mx-auto pt-20">
      <h1 className="font-display text-3xl text-mist-100 mb-6">Create your account</h1>
      <form onSubmit={onSubmit} className="flex flex-col gap-4">
        <input placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })}
          className="rounded-lg bg-ink-800 border border-ink-700 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-signal-500" required />
        <input placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })}
          className="rounded-lg bg-ink-800 border border-ink-700 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-signal-500" required />
        <input type="password" placeholder="Password (min 8 chars)" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })}
          className="rounded-lg bg-ink-800 border border-ink-700 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-signal-500" required />
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button type="submit" className="rounded-full bg-signal-500 text-ink-950 font-medium px-6 py-2 hover:bg-signal-400">
          Sign up
        </button>
      </form>
      <p className="text-mist-500 text-sm mt-4">
        Already have an account? <Link to="/login" className="text-signal-400">Log in</Link>
      </p>
    </div>
  )
}
