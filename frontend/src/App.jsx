import { useState } from "react"
import axios from "axios"

const API_URL = "http://127.0.0.1:8000"

const severityColor = {
  critical: "bg-red-100 text-red-700 border-red-200",
  high: "bg-orange-100 text-orange-700 border-orange-200",
  medium: "bg-yellow-100 text-yellow-700 border-yellow-200",
  low: "bg-green-100 text-green-700 border-green-200",
}

export default function App() {
  const [product, setProduct] = useState("")
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState("")

  async function handleSearch() {
    if (!product.trim()) return
    setLoading(true)
    setError("")
    setResult(null)
    try {
      const res = await axios.post(`${API_URL}/search/`, {
        product: product.trim(),
        limit: 10,
      })
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong")
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") handleSearch()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <h1 className="text-2xl font-bold text-gray-900">ProblemBase</h1>
        <p className="text-sm text-gray-500">A search engine for unsolved software problems</p>
      </div>

      <div className="max-w-3xl mx-auto px-6 py-12">
        <div className="flex gap-3">
          <input
            type="text"
            value={product}
            onChange={(e) => setProduct(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Search a product... e.g. Notion, Slack, Figma"
            className="flex-1 border border-gray-300 rounded-lg px-4 py-3 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSearch}
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition"
          >
            {loading ? "Searching..." : "Search"}
          </button>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {loading && (
          <div className="mt-12 text-center text-gray-500">
            <p className="text-lg">Scraping complaints and analyzing with AI...</p>
            <p className="text-sm mt-1">This takes 10-15 seconds on first search</p>
          </div>
        )}

        {result && (
          <div className="mt-8">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                Problems with <span className="text-blue-600">{result.product}</span>
              </h2>
              <p className="text-sm text-gray-500 mt-1">
                {result.total_complaints} complaints analyzed · {result.clusters.length} themes found
              </p>
            </div>

            <div className="space-y-4">
              {result.clusters.map((cluster, i) => (
                <div key={i} className="bg-white border border-gray-200 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold text-gray-900 text-lg">{cluster.theme}</h3>
                    <span className={`text-xs font-medium px-3 py-1 rounded-full border ${severityColor[cluster.severity]}`}>
                      {cluster.severity}
                    </span>
                  </div>

                  <p className="text-gray-600 text-sm mb-4">{cluster.insight}</p>

                  <div className="space-y-2">
                    {cluster.complaints.slice(0, 3).map((c, j) => (
                      <a key={j} href={c.url} target="_blank" rel="noreferrer" className="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-medium text-gray-400 uppercase">{c.source}</span>
                          <span className="text-xs text-gray-400">· {c.score} pts</span>
                        </div>
                        <p className="text-sm text-gray-700 line-clamp-2">{c.text}</p>
                      </a>
                    ))}
                  </div>

                  <p className="text-xs text-gray-400 mt-3">{cluster.complaint_count} complaints in this theme</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}