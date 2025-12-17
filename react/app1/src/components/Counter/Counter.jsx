import { useState } from 'react'
import Button from '../Button/Button'
import './Counter.css'

const Counter = () => {
  const [count, setCount] = useState(0)
  const [step, setStep] = useState(1)

  const increment = () => setCount(count + step)
  const decrement = () => setCount(count - step)
  const reset = () => setCount(0)

  return (
    <div className="counter">
      <div className="counter-display">
        <span className="counter-number">{count}</span>
      </div>
      
      <div className="counter-controls">
        <div className="step-control">
          <label htmlFor="step">Step:</label>
          <input
            id="step"
            type="number"
            value={step}
            onChange={(e) => setStep(Number(e.target.value))}
            min="1"
            className="step-input"
          />
        </div>
        
        <div className="counter-buttons">
          <Button variant="danger" onClick={decrement}>
            - {step}
          </Button>
          <Button variant="secondary" onClick={reset}>
            Reset
          </Button>
          <Button variant="success" onClick={increment}>
            + {step}
          </Button>
        </div>
      </div>
    </div>
  )
}

export default Counter