import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../api/AuthContext.jsx'

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const onSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await login(email, password)
      navigate('/')
    } catch {
      setError('Incorrect email or password.')
    }
  }

  return (
    <div className="max-w-sm mx-auto pt-20">
      <h1 className="font-display text-3xl text-mist-100 mb-6">Log in</h1>
      <form onSubmit={onSubmit} className="flex flex-col gap-4">
        <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)}
          className="rounded-lg bg-ink-800 border border-ink-700 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-signal-500" required />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)}
          className="rounded-lg bg-ink-800 border border-ink-700 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-signal-500" required />
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button type="submit" className="rounded-full bg-signal-500 text-ink-950 font-medium px-6 py-2 hover:bg-signal-400">
          Log in
        </button>
      </form>
      <p className="text-mist-500 text-sm mt-4">
        No account? <Link to="/register" className="text-signal-400">Sign up</Link>
      </p>
      <p className="text-mist-500 text-xs mt-6">Demo: admin@example.com / Admin@123 or user1@example.com / Password@123</p>
    </div>
  )
}
