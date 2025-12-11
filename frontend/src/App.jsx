import { useState } from 'react'
import { Upload, FileText, Image, CheckCircle, AlertCircle, Loader2 } from 'lucide-react'
import axios from 'axios'

function App() {
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [customPrompt, setCustomPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleFilesChange = (e) => {
    const files = Array.from(e.target.files)
    setUploadedFiles(files)
    setError(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (uploadedFiles.length === 0) {
      setError('Please upload at least one file (text or images)')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const formData = new FormData()
      
      // Add all files
      uploadedFiles.forEach((file) => {
        formData.append('files', file)
      })

      // Add custom prompt if provided
      if (customPrompt.trim()) {
        formData.append('customPrompt', customPrompt.trim())
      }

      const response = await axios.post('http://localhost:8000/api/generate-tickets', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setResult(response.data)
    } catch (err) {
      console.error('Error:', err)
      setError(err.response?.data?.detail || 'Failed to generate tickets. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setUploadedFiles([])
    setCustomPrompt('')
    setResult(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
                <FileText className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
                JIRA Ticket Generator
              </span>
            </div>
            <div className="text-sm text-gray-600">
              AI-Powered Requirements Analysis
            </div>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-6 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-6xl font-extrabold text-gray-900 mb-6">
            Transform Requirements into{' '}
            <span className="bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent">
              JIRA Tickets
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Upload your requirements and architecture diagrams. Our AI will analyze them and generate 
            comprehensive Epics, Stories, and Subtasks ready for JIRA.
          </p>
          <div className="mt-8 flex items-center justify-center gap-8 text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span>AI-Powered Analysis</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span>Custom Prompts</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <span>Multi-file Support</span>
            </div>
          </div>
        </div>

        {/* Upload Form */}
        <div className="max-w-5xl mx-auto">
          <div className="bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-8 py-6">
              <h2 className="text-2xl font-bold text-white">Configure Your Analysis</h2>
              <p className="text-indigo-100 mt-1">Customize the AI prompt and upload your files</p>
            </div>
            
            <form onSubmit={handleSubmit} className="p-8 space-y-8">
            {/* Custom Prompt Input */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-6 border border-indigo-100">
              <label className="flex items-center gap-2 text-base font-bold text-gray-800 mb-4">
                <span className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center text-white text-sm">
                  1
                </span>
                Custom AI Prompt (Optional)
              </label>
              <textarea
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="Enter your custom instructions for AI analysis... (Leave empty to use default prompt)&#10;&#10;Example: 'Generate user stories with acceptance criteria. Focus on security and performance. Include story points estimation.'"
                className="w-full h-40 px-5 py-4 border-2 border-indigo-200 rounded-xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:outline-none resize-none text-sm bg-white shadow-sm transition-all"
              />
              <p className="text-xs text-gray-600 mt-3 flex items-start gap-2">
                <span className="text-indigo-600 mt-0.5">💡</span>
                <span>Pro tip: Be specific about what you want. Mention acceptance criteria, story points, priority levels, or technical details you need.</span>
              </p>
            </div>

            {/* Combined File Upload */}
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-6 border border-purple-100">
              <label className="flex items-center gap-2 text-base font-bold text-gray-800 mb-4">
                <span className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center text-white text-sm">
                  2
                </span>
                Upload Files (Requirements + Diagrams)
              </label>
              <div className="border-3 border-dashed border-purple-300 rounded-xl p-10 hover:border-purple-500 hover:bg-white transition-all cursor-pointer bg-white/50">
                <input
                  type="file"
                  accept=".txt,image/*"
                  multiple
                  onChange={handleFilesChange}
                  className="hidden"
                  id="files-upload"
                />
                <label
                  htmlFor="files-upload"
                  className="flex flex-col items-center cursor-pointer"
                >
                  <div className="flex gap-6 mb-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg transform hover:scale-105 transition-transform">
                      <FileText className="w-8 h-8 text-white" />
                    </div>
                    <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg transform hover:scale-105 transition-transform">
                      <Image className="w-8 h-8 text-white" />
                    </div>
                  </div>
                  <span className="text-base font-semibold text-gray-700 text-center mb-2">
                    {uploadedFiles.length > 0
                      ? `${uploadedFiles.length} file(s) selected`
                      : 'Click or drag files here'}
                  </span>
                  <span className="text-sm text-gray-500 text-center">
                    Upload .txt files and images (PNG, JPG, etc.)
                  </span>
                  <span className="text-xs text-gray-400 mt-2">
                    Select multiple files at once with Ctrl+Click
                  </span>
                </label>
              </div>
              {uploadedFiles.length > 0 && (
                <div className="mt-5 space-y-2">
                  <p className="text-sm font-semibold text-gray-700 mb-3">Selected Files:</p>
                  <div className="grid grid-cols-2 gap-2">
                    {uploadedFiles.map((file, idx) => (
                      <div
                        key={idx} 
                        className={`flex items-center gap-3 px-4 py-3 rounded-lg shadow-sm border ${
                          file.name.endsWith('.txt') 
                            ? 'bg-blue-50 border-blue-200' 
                            : 'bg-green-50 border-green-200'
                        }`}
                      >
                        <span className="text-2xl">
                          {file.name.endsWith('.txt') ? '📄' : '🖼️'}
                        </span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-800 truncate">{file.name}</p>
                          <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading || uploadedFiles.length === 0}
                className="flex-1 bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-4 px-8 rounded-xl font-bold text-lg hover:from-indigo-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 flex items-center justify-center gap-3"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-6 h-6 animate-spin" />
                    Analyzing with AI...
                  </>
                ) : (
                  <>
                    <Upload className="w-6 h-6" />
                    Generate JIRA Tickets
                  </>
                )}
              </button>
              <button
                type="button"
                onClick={handleReset}
                className="px-8 py-4 border-2 border-gray-300 rounded-xl font-semibold text-gray-700 hover:bg-gray-50 hover:border-gray-400 transition-all"
              >
                Reset
              </button>
            </div>
          </form>

          {/* Error Message */}
          {error && (
            <div className="m-8 bg-red-50 border-2 border-red-200 rounded-xl p-5 flex items-start gap-4 shadow-sm">
              <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-base font-bold text-red-800">Error</p>
                <p className="text-sm text-red-600 mt-1">{error}</p>
              </div>
            </div>
          )}
          </div>
        </div>

        {/* Results Display */}
        {result && (
          <div className="max-w-6xl mx-auto mt-12">
            <div className="bg-white rounded-3xl shadow-2xl border border-gray-100 overflow-hidden">
              {/* Success Header */}
              <div className="bg-gradient-to-r from-green-500 to-emerald-600 px-8 py-6">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
                    <CheckCircle className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <h2 className="text-3xl font-bold text-white">
                      Tickets Generated Successfully!
                    </h2>
                    <p className="text-green-50 mt-1 text-base">
                      {result.stats.epics} Epic(s) • {result.stats.imagesProcessed} Image(s) Processed
                    </p>
                  </div>
                </div>
              </div>

              {/* Epics Display */}
              <div className="p-8 space-y-8">
                {result.aiOutput.epics?.map((epic, epicIdx) => (
                  <div key={epicIdx} className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl border-2 border-indigo-200 overflow-hidden shadow-lg hover:shadow-xl transition-shadow">
                    <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4">
                      <div className="flex items-center gap-3">
                        <span className="px-3 py-1 bg-white/20 text-white text-xs font-bold rounded-full backdrop-blur-sm">
                          EPIC {epicIdx + 1}
                        </span>
                        <h3 className="text-2xl font-bold text-white flex-1">
                          {epic.summary}
                        </h3>
                      </div>
                      <p className="text-indigo-100 mt-3 text-sm leading-relaxed">
                        {epic.description}
                      </p>
                    </div>

                    {/* Stories */}
                    <div className="p-6 space-y-4">
                      {epic.stories?.map((story, storyIdx) => (
                        <div key={storyIdx} className="bg-white rounded-xl border border-gray-200 shadow-md hover:shadow-lg transition-shadow overflow-hidden">
                          <div className="bg-gradient-to-r from-blue-500 to-cyan-500 px-5 py-3">
                            <div className="flex items-center gap-2">
                              <span className="px-2 py-0.5 bg-white/30 text-white text-xs font-bold rounded backdrop-blur-sm">
                                STORY {storyIdx + 1}
                              </span>
                              <h4 className="text-lg font-bold text-white flex-1">
                                {story.summary}
                              </h4>
                            </div>
                          </div>
                          <div className="p-5">
                            <p className="text-sm text-gray-700 leading-relaxed mb-4">
                              {story.description}
                            </p>

                            {/* Subtasks */}
                            {story.subtasks && story.subtasks.length > 0 && (
                              <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                                <p className="text-xs font-bold text-gray-600 uppercase mb-3 flex items-center gap-2">
                                  <span className="w-5 h-5 bg-green-500 rounded flex items-center justify-center text-white text-xs">
                                    {story.subtasks.length}
                                  </span>
                                  Subtasks
                                </p>
                                <div className="space-y-2">
                                  {story.subtasks.map((subtask, subIdx) => (
                                    <div key={subIdx} className="flex items-start gap-3 bg-white rounded-lg px-4 py-2.5 border border-gray-100 hover:border-green-300 transition-colors">
                                      <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
                                      <span className="text-sm text-gray-700">
                                        {subtask.summary}
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              {/* Download JSON */}
              <div className="p-8 pt-0">
                <button
                  onClick={() => {
                    const dataStr = JSON.stringify(result.aiOutput, null, 2)
                    const dataBlob = new Blob([dataStr], { type: 'application/json' })
                    const url = URL.createObjectURL(dataBlob)
                    const link = document.createElement('a')
                    link.href = url
                    link.download = 'jira-tickets.json'
                    link.click()
                  }}
                  className="w-full bg-gradient-to-r from-gray-800 to-gray-900 text-white py-4 px-6 rounded-xl font-bold text-lg hover:from-gray-900 hover:to-black transition-all shadow-lg hover:shadow-xl"
                >
                  📥 Download JSON for JIRA
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
