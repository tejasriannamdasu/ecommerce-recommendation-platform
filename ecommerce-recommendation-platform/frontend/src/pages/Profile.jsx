import { useAuth } from '../api/AuthContext.jsx'

export default function Profile() {
  const { user } = useAuth()
  if (!user) return <div className="pt-16 text-mist-500">Please log in.</div>
  return (
    <div className="pt-16 max-w-md">
      <h1 className="font-display text-3xl text-mist-100 mb-6">Your profile</h1>
      <div className="rounded-xl2 bg-ink-800 border border-ink-700 p-6 flex flex-col gap-2">
        <p><span className="text-mist-500">Username:</span> {user.username}</p>
        <p><span className="text-mist-500">Email:</span> {user.email}</p>
        <p><span className="text-mist-500">Role:</span> {user.role}</p>
      </div>
    </div>
  )
}
