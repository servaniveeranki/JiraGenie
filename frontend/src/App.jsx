import { useState } from 'react';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Loader2, 
  ChevronRight, 
  Layers, 
  CheckSquare,
  ChevronDown,
  Filter,
  BarChart3,
  X,
  Download
} from 'lucide-react';
import axios from 'axios';

function App() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [customPrompt, setCustomPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [jiraLoading, setJiraLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [jiraError, setJiraError] = useState(null);
  const [jiraSuccess, setJiraSuccess] = useState(null);
  const [expandedEpics, setExpandedEpics] = useState({});
  const [expandedStories, setExpandedStories] = useState({});
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [isDragging, setIsDragging] = useState(false);

  // Handle file drag and drop
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    handleFilesChange({ target: { files } });
  };

  const handleFilesChange = (e) => {
    const files = Array.from(e.target.files || []);
    setUploadedFiles(prev => [...prev, ...files]);
    setError(null);
  };

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (uploadedFiles.length === 0) {
      setError('Please upload at least one file (text or images)');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setJiraError(null);
    setJiraSuccess(null);

    try {
      const formData = new FormData();
      
      // Add all files
      uploadedFiles.forEach((file) => {
        formData.append('files', file);
      });

      // Add custom prompt if provided
      if (customPrompt.trim()) {
        formData.append('customPrompt', customPrompt.trim());
      }

      const response = await axios.post('http://localhost:8000/api/generate-tickets', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
    } catch (err) {
      console.error('Error:', err);
      setError(err.response?.data?.detail || 'Failed to generate tickets. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setUploadedFiles([]);
    setCustomPrompt('');
    setResult(null);
    setError(null);
    setJiraError(null);
    setJiraSuccess(null);
    setExpandedEpics({});
    setExpandedStories({});
    setCategoryFilter('ALL');
  };

  const handleCreateInJira = async () => {
    if (!result?.aiOutput) {
      setJiraError('No ticket data available. Please generate tickets first.');
      return;
    }

    setJiraLoading(true);
    setJiraError(null);
    setJiraSuccess(null);

    try {
      const response = await axios.post('http://localhost:8000/api/jira/create-tickets', {
        ai_output: result.aiOutput
      });
      
      if (response.data.success) {
        setJiraSuccess(
          `Successfully created ${response.data.created_issues.epics.length} epics, ` +
          `${response.data.created_issues.stories.length} stories, and ` +
          `${response.data.created_issues.subtasks.length} subtasks in Jira!`
        );
      } else {
        setJiraError(
          `Some issues were not created: ${response.data.errors?.join(', ') || 'Unknown error'}`
        );
      }
    } catch (err) {
      console.error('Jira creation error:', err);
      setJiraError(
        err.response?.data?.detail || 
        'Failed to create tickets in Jira. Please check your Jira configuration.'
      );
    } finally {
      setJiraLoading(false);
    }
  };

  const handleCreateDirectlyFromFile = async () => {
    if (uploadedFiles.length === 0) {
      setJiraError('Please upload a requirements file first.');
      return;
    }

    setJiraLoading(true);
    setJiraError(null);
    setJiraSuccess(null);

    try {
      const formData = new FormData();
      uploadedFiles.forEach((file) => {
        formData.append('files', file);
      });

      if (customPrompt.trim()) {
        formData.append('customPrompt', customPrompt.trim());
      }

      const response = await axios.post('http://localhost:8000/api/jira/create-from-file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      if (response.data.success) {
        setJiraSuccess(response.data.message);
      } else {
        setJiraError(
          response.data.message || 
          `Some issues were not created: ${response.data.errors?.join(', ') || 'Unknown error'}`
        );
        if (response.data.created_issues && 
            (response.data.created_issues.epics?.length > 0 || 
             response.data.created_issues.stories?.length > 0)) {
          setJiraSuccess(
            `Partially successful: Created ${response.data.created_issues.epics?.length || 0} epics, ` +
            `${response.data.created_issues.stories?.length || 0} stories, ` +
            `${response.data.created_issues.subtasks?.length || 0} subtasks`
          );
        }
      }
    } catch (err) {
      console.error('Direct Jira creation error:', err);
      setJiraError(
        err.response?.data?.detail || 
        'Failed to create tickets in Jira. Please check your Jira configuration.'
      );
    } finally {
      setJiraLoading(false);
    }
  };

  const toggleEpic = (epicIdx) => {
    setExpandedEpics(prev => ({
      ...prev,
      [epicIdx]: !prev[epicIdx]
    }));
  };

  const toggleStory = (epicIdx, storyIdx) => {
    const key = `${epicIdx}-${storyIdx}`;
    setExpandedStories(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const toggleAllEpics = () => {
    if (Object.keys(expandedEpics).length > 0) {
      setExpandedEpics({});
      setExpandedStories({});
    } else {
      const allExpanded = {};
      result?.aiOutput?.epics?.forEach((_, idx) => {
        allExpanded[idx] = true;
      });
      setExpandedEpics(allExpanded);
    }
  };

  const getFilteredEpics = () => {
    if (!result?.aiOutput?.epics) return [];
    if (categoryFilter === 'ALL') return result.aiOutput.epics;
    return result.aiOutput.epics.filter(
      epic => epic.category === categoryFilter
    );
  };

  const downloadJson = () => {
    if (!result?.aiOutput) return;
    
    const dataStr = `data:text/json;charset=utf-8,${encodeURIComponent(
      JSON.stringify(result.aiOutput, null, 2)
    )}`;
    
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute('href', dataStr);
    downloadAnchorNode.setAttribute('download', 'jira-tickets.json');
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-slate-200">
      {/* Navigation */}
      <nav className="bg-slate-800/80 backdrop-blur-md border-b border-slate-700/50 sticky top-0 z-50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <div className="h-10 w-10 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                  <Layers className="h-5 w-5 text-white" />
                </div>
                <span className="ml-3 text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-400">
                  JIRA Generator
                </span>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {uploadedFiles.length > 0 && (
                <button
                  onClick={handleCreateDirectlyFromFile}
                  disabled={jiraLoading}
                  className={`flex items-center px-4 py-2 rounded-md font-medium ${
                    jiraLoading
                      ? 'bg-emerald-700/50 text-emerald-300 cursor-not-allowed'
                      : 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white hover:from-emerald-600 hover:to-teal-700'
                  } transition-colors`}
                >
                  {jiraLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Creating in Jira...
                    </>
                  ) : (
                    <>
                      <Layers className="h-4 w-4 mr-2" />
                      Create in Jira (Direct)
                    </>
                  )}
                </button>
              )}
              {result && (
                <>
                  <button
                    onClick={downloadJson}
                    className="hidden sm:flex items-center px-3 py-1.5 text-sm font-medium rounded-md text-blue-300 hover:text-blue-100 bg-slate-700/50 hover:bg-slate-600/50 transition-colors"
                  >
                    <Download className="h-4 w-4 mr-1.5" />
                    Export JSON
                  </button>
                  <button
                    onClick={handleCreateInJira}
                    disabled={jiraLoading}
                    className={`flex items-center px-4 py-2 rounded-md font-medium ${
                      jiraLoading
                        ? 'bg-emerald-700/50 text-emerald-300 cursor-not-allowed'
                        : 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white hover:from-emerald-600 hover:to-teal-700'
                    } transition-colors`}
                  >
                    {jiraLoading ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Creating...
                      </>
                    ) : (
                      <>
                        <Layers className="h-4 w-4 mr-2" />
                        Create in Jira
                      </>
                    )}
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Upload Section */}
        <div className="max-w-4xl mx-auto">
          <div className="bg-slate-800/50 rounded-xl border border-slate-700/50 overflow-hidden shadow-lg">
            <div className="px-6 py-5 border-b border-slate-700/50 bg-gradient-to-r from-slate-800/50 to-slate-800/30">
              <h2 className="text-xl font-semibold text-white">Generate JIRA Tickets</h2>
              <p className="text-sm text-slate-400 mt-1">Upload requirements and let AI create your tickets</p>
            </div>

            <div className="p-6">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Custom Prompt */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Custom Instructions (Optional)
                  </label>
                  <div className="relative">
                    <textarea
                      value={customPrompt}
                      onChange={(e) => setCustomPrompt(e.target.value)}
                      placeholder="E.g., 'Include acceptance criteria', 'Add story points', etc."
                      className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-lg focus:ring-2 focus:ring-blue-500/50 focus:border-transparent text-slate-200 placeholder-slate-500 transition-all min-h-[100px] text-sm"
                      maxLength={500}
                    />
                    <div className="absolute bottom-2 right-2 text-xs text-slate-500">
                      {customPrompt.length}/500
                    </div>
                  </div>
                </div>

                {/* File Upload */}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Upload Requirements
                  </label>
                  <div 
                    className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
                      isDragging 
                        ? 'border-blue-500 bg-slate-800/30' 
                        : 'border-slate-700 hover:border-slate-600 bg-slate-800/30 hover:bg-slate-800/50'
                    }`}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                  >
                    <input
                      type="file"
                      id="file-upload"
                      className="hidden"
                      multiple
                      onChange={handleFilesChange}
                      accept=".txt,.md,.pdf,.doc,.docx,image/*"
                    />
                    <label
                      htmlFor="file-upload"
                      className="flex flex-col items-center justify-center space-y-3 cursor-pointer"
                    >
                      <div className="p-3 rounded-full bg-slate-700/50">
                        <Upload className="h-6 w-6 text-blue-400" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-slate-200">
                          {uploadedFiles.length > 0 
                            ? `${uploadedFiles.length} file${uploadedFiles.length > 1 ? 's' : ''} selected`
                            : 'Drag and drop files here or click to browse'}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">
                          Supported: .txt, .md, .pdf, .doc, .docx, images
                        </p>
                      </div>
                      <span className="text-xs text-blue-400 hover:text-blue-300 transition-colors">
                        Select files
                      </span>
                    </label>
                  </div>

                  {/* Uploaded files list */}
                  {uploadedFiles.length > 0 && (
                    <div className="mt-3 space-y-2">
                      {uploadedFiles.map((file, index) => (
                        <div 
                          key={index}
                          className="flex items-center justify-between bg-slate-800/50 rounded-lg px-3 py-2 text-sm"
                        >
                          <div className="flex items-center space-x-2">
                            <FileText className="h-4 w-4 text-blue-400 flex-shrink-0" />
                            <span className="truncate max-w-xs">{file.name}</span>
                            <span className="text-xs text-slate-500">
                              {(file.size / 1024).toFixed(1)} KB
                            </span>
                          </div>
                          <button
                            type="button"
                            onClick={() => removeFile(index)}
                            className="text-slate-500 hover:text-red-400 transition-colors"
                          >
                            <X className="h-4 w-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex flex-col sm:flex-row justify-end space-y-3 sm:space-y-0 sm:space-x-3">
                  {result && (
                    <button
                      type="button"
                      onClick={handleReset}
                      className="px-4 py-2 text-sm font-medium text-slate-300 hover:text-white transition-colors"
                    >
                      Start Over
                    </button>
                  )}
                  <button
                    type="submit"
                    disabled={uploadedFiles.length === 0 || loading}
                    className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                      uploadedFiles.length === 0 || loading
                        ? 'bg-slate-700/50 text-slate-500 cursor-not-allowed'
                        : 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white hover:from-blue-600 hover:to-indigo-700'
                    }`}
                  >
                    {loading ? (
                      <span className="flex items-center justify-center">
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Generating...
                      </span>
                    ) : (
                      'Generate Tickets'
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Messages */}
          <div className="mt-6 space-y-4">
            {error && (
              <div className="bg-red-900/30 border border-red-800/50 text-red-200 px-4 py-3 rounded-lg flex items-start space-x-3">
                <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-medium">Error</h3>
                  <p className="text-sm">{error}</p>
                </div>
              </div>
            )}

            {jiraError && (
              <div className="bg-amber-900/30 border border-amber-800/50 text-amber-200 px-4 py-3 rounded-lg flex items-start space-x-3">
                <AlertCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-medium">Jira Error</h3>
                  <p className="text-sm">{jiraError}</p>
                </div>
              </div>
            )}

            {jiraSuccess && (
              <div className="bg-green-900/30 border border-green-800/50 text-green-200 px-4 py-3 rounded-lg flex items-start space-x-3">
                <CheckCircle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-medium">Success!</h3>
                  <p className="text-sm">{jiraSuccess}</p>
                </div>
              </div>
            )}
          </div>

          {/* Results */}
          {result && (
            <div className="mt-8">
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6">
                <div>
                  <h2 className="text-xl font-semibold text-white">Generated Tickets</h2>
                  <p className="text-sm text-slate-400">
                    {result.stats.epics} Epics • {result.stats.stories} Stories • {result.stats.subtasks} Subtasks
                  </p>
                </div>
                
                <div className="mt-4 sm:mt-0 flex items-center space-x-3">
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Filter className="h-4 w-4 text-slate-500" />
                    </div>
                    <select
                      value={categoryFilter}
                      onChange={(e) => setCategoryFilter(e.target.value)}
                      className="pl-10 pr-8 py-2 bg-slate-800/50 border border-slate-700/50 rounded-lg text-sm text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-transparent appearance-none"
                    >
                      <option value="ALL">All Categories</option>
                      <option value="FUNCTIONAL">Functional</option>
                      <option value="NON-FUNCTIONAL">Non-Functional</option>
                    </select>
                    <div className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
                      <ChevronDown className="h-4 w-4 text-slate-400" />
                    </div>
                  </div>
                  
                  <button
                    onClick={toggleAllEpics}
                    className="px-3 py-2 text-xs font-medium rounded-lg bg-slate-800/50 hover:bg-slate-700/50 text-slate-300 hover:text-white transition-colors"
                  >
                    {Object.keys(expandedEpics).length > 0 ? 'Collapse All' : 'Expand All'}
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                {getFilteredEpics().length > 0 ? (
                  getFilteredEpics().map((epic, epicIdx) => (
                    <div 
                      key={epicIdx} 
                      className="bg-slate-800/30 rounded-xl border border-slate-700/50 overflow-hidden transition-all"
                    >
                      {/* Epic Header */}
                      <button
                        onClick={() => toggleEpic(epicIdx)}
                        className="w-full px-5 py-4 text-left flex items-center justify-between hover:bg-slate-800/50 transition-colors group"
                      >
                        <div className="flex items-center space-x-3">
                          <ChevronRight
                            className={`h-5 w-5 text-slate-400 transition-transform duration-200 ${
                              expandedEpics[epicIdx] ? 'transform rotate-90' : ''
                            }`}
                          />
                          <div>
                            <div className="flex items-center space-x-2">
                              <span className="font-medium text-blue-300 group-hover:text-blue-200">
                                {epic.summary}
                              </span>
                              <span className="text-xs px-2 py-0.5 rounded-full bg-blue-900/50 text-blue-200">
                                Epic
                              </span>
                              {epic.category && (
                                <span className="text-xs px-2 py-0.5 rounded-full bg-slate-700/50 text-slate-300">
                                  {epic.category}
                                </span>
                              )}
                            </div>
                            {epic.description && (
                              <p className="text-sm text-slate-400 mt-1 line-clamp-1">
                                {epic.description}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-xs px-2 py-1 bg-slate-700/50 rounded-full text-slate-300">
                            {epic.stories?.length || 0} {epic.stories?.length === 1 ? 'story' : 'stories'}
                          </span>
                        </div>
                      </button>

                      {/* Stories */}
                      {expandedEpics[epicIdx] && (
                        <div className="divide-y divide-slate-700/30">
                          {epic.stories?.map((story, storyIdx) => (
                            <div key={storyIdx} className="bg-slate-800/20 pl-12 pr-5 py-4">
                              <div className="flex items-start justify-between">
                                <div className="flex-1">
                                  <div className="flex items-center space-x-2">
                                    <CheckSquare className="h-4 w-4 text-green-400 mt-0.5 flex-shrink-0" />
                                    <span className="font-medium text-slate-200">
                                      {story.summary}
                                    </span>
                                    {story.priority && (
                                      <span 
                                        className={`text-xs px-2 py-0.5 rounded-full ${
                                          story.priority.toLowerCase() === 'high' 
                                            ? 'bg-red-900/50 text-red-200' 
                                            : story.priority.toLowerCase() === 'medium' 
                                              ? 'bg-yellow-900/50 text-yellow-200' 
                                              : 'bg-blue-900/50 text-blue-200'
                                        }`}
                                      >
                                        {story.priority}
                                      </span>
                                    )}
                                  </div>
                                  
                                  {story.description && (
                                    <p className="text-sm text-slate-400 mt-1 ml-6">
                                      {story.description}
                                    </p>
                                  )}

                                  {/* Subtasks */}
                                  {story.subtasks?.length > 0 && (
                                    <div className="mt-3 ml-6">
                                      <button
                                        onClick={() => toggleStory(epicIdx, storyIdx)}
                                        className="flex items-center text-xs text-slate-400 hover:text-slate-300 transition-colors"
                                      >
                                        <ChevronRight
                                          className={`h-3.5 w-3.5 mr-1 transition-transform duration-200 ${
                                            expandedStories[`${epicIdx}-${storyIdx}`] 
                                              ? 'transform rotate-90' 
                                              : ''
                                          }`}
                                        />
                                        {story.subtasks.length} subtasks
                                      </button>

                                      {expandedStories[`${epicIdx}-${storyIdx}`] && (
                                        <ul className="mt-2 ml-4 space-y-2">
                                          {story.subtasks.map((subtask, subIdx) => (
                                            <li 
                                              key={subIdx} 
                                              className="flex items-start"
                                            >
                                              <span className="w-1.5 h-1.5 mt-2 bg-slate-500 rounded-full flex-shrink-0 mr-2"></span>
                                              <span className="text-sm text-slate-300">
                                                {subtask.summary}
                                              </span>
                                            </li>
                                          ))}
                                        </ul>
                                      )}
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12 bg-slate-800/30 rounded-xl border-2 border-dashed border-slate-700/50">
                    <BarChart3 className="h-10 w-10 mx-auto text-slate-500 mb-3" />
                    <h3 className="text-lg font-medium text-slate-300">No matching epics found</h3>
                    <p className="text-slate-500 mt-1 text-sm">
                      Try adjusting your filters or generate new tickets with different requirements.
                    </p>
                  </div>
                )}
              </div>

              {/* Export Options */}
              <div className="mt-8 flex flex-wrap justify-end gap-3">
                <button
                  onClick={downloadJson}
                  className="flex items-center px-4 py-2 text-sm font-medium rounded-lg bg-slate-800/50 hover:bg-slate-700/50 text-slate-300 hover:text-white transition-colors"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download JSON
                </button>
                <button
                  onClick={handleCreateInJira}
                  disabled={jiraLoading}
                  className={`flex items-center px-4 py-2 text-sm font-medium rounded-lg ${
                    jiraLoading
                      ? 'bg-emerald-700/50 text-emerald-300 cursor-not-allowed'
                      : 'bg-gradient-to-r from-emerald-500 to-teal-600 text-white hover:from-emerald-600 hover:to-teal-700'
                  } transition-colors`}
                >
                  {jiraLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Creating in Jira...
                    </>
                  ) : (
                    <>
                      <Layers className="h-4 w-4 mr-2" />
                      Create in Jira
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="mt-12 py-6 border-t border-slate-800">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2">
              <div className="h-6 w-6 rounded-md bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                <Layers className="h-3.5 w-3.5 text-white" />
              </div>
              <span className="text-sm font-medium text-slate-400">
                JIRA Ticket Generator
              </span>
            </div>
            <div className="mt-4 md:mt-0 text-sm text-slate-500">
              &copy; {new Date().getFullYear()} All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
