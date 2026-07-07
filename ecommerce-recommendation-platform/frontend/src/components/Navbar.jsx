import { Link, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useAuth } from '../api/AuthContext.jsx'

export default function Navbar() {
  const { user, logout } = useAuth()
  const [query, setQuery] = useState('')
  const navigate = useNavigate()

  const onSearch = (e) => {
    e.preventDefault()
    if (query.trim()) navigate(`/search?q=${encodeURIComponent(query)}`)
  }

  return (
    <header className="sticky top-0 z-20 border-b border-ink-700 bg-ink-950/90 backdrop-blur">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center gap-6">
        <Link to="/" className="font-display text-xl tracking-tight text-mist-100">
          Signal<span className="text-signal-500">.</span>
        </Link>

        <form onSubmit={onSearch} className="flex-1 max-w-xl">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search — try 'wireless headphones for gaming'"
            className="w-full rounded-full bg-ink-800 border border-ink-700 px-4 py-2 text-sm placeholder:text-mist-500 focus:outline-none focus:ring-2 focus:ring-signal-500"
          />
        </form>

        <nav className="flex items-center gap-4 text-sm">
          {user ? (
            <>
              <Link to="/wishlist" className="text-mist-300 hover:text-signal-400">Wishlist</Link>
              <Link to="/profile" className="text-mist-300 hover:text-signal-400">{user.username}</Link>
              {user.role === 'admin' && (
                <Link to="/admin" className="text-mist-300 hover:text-signal-400">Dashboard</Link>
              )}
              <button onClick={logout} className="text-mist-500 hover:text-signal-400">Log out</button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-mist-300 hover:text-signal-400">Log in</Link>
              <Link
                to="/register"
                className="rounded-full bg-signal-500 text-ink-950 font-medium px-4 py-1.5 hover:bg-signal-400"
              >
                Sign up
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}
