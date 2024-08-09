import { useState } from 'react'
import axios from 'axios'

export default function Home() {
  const [url, setUrl] = useState('')
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const response = await axios.post('http://localhost:8000/api/v1/analysis/', { url })
      setAnalysis(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-light-blue-500 shadow-lg transform -skew-y-6 sm:skew-y-0 sm:-rotate-6 sm:rounded-3xl"></div>
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <div className="max-w-md mx-auto">
            <div>
              <h1 className="text-2xl font-semibold">Writer Analysis Tool</h1>
            </div>
            <div className="divide-y divide-gray-200">
              <form onSubmit={handleSubmit} className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                <div className="relative">
                  <input
                    id="url"
                    name="url"
                    type="text"
                    className="peer placeholder-transparent h-10 w-full border-b-2 border-gray-300 text-gray-900 focus:outline-none focus:border-rose-600"
                    placeholder="Enter URL"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                  />
                  <label htmlFor="url" className="absolute left-0 -top-3.5 text-gray-600 text-sm peer-placeholder-shown:text-base peer-placeholder-shown:text-gray-440 peer-placeholder-shown:top-2 transition-all peer-focus:-top-3.5 peer-focus:text-gray-600 peer-focus:text-sm">Enter URL</label>
                </div>
                <div className="relative">
                  <button className="bg-blue-500 text-white rounded-md px-2 py-1">Analyze</button>
                </div>
              </form>
            </div>
            {loading && <p>Loading...</p>}
            {error && <p className="text-red-500">{error}</p>}
            {analysis && (
              <div className="mt-8">
                <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
                <p><strong>Insights:</strong> {analysis.insights}</p>
                <p><strong>Writing Style:</strong> {analysis.writing_style}</p>
                <p><strong>Key Themes:</strong> {analysis.key_themes.join(', ')}</p>
                <p><strong>Readability Score:</strong> {analysis.readability_score.toFixed(2)}</p>
                <p><strong>Sentiment:</strong> {analysis.sentiment}</p>
                <p><strong>Post Count:</strong> {analysis.post_count}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}