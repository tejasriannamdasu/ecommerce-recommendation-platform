import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import client from '../api/client.js'
import ProductCard from '../components/ProductCard.jsx'

export default function SearchResults() {
  const [params] = useSearchParams()
  const q = params.get('q') || ''
  const [result, setResult] = useState({ products: [], total: 0 })
  const [semantic, setSemantic] = useState(true)

  useEffect(() => {
    if (!q) return
    client.get(`/products/search?q=${encodeURIComponent(q)}&semantic=${semantic}`)
      .then((res) => setResult(res.data))
  }, [q, semantic])

  return (
    <div className="pt-16">
      <div className="flex items-center justify-between mb-6">
        <h1 className="font-display text-3xl text-mist-100">Results for "{q}"</h1>
        <label className="flex items-center gap-2 text-sm text-mist-500">
          <input type="checkbox" checked={semantic} onChange={(e) => setSemantic(e.target.checked)} />
          Semantic search
        </label>
      </div>
      <p className="text-mist-500 text-sm mb-4">{result.total} products found</p>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {result.products.map((p) => <ProductCard key={p.id} product={p} />)}
      </div>
    </div>
  )
}
