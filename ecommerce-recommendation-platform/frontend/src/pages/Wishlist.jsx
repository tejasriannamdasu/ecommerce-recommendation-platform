import { useEffect, useState } from 'react'
import client from '../api/client.js'
import ProductCard from '../components/ProductCard.jsx'

export default function Wishlist() {
  const [items, setItems] = useState([])
  useEffect(() => { client.get('/wishlist').then((res) => setItems(res.data)) }, [])
  return (
    <div className="pt-16">
      <h1 className="font-display text-3xl text-mist-100 mb-6">Your wishlist</h1>
      {items.length === 0 ? (
        <p className="text-mist-500">Nothing saved yet.</p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {items.map((p) => <ProductCard key={p.id} product={p} />)}
        </div>
      )}
    </div>
  )
}
