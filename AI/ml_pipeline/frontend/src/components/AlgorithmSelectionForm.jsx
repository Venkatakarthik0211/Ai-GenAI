import React, { useState } from 'react'
import { pipelineApi } from '../services/api'

function AlgorithmSelectionForm({ run, onAlgorithmSelected }) {
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('')
  const [userFeedback, setUserFeedback] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const recommendedAlgorithms = run.recommended_algorithms || []
  const algorithmCategory = run.algorithm_category || 'unknown'
  const algorithmConfidence = run.algorithm_confidence || 0
  const learningParadigm = run.learning_paradigm || 'supervised'
  const algorithmRequirements = run.algorithm_requirements || {}
  const preprocessingPriorities = run.preprocessing_priorities || {}

  const handleSubmit = async (approved) => {
    if (approved && !selectedAlgorithm) {
      setError('Please select an algorithm before continuing')
      return
    }

    setSubmitting(true)
    setError(null)

    try {
      // Submit algorithm selection
      await pipelineApi.submitAlgorithmSelection(run.pipeline_run_id, {
        selected_algorithm: selectedAlgorithm,
        user_feedback: userFeedback,
        approved: approved
      })

      // If approved, continue to Agent 1B
      if (approved) {
        const continueResponse = await pipelineApi.continueAfterAlgorithmSelection(run.pipeline_run_id)

        if (!continueResponse.success) {
          throw new Error(continueResponse.message || 'Failed to continue to Agent 1B')
        }
      }

      // Notify parent component
      if (onAlgorithmSelected) {
        onAlgorithmSelected(approved)
      }
    } catch (err) {
      setError(err.message || 'Failed to submit algorithm selection')
      console.error('Error submitting algorithm selection:', err)
    } finally {
      setSubmitting(false)
    }
  }

  if (!recommendedAlgorithms || recommendedAlgorithms.length === 0) {
    return (
      <div className="bg-red-50 border-2 border-red-300 p-4 rounded-lg">
        <p className="text-red-800 font-semibold">⚠️ No algorithms recommended by Agent 1A</p>
      </div>
    )
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg border-2 border-blue-400 mb-6">
      {/* Header */}
      <div className="mb-6 p-6 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg shadow-lg">
        <h3 className="text-2xl font-bold flex items-center gap-2 mb-3">
          🤖 Agent 1A: Algorithm Recommendation
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-sm opacity-90 mb-1">Learning Paradigm</div>
            <div className="text-xl font-bold">
              {learningParadigm.replace(/_/g, ' ').toUpperCase()}
              <span className="ml-2">
                {learningParadigm === 'supervised' ? '🎯' : '🔍'}
              </span>
            </div>
          </div>

          <div>
            <div className="text-sm opacity-90 mb-1">Algorithm Category</div>
            <div className="text-xl font-bold">
              {algorithmCategory.replace(/_/g, ' ').toUpperCase()}
            </div>
          </div>

          <div>
            <div className="text-sm opacity-90 mb-1">Confidence</div>
            <div className="text-xl font-bold">
              {(algorithmConfidence * 100).toFixed(0)}%
              {algorithmConfidence >= 0.8 ? ' 🎯' : algorithmConfidence >= 0.6 ? ' ✓' : ' ⚠️'}
            </div>
          </div>
        </div>
      </div>

      {/* Algorithm Requirements */}
      {Object.keys(algorithmRequirements).length > 0 && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
            📋 Algorithm Requirements
          </h4>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(algorithmRequirements).map(([key, value]) => (
              <div key={key} className="flex justify-between">
                <span className="text-gray-600">{key.replace(/_/g, ' ')}:</span>
                <span className="font-medium text-gray-900">{String(value)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Algorithm Selection */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-900 mb-3 text-lg flex items-center gap-2">
          ✨ Select ONE Algorithm for Your ML Task
        </h4>
        <p className="text-sm text-gray-600 mb-4">
          Agent 1A recommends {recommendedAlgorithms.length} algorithms based on your data characteristics.
          Select one to continue with preprocessing configuration.
        </p>

        <div className="space-y-3">
          {recommendedAlgorithms.map((algorithm, index) => (
            <div
              key={index}
              onClick={() => setSelectedAlgorithm(algorithm)}
              className={`
                p-4 border-2 rounded-lg cursor-pointer transition-all duration-200
                ${selectedAlgorithm === algorithm
                  ? 'border-blue-600 bg-blue-50 shadow-lg'
                  : 'border-gray-300 bg-white hover:border-blue-400 hover:bg-blue-50'
                }
              `}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`
                    w-6 h-6 rounded-full border-2 flex items-center justify-center
                    ${selectedAlgorithm === algorithm
                      ? 'border-blue-600 bg-blue-600'
                      : 'border-gray-400'
                    }
                  `}>
                    {selectedAlgorithm === algorithm && (
                      <span className="text-white text-sm">✓</span>
                    )}
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900 text-lg">
                      {algorithm}
                    </div>
                    {index === 0 && (
                      <span className="text-xs text-blue-600 font-medium">
                        Recommended by Agent 1A
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Preprocessing Priorities Preview */}
      {Object.keys(preprocessingPriorities).length > 0 && (
        <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
            🔧 Preprocessing Priorities
          </h4>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {Object.entries(preprocessingPriorities).map(([step, priority]) => (
              <div key={step} className="flex justify-between">
                <span className="text-gray-600">{step.replace(/_/g, ' ')}:</span>
                <span className={`
                  font-medium px-2 py-0.5 rounded text-xs
                  ${priority === 'required' ? 'bg-red-100 text-red-800' :
                    priority === 'recommended' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'}
                `}>
                  {priority.toUpperCase()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* User Feedback */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Additional Comments (Optional)
        </label>
        <textarea
          value={userFeedback}
          onChange={(e) => setUserFeedback(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows="3"
          placeholder="Any feedback or reasons for your selection..."
        />
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-300 rounded-lg">
          <p className="text-red-800 text-sm">⚠️ {error}</p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3 justify-end">
        <button
          onClick={() => handleSubmit(false)}
          disabled={submitting}
          className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
        >
          {submitting ? '⏳ Processing...' : '❌ Reject & Restart from Agent 0'}
        </button>
        <button
          onClick={() => handleSubmit(true)}
          disabled={submitting || !selectedAlgorithm}
          className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
        >
          {submitting ? '⏳ Processing...' : '✅ Approve & Continue to Agent 1B'}
        </button>
      </div>

      {/* Info Box */}
      <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-900">
          <strong>ℹ️ What happens next?</strong><br/>
          • <strong>If you approve:</strong> Agent 1B will generate preprocessing questions tailored to your selected algorithm ({selectedAlgorithm || 'none selected'})<br/>
          • <strong>If you reject:</strong> Pipeline will restart from Agent 0 with your feedback
        </p>
      </div>
    </div>
  )
}

export default AlgorithmSelectionForm
