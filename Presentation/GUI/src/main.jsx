import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { createTheme, CssBaseline, ThemeProvider } from '@mui/material'
import App from './App'
import './_assets/styles/global.css'
const theme = createTheme({ palette: { primary: { main: '#13695e' }, background: { default: '#f4f6f5' } }, typography: { fontFamily: 'Inter, system-ui, sans-serif', button: { textTransform: 'none', fontWeight: 650 } }, shape: { borderRadius: 12 } })
ReactDOM.createRoot(document.getElementById('root')).render(<React.StrictMode><ThemeProvider theme={theme}><CssBaseline/><BrowserRouter><App/></BrowserRouter></ThemeProvider></React.StrictMode>)
