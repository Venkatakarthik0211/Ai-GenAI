import React, { useState } from 'react'
import { pipelineApi } from '../services/api'

function ReviewForm({ run, onReviewSubmitted }) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState({})
  const [selectedOptions, setSelectedOptions] = useState({}) // Track selected option objects
  const [userFeedback, setUserFeedback] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [viewMode, setViewMode] = useState('wizard') // 'wizard' or 'overview'

  const questions = run.review_questions || []
  const currentQuestion = questions[currentQuestionIndex]
  const isLastQuestion = currentQuestionIndex === questions.length - 1
  const allQuestionsAnswered = questions.every(q => answers[q.question_id] !== undefined)

  // Algorithm context from Agent 1A
  const algorithmCategory = run.algorithm_category || 'unknown'
  const algorithmConfidence = run.algorithm_confidence || 0
  const recommendedAlgorithms = run.recommended_algorithms || []
  const algorithmRequirements = run.algorithm_requirements || {}

  // Get suitability badge color
  const getSuitabilityColor = (suitability) => {
    switch (suitability?.toLowerCase()) {
      case 'excellent': return 'bg-green-100 text-green-800 border-green-300'
      case 'good': return 'bg-blue-100 text-blue-800 border-blue-300'
      case 'acceptable': return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'poor': return 'bg-red-100 text-red-800 border-red-300'
      default: return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const handleAnswer = (questionId, answerValue, optionObject = null) => {
    setAnswers({
      ...answers,
      [questionId]: answerValue
    })

    if (optionObject) {
      setSelectedOptions({
        ...selectedOptions,
        [questionId]: optionObject
      })
    }
  }

  const handleNext = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
    }
  }

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1)
    }
  }

  const handleSubmit = async (approved) => {
    setSubmitting(true)
    setError(null)

    try {
      // Convert answers to the expected format
      // For technique selection questions, we need to extract the technique name and parameters
      const answersArray = Object.entries(answers).map(([question_id, answer]) => {
        const question = questions.find(q => q.question_id === question_id)
        const selectedOption = selectedOptions[question_id]

        return {
          question_id,
          answer,
          // Include technique name and params if this is a technique selection
          ...(selectedOption && selectedOption.value && {
            technique_name: selectedOption.value,
            technique_params: selectedOption.parameters || {}
          })
        }
      })

      // Submit review
      await pipelineApi.submitReviewAnswers(run.pipeline_run_id, {
        answers: answersArray,
        user_feedback: userFeedback,
        approved: approved
      })

      // If approved, continue pipeline
      if (approved) {
        const continueResponse = await pipelineApi.continuePipeline(run.pipeline_run_id)

        // Check if preprocessing succeeded
        if (!continueResponse.success) {
          throw new Error(continueResponse.message || 'Pipeline continuation failed')
        }
      }

      // Notify parent component
      if (onReviewSubmitted) {
        onReviewSubmitted(approved)
      }
    } catch (err) {
      setError(err.message || 'Failed to submit review')
      console.error('Error submitting review:', err)
    } finally {
      setSubmitting(false)
    }
  }

  if (!questions || questions.length === 0) {
    return null
  }

  const reviewIteration = run.review_iteration || 0

  // Get learning paradigm and question count by preprocessing step
  const learning_paradigm = run.learning_paradigm || 'supervised'
  const questionCountByStep = run.question_count_by_step || {}

  // Determine preprocessing steps based on learning paradigm
  const preprocessingSteps = learning_paradigm === 'unsupervised'
    ? ['clean_outliers', 'handle_missing', 'encode_features', 'scale_features']
    : ['clean_data', 'handle_missing', 'encode_features', 'scale_features']

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg border-2 border-yellow-300 mb-6">
      {/* Algorithm Context Banner (Agent 1A) */}
      <div className="mb-6 p-6 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg shadow-lg">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-2xl font-bold flex items-center gap-2">
            🤖 Algorithm Category Detected
          </h3>
          {reviewIteration > 0 && (
            <span className="px-3 py-1 bg-white text-blue-600 rounded-full text-sm font-semibold">
              Iteration {reviewIteration + 1}
            </span>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-sm opacity-90 mb-1">Learning Paradigm</div>
            <div className="text-2xl font-bold">
              {learning_paradigm.replace(/_/g, ' ').toUpperCase()}
              <span className="ml-2 text-base">
                {learning_paradigm === 'supervised' ? '🎯' : '🔍'}
              </span>
            </div>
          </div>
          <div>
            <div className="text-sm opacity-90 mb-1">Algorithm Category</div>
            <div className="text-2xl font-bold">{algorithmCategory.replace(/_/g, ' ').toUpperCase()}</div>
          </div>
          <div>
            <div className="text-sm opacity-90 mb-1">Confidence</div>
            <div className="text-2xl font-bold">{(algorithmConfidence * 100).toFixed(1)}%</div>
          </div>
        </div>

        {recommendedAlgorithms && recommendedAlgorithms.length > 0 && (
          <div className="mt-4 pt-4 border-t border-white/30">
            <div className="text-sm opacity-90 mb-2">Recommended Algorithms</div>
            <div className="flex flex-wrap gap-2">
              {recommendedAlgorithms.map((algo, idx) => (
                <span key={idx} className="px-3 py-1 bg-white/20 rounded-full text-sm font-medium">
                  {algo}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="mt-4 p-3 bg-white/10 rounded text-sm">
          💡 <strong>Agent 1A analyzed your dataset</strong> and predicted the optimal algorithm category. The questions below are tailored to this prediction.
        </div>
      </div>

      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold flex items-center gap-2">
          <span className="text-2xl">⚠️</span> Algorithm-Aware Configuration Review
        </h3>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('wizard')}
            className={`px-3 py-1 rounded text-sm font-medium ${
              viewMode === 'wizard' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            Wizard
          </button>
          <button
            onClick={() => setViewMode('overview')}
            className={`px-3 py-1 rounded text-sm font-medium ${
              viewMode === 'overview' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
            }`}
          >
            Overview
          </button>
        </div>
      </div>

      {/* Question Distribution by Step */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div className="text-sm font-semibold mb-3">Questions by Preprocessing Step</div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {preprocessingSteps.map(step => {
            const count = questionCountByStep[step] || 0
            return (
              <div key={step} className="text-center p-2 bg-white rounded border border-gray-200">
                <div className="text-xs text-gray-600 mb-1">{step.replace(/_/g, ' ')}</div>
                <div className="text-lg font-bold text-blue-600">{count}</div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Wizard Mode */}
      {viewMode === 'wizard' && (
        <>
          {/* Progress Indicator */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">Question {currentQuestionIndex + 1} of {questions.length}</span>
              <span className="text-xs text-gray-500">
                {allQuestionsAnswered ? '✓ All answered' : `${Object.keys(answers).length} answered`}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
              />
            </div>
          </div>

          {/* Current Question */}
          {currentQuestion && (
            <div className="mb-6 p-6 bg-gray-50 rounded-lg border-2 border-gray-300">
              {/* Header with Priority and Step */}
              <div className="flex items-center justify-between mb-4">
                <span className={`px-3 py-1 rounded text-xs font-semibold ${
                  currentQuestion.priority === 'high' ? 'bg-red-100 text-red-800' :
                  currentQuestion.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {currentQuestion.priority?.toUpperCase()} PRIORITY
                </span>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded text-xs font-semibold">
                  {currentQuestion.preprocessing_step?.replace(/_/g, ' ').toUpperCase()}
                </span>
              </div>

              {/* Question Text */}
              <div className="text-lg font-semibold mb-3">{currentQuestion.question_text}</div>

              {/* Context */}
              {currentQuestion.context && (
                <div className="text-sm text-gray-600 mb-4 italic">
                  💡 {currentQuestion.context}
                </div>
              )}

              {/* Answer Options */}
              <div className="mt-4">
                {/* Multiple Choice with Technique Options */}
                {currentQuestion.question_type === 'multiple_choice' && currentQuestion.options && (
                  <div className="space-y-3">
                    {currentQuestion.options.map((option, idx) => (
                      <div
                        key={idx}
                        onClick={() => handleAnswer(currentQuestion.question_id, option.value, option)}
                        className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                          answers[currentQuestion.question_id] === option.value
                            ? 'border-blue-600 bg-blue-50 shadow-lg'
                            : 'border-gray-200 bg-white hover:border-gray-400'
                        }`}
                      >
                        {/* Option Header */}
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            {answers[currentQuestion.question_id] === option.value && (
                              <span className="text-blue-600 font-bold text-lg">✓</span>
                            )}
                            <span className="font-semibold text-lg">{option.label}</span>
                            {option.recommended && (
                              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-bold rounded">
                                RECOMMENDED
                              </span>
                            )}
                          </div>
                          {option.algorithm_suitability && (
                            <span className={`px-2 py-1 text-xs font-semibold rounded border ${
                              getSuitabilityColor(option.algorithm_suitability)
                            }`}>
                              {option.algorithm_suitability.toUpperCase()}
                            </span>
                          )}
                        </div>

                        {/* Reasoning */}
                        {option.reasoning && (
                          <div className="text-sm text-gray-700 mb-2">
                            {option.reasoning}
                          </div>
                        )}

                        {/* Parameters */}
                        {option.parameters && option.parameters.length > 0 && (
                          <div className="mt-3 p-3 bg-gray-50 rounded text-xs">
                            <div className="font-semibold mb-1">Parameters:</div>
                            <div className="space-y-1">
                              {option.parameters.map((param, pIdx) => (
                                <div key={pIdx} className="flex justify-between">
                                  <span className="text-gray-600">{param.name}:</span>
                                  <span className="font-medium">{JSON.stringify(param.default_value)}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Yes/No Questions */}
                {currentQuestion.question_type === 'yes_no' && (
                  <div className="flex gap-3">
                    <button
                      onClick={() => handleAnswer(currentQuestion.question_id, 'yes')}
                      className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all ${
                        answers[currentQuestion.question_id] === 'yes'
                          ? 'bg-green-600 text-white shadow-lg'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      ✓ Yes
                    </button>
                    <button
                      onClick={() => handleAnswer(currentQuestion.question_id, 'no')}
                      className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all ${
                        answers[currentQuestion.question_id] === 'no'
                          ? 'bg-red-600 text-white shadow-lg'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      ✗ No
                    </button>
                  </div>
                )}

                {/* Text Input */}
                {currentQuestion.question_type === 'text_input' && (
                  <textarea
                    value={answers[currentQuestion.question_id] || ''}
                    onChange={(e) => handleAnswer(currentQuestion.question_id, e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                    rows="4"
                    placeholder="Enter your answer..."
                  />
                )}
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between mb-6">
            <button
              onClick={handlePrevious}
              disabled={currentQuestionIndex === 0}
              className="px-6 py-2 bg-gray-300 hover:bg-gray-400 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-semibold text-gray-800"
            >
              ← Previous
            </button>
            <button
              onClick={handleNext}
              disabled={isLastQuestion}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg font-semibold text-white"
            >
              Next →
            </button>
          </div>
        </>
      )}

      {/* Overview Mode */}
      {viewMode === 'overview' && (
        <div className="mb-6 space-y-4">
          {preprocessingSteps.map(step => {
            const stepQuestions = questions.filter(q => q.preprocessing_step === step)
            if (stepQuestions.length === 0) return null

            return (
              <div key={step} className="border border-gray-300 rounded-lg p-4">
                <h4 className="font-bold text-lg mb-3 capitalize">{step.replace(/_/g, ' ')}</h4>
                <div className="space-y-3">
                  {stepQuestions.map((q, idx) => (
                    <div key={q.question_id} className="p-3 bg-gray-50 rounded">
                      <div className="font-semibold mb-2">{q.question_text}</div>
                      <div className="text-sm">
                        Answer: <span className="font-medium text-blue-600">
                          {answers[q.question_id] || 'Not answered'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Final Review Section (shown when all questions answered) */}
      {allQuestionsAnswered && (
        <div className="border-t-2 border-gray-300 pt-6 mt-6">
          <h4 className="text-lg font-bold mb-4">Final Review</h4>

          {/* Show selected techniques summary */}
          <div className="mb-6 p-4 bg-blue-50 border-2 border-blue-200 rounded-lg">
            <div className="font-semibold mb-3">Selected Preprocessing Techniques:</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {Object.entries(selectedOptions).map(([qId, option]) => {
                const question = questions.find(q => q.question_id === qId)
                if (!question || !option.label) return null

                return (
                  <div key={qId} className="p-2 bg-white rounded border border-blue-200">
                    <div className="text-xs text-gray-600">{question.preprocessing_step?.replace(/_/g, ' ')}</div>
                    <div className="font-medium text-sm">{option.label}</div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Optional Feedback */}
          <div className="mb-6">
            <label className="block text-sm font-semibold mb-2">
              Additional Feedback (Optional)
            </label>
            <textarea
              value={userFeedback}
              onChange={(e) => setUserFeedback(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              rows="3"
              placeholder="Any additional comments or concerns..."
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
              {submitting ? 'Submitting...' : '✓ Approve & Continue Pipeline'}
            </button>
            <button
              onClick={() => handleSubmit(false)}
              disabled={submitting}
              className="flex-1 py-3 px-6 bg-orange-600 hover:bg-orange-700 disabled:opacity-50 text-white font-bold rounded-lg text-lg"
            >
              {submitting ? 'Submitting...' : '🔄 Request Re-Analysis'}
            </button>
          </div>
          <div className="mt-2 text-sm text-gray-600 text-center">
            Note: Approving will execute the selected preprocessing techniques optimized for {algorithmCategory.replace(/_/g, ' ')}
          </div>
        </div>
      )}
    </div>
  )
}

export default ReviewForm
