import { Link } from 'react-router-dom'

export default function ProductCard({ product, reason }) {
  return (
    <Link
      to={`/product/${product.id}`}
      className="group flex flex-col rounded-xl2 bg-ink-800 border border-ink-700 overflow-hidden hover:border-signal-500/60 transition-colors"
    >
      <div className="aspect-square bg-ink-700 overflow-hidden">
        <img
          src={product.image_url}
          alt={product.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          loading="lazy"
        />
      </div>
      <div className="p-4 flex flex-col gap-1">
        <h3 className="text-sm font-medium text-mist-100 line-clamp-2">{product.title}</h3>
        <div className="flex items-center justify-between mt-1">
          <span className="text-signal-400 font-semibold">${product.price?.toFixed(2)}</span>
          {product.avg_rating > 0 && (
            <span className="text-xs text-mist-500">★ {product.avg_rating.toFixed(1)} ({product.num_ratings})</span>
          )}
        </div>
        {reason && (
          <p className="text-xs text-mist-500 mt-1 italic line-clamp-1">{reason}</p>
        )}
      </div>
    </Link>
  )
}
