import React, { useState } from 'react'
import { pipelineApi } from '../services/api'

function PreprocessingReviewForm({ run, onReviewSubmitted }) {
  const [userFeedback, setUserFeedback] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [expandedStep, setExpandedStep] = useState(null)

  const preprocessingSummary = run.preprocessing_summary || {}
  const originalShape = preprocessingSummary.original_shape || {}
  const finalShape = preprocessingSummary.final_shape || {}
  const stepsCompleted = preprocessingSummary.steps_completed || []
  const rowsRemoved = preprocessingSummary.rows_removed || 0
  const columnsAdded = preprocessingSummary.columns_added || 0

  const handleSubmit = async (approved) => {
    setSubmitting(true)
    setError(null)

    try {
      // Submit preprocessing review
      await pipelineApi.submitPreprocessingReview(run.pipeline_run_id, {
        approved: approved,
        user_feedback: userFeedback
      })

      // If approved, continue pipeline to feature engineering
      if (approved) {
        const continueResponse = await pipelineApi.continuePipeline(run.pipeline_run_id)

        if (!continueResponse.success) {
          throw new Error(continueResponse.message || 'Pipeline continuation failed')
        }
      }

      // Notify parent component
      if (onReviewSubmitted) {
        onReviewSubmitted(approved)
      }
    } catch (err) {
      setError(err.message || 'Failed to submit preprocessing review')
      console.error('Error submitting preprocessing review:', err)
    } finally {
      setSubmitting(false)
    }
  }

  const toggleStep = (stepName) => {
    setExpandedStep(expandedStep === stepName ? null : stepName)
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg border-2 border-green-300 mb-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold flex items-center gap-2">
          <span className="text-2xl">✓</span> Preprocessing Complete - Review Results
        </h3>
      </div>

      {/* Overall Summary */}
      <div className="mb-6 p-6 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg shadow-lg">
        <h4 className="text-2xl font-bold mb-4">Data Transformation Summary</h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Original Shape */}
          <div className="p-4 bg-white/10 rounded-lg">
            <div className="text-sm opacity-90 mb-2">Original Dataset</div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold">{originalShape.rows || 0}</span>
              <span className="text-lg">rows</span>
              <span className="text-2xl mx-2">×</span>
              <span className="text-3xl font-bold">{originalShape.columns || 0}</span>
              <span className="text-lg">columns</span>
            </div>
          </div>

          {/* Final Shape */}
          <div className="p-4 bg-white/10 rounded-lg">
            <div className="text-sm opacity-90 mb-2">After Preprocessing</div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold">{finalShape.rows || 0}</span>
              <span className="text-lg">rows</span>
              <span className="text-2xl mx-2">×</span>
              <span className="text-3xl font-bold">{finalShape.columns || 0}</span>
              <span className="text-lg">columns</span>
            </div>
          </div>

          {/* Changes */}
          <div className="p-4 bg-white/10 rounded-lg">
            <div className="text-sm opacity-90 mb-2">Rows Removed</div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold">{rowsRemoved}</span>
              <span className="text-lg">rows</span>
              {rowsRemoved > 0 && originalShape.rows > 0 && (
                <span className="text-sm opacity-75">
                  ({((rowsRemoved / originalShape.rows) * 100).toFixed(1)}%)
                </span>
              )}
            </div>
          </div>

          <div className="p-4 bg-white/10 rounded-lg">
            <div className="text-sm opacity-90 mb-2">Columns Added</div>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold">{columnsAdded}</span>
              <span className="text-lg">columns</span>
              {columnsAdded > 0 && originalShape.columns > 0 && (
                <span className="text-sm opacity-75">
                  ({((columnsAdded / originalShape.columns) * 100).toFixed(1)}%)
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Steps Detail */}
      <div className="mb-6">
        <h4 className="text-lg font-bold mb-4">Preprocessing Steps Applied</h4>
        <div className="space-y-3">
          {stepsCompleted.map((step, idx) => {
            const isExpanded = expandedStep === step.step

            return (
              <div key={idx} className="border-2 border-gray-200 rounded-lg overflow-hidden">
                {/* Step Header */}
                <div
                  onClick={() => toggleStep(step.step)}
                  className="p-4 bg-gray-50 cursor-pointer hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-xl font-bold text-blue-600">
                        {idx + 1}
                      </span>
                      <div>
                        <div className="font-semibold text-lg capitalize">
                          {step.step.replace(/_/g, ' ')}
                        </div>
                        <div className="text-sm text-gray-600">
                          Technique: <span className="font-medium text-blue-600">{step.technique}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {step.rows_removed !== null && step.rows_removed > 0 && (
                        <span className="px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-semibold">
                          -{step.rows_removed} rows
                        </span>
                      )}
                      {step.missing_handled !== null && step.missing_handled > 0 && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs font-semibold">
                          {step.missing_handled} values imputed
                        </span>
                      )}
                      {step.new_columns_created !== null && step.new_columns_created > 0 && (
                        <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-semibold">
                          +{step.new_columns_created} columns
                        </span>
                      )}
                      {step.scaler_fitted && (
                        <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded text-xs font-semibold">
                          Scaler fitted
                        </span>
                      )}
                      <span className="text-gray-400 ml-2">
                        {isExpanded ? '▼' : '▶'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Step Details (Expanded) */}
                {isExpanded && (
                  <div className="p-4 bg-white border-t-2 border-gray-200">
                    {/* Algorithm Context */}
                    {step.algorithm_context && (
                      <div className="mb-3 p-3 bg-purple-50 border border-purple-200 rounded">
                        <div className="text-xs font-semibold text-purple-800 mb-1">
                          Algorithm Context
                        </div>
                        <div className="text-sm text-purple-700 capitalize">
                          {step.algorithm_context.replace(/_/g, ' ')}
                        </div>
                      </div>
                    )}

                    {/* Bedrock LLM Reasoning */}
                    {step.bedrock_reasoning && (
                      <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded">
                        <div className="text-xs font-semibold text-blue-800 mb-1 flex items-center gap-1">
                          <span>🤖</span> Bedrock LLM Reasoning
                        </div>
                        <div className="text-sm text-blue-700">
                          {step.bedrock_reasoning}
                        </div>
                      </div>
                    )}

                    {/* Parameters */}
                    {step.parameters && Object.keys(step.parameters).length > 0 && (
                      <div className="mb-3 p-3 bg-gray-50 border border-gray-200 rounded">
                        <div className="text-xs font-semibold text-gray-800 mb-2">
                          Parameters Used
                        </div>
                        <div className="space-y-1">
                          {Object.entries(step.parameters).map(([key, value]) => (
                            <div key={key} className="flex justify-between text-sm">
                              <span className="text-gray-600">{key}:</span>
                              <span className="font-medium text-gray-900">
                                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* High Cardinality Strategy (for encode_features) */}
                    {step.high_cardinality_strategy && (
                      <div className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                        <div className="text-xs font-semibold text-yellow-800 mb-1">
                          High-Cardinality Strategy
                        </div>
                        <div className="text-sm text-yellow-700">
                          <div><strong>Technique:</strong> {step.high_cardinality_strategy.technique}</div>
                          <div><strong>Columns:</strong> {step.high_cardinality_strategy.columns?.join(', ')}</div>
                          {step.high_cardinality_strategy.reasoning && (
                            <div className="mt-1 italic">{step.high_cardinality_strategy.reasoning}</div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Optional Feedback */}
      <div className="mb-6 border-t-2 border-gray-300 pt-6">
        <label className="block text-sm font-semibold mb-2">
          Feedback (Optional)
        </label>
        <textarea
          value={userFeedback}
          onChange={(e) => setUserFeedback(e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
          rows="3"
          placeholder="Any concerns about the preprocessing results? (e.g., 'Too many rows removed', 'Should use different encoding')"
        />
      </div>

      {/* Error Display */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded text-red-800 text-sm">
          {error}
        </div>
      )}

      {/* Submit Buttons */}
      <div className="flex gap-4">
        <button
          onClick={() => handleSubmit(true)}
          disabled={submitting}
          className="flex-1 py-3 px-6 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-bold rounded-lg text-lg"
        >
          {submitting ? 'Submitting...' : '✓ Approve & Continue to Feature Engineering'}
        </button>
        <button
          onClick={() => handleSubmit(false)}
          disabled={submitting}
          className="flex-1 py-3 px-6 bg-orange-600 hover:bg-orange-700 disabled:opacity-50 text-white font-bold rounded-lg text-lg"
        >
          {submitting ? 'Submitting...' : '🔄 Reject & Retry Preprocessing'}
        </button>
      </div>
      <div className="mt-2 text-sm text-gray-600 text-center">
        Note: Rejecting will restart preprocessing from the beginning with new LLM parameter selection
      </div>
    </div>
  )
}

export default PreprocessingReviewForm
