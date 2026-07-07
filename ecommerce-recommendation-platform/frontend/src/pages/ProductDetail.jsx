import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import client from '../api/client.js'
import { useAuth } from '../api/AuthContext.jsx'
import RecommendationRail from '../components/RecommendationRail.jsx'

export default function ProductDetail() {
  const { id } = useParams()
  const { user } = useAuth()
  const [product, setProduct] = useState(null)
  const [similar, setSimilar] = useState({ items: [], loading: true })

  useEffect(() => {
    client.get(`/products/${id}`).then((res) => setProduct(res.data))
    client.get(`/products/${id}/similar?limit=8`)
      .then((res) => setSimilar({ items: res.data, loading: false }))
      .catch(() => setSimilar({ items: [], loading: false }))
    if (user) client.post(`/products/${id}/view`).catch(() => {})
  }, [id, user])

  const addToWishlist = () => client.post(`/wishlist/${id}`)

  if (!product) return <div className="pt-16 text-mist-500">Loading…</div>

  return (
    <div className="pt-12">
      <div className="grid md:grid-cols-2 gap-10">
        <div className="aspect-square bg-ink-800 rounded-xl2 overflow-hidden">
          <img src={product.image_url} alt={product.title} className="w-full h-full object-cover" />
        </div>
        <div>
          <h1 className="font-display text-3xl text-mist-100">{product.title}</h1>
          <p className="text-signal-400 text-2xl font-semibold mt-2">${product.price?.toFixed(2)}</p>
          <p className="text-mist-500 mt-4 leading-relaxed">{product.description}</p>
          <div className="flex items-center gap-3 mt-4 text-sm text-mist-500">
            <span>★ {product.avg_rating?.toFixed(1)} ({product.num_ratings} ratings)</span>
            <span>·</span>
            <span>{product.brand}</span>
          </div>
          {user && (
            <button
              onClick={addToWishlist}
              className="mt-6 rounded-full bg-signal-500 text-ink-950 font-medium px-6 py-2 hover:bg-signal-400"
            >
              Add to wishlist
            </button>
          )}
        </div>
      </div>

      <RecommendationRail title="Similar products" items={similar.items} loading={similar.loading} />
    </div>
  )
}
