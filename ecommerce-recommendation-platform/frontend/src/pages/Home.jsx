import { useEffect, useState } from 'react'
import client from '../api/client.js'
import { useAuth } from '../api/AuthContext.jsx'
import RecommendationRail from '../components/RecommendationRail.jsx'
import ProductCard from '../components/ProductCard.jsx'

export default function Home() {
  const { user } = useAuth()
  const [personalized, setPersonalized] = useState({ items: [], loading: true })
  const [trending, setTrending] = useState({ items: [], loading: true })
  const [catalog, setCatalog] = useState([])

  useEffect(() => {
    client.get('/recommendations/trending?limit=10')
      .then((res) => setTrending({ items: res.data.items, loading: false }))
      .catch(() => setTrending({ items: [], loading: false }))

    client.get('/products?limit=12')
      .then((res) => setCatalog(res.data))
      .catch(() => {})

    if (user) {
      client.get('/recommendations/personalized?limit=10')
        .then((res) => setPersonalized({ items: res.data.items, loading: false }))
        .catch(() => setPersonalized({ items: [], loading: false }))
    } else {
      setPersonalized({ items: [], loading: false })
    }
  }, [user])

  return (
    <div>
      <section className="pt-16 pb-10 border-b border-ink-700">
        <p className="uppercase tracking-widest text-signal-500 text-xs font-medium mb-3">Hybrid ML Recommendation Engine</p>
        <h1 className="font-display text-4xl md:text-5xl text-mist-100 max-w-2xl leading-tight">
          Every shelf, quietly rearranged for you.
        </h1>
        <p className="text-mist-500 mt-4 max-w-lg">
          Content-based filtering, collaborative filtering, and semantic vector
          search — blended into one ranked feed, explained in plain language.
        </p>
      </section>

      {user && (
        <RecommendationRail
          title="Picked for you"
          items={personalized.items}
          loading={personalized.loading}
        />
      )}

      <RecommendationRail
        title="Trending right now"
        items={trending.items}
        loading={trending.loading}
      />

      <section className="mt-12">
        <h2 className="font-display text-2xl text-mist-100 mb-4">Browse the catalog</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {catalog.map((p) => <ProductCard key={p.id} product={p} />)}
        </div>
      </section>
    </div>
  )
}
