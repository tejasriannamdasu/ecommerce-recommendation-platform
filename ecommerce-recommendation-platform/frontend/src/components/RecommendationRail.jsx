import ProductCard from './ProductCard.jsx'

export default function RecommendationRail({ title, items = [], loading }) {
  return (
    <section className="mt-12">
      <h2 className="font-display text-2xl text-mist-100 mb-4">{title}</h2>
      {loading ? (
        <div className="text-mist-500 text-sm">Loading recommendations…</div>
      ) : items.length === 0 ? (
        <div className="text-mist-500 text-sm">Nothing to show yet.</div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {items.map((item) => (
            <ProductCard
              key={item.product?.id ?? item.id}
              product={item.product ?? item}
              reason={item.reason}
            />
          ))}
        </div>
      )}
    </section>
  )
}
