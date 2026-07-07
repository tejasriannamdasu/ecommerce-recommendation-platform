import { useEffect, useState } from 'react'
import client from '../api/client.js'
import { useAuth } from '../api/AuthContext.jsx'

export default function AdminDashboard() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (user?.role !== 'admin') return
    client.get('/analytics/dashboard')
      .then((res) => setData(res.data))
      .catch(() => setError('Failed to load analytics.'))
  }, [user])

  if (user?.role !== 'admin') {
    return <div className="pt-16 text-mist-500">Admin access required.</div>
  }
  if (error) return <div className="pt-16 text-red-400">{error}</div>
  if (!data) return <div className="pt-16 text-mist-500">Loading analytics…</div>

  return (
    <div className="pt-16">
      <h1 className="font-display text-3xl text-mist-100 mb-6">Analytics dashboard</h1>

      <div className="grid grid-cols-3 gap-4 mb-10">
        <Stat label="Active users" value={data.user_activity.active_users} />
        <Stat label="Total orders" value={data.user_activity.total_orders} />
        <Stat label="Revenue" value={`$${data.user_activity.total_revenue.toFixed(2)}`} />
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        <Panel title="Most viewed products">
          {data.most_viewed_products.map((p, i) => (
            <Row key={i} label={p.title} value={`${p.views} views`} />
          ))}
        </Panel>
        <Panel title="Most purchased products">
          {data.most_purchased_products.map((p, i) => (
            <Row key={i} label={p.title} value={`${p.units_sold} sold`} />
          ))}
        </Panel>
        <Panel title="Top categories">
          {data.top_categories.map((c, i) => (
            <Row key={i} label={c.category} value={`${c.num_products} items`} />
          ))}
        </Panel>
      </div>
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="rounded-xl2 bg-ink-800 border border-ink-700 p-5">
      <p className="text-mist-500 text-xs uppercase tracking-wide">{label}</p>
      <p className="font-display text-2xl text-signal-400 mt-1">{value}</p>
    </div>
  )
}

function Panel({ title, children }) {
  return (
    <div className="rounded-xl2 bg-ink-800 border border-ink-700 p-5">
      <h2 className="text-mist-100 font-medium mb-3">{title}</h2>
      <div className="flex flex-col gap-2">{children}</div>
    </div>
  )
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-mist-300 truncate pr-2">{label}</span>
      <span className="text-mist-500 shrink-0">{value}</span>
    </div>
  )
}
