import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import DigitalizacionDemo from './DigitalizacionDemo.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <DigitalizacionDemo />
  </StrictMode>,
)
