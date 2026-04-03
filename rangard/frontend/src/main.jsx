import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#161b22',
            color: '#c9d1d9',
            border: '1px solid #30363d',
            borderRadius: '10px',
            fontSize: '14px',
          },
        }}
      />
    </BrowserRouter>
  </React.StrictMode>
)