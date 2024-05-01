import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './app/index.jsx'
import './css/index.css'
import AuthProvider from './components/auth/index.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>,
)