import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { InspectionProvider } from './context/InspectionContext.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <InspectionProvider>
      <App />
    </InspectionProvider>
  </StrictMode>,
)
