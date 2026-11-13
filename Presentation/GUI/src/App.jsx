import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import { useState } from 'react'
import { Button, TextField } from '@mui/material'
import Chat from './features/Chat'
import Documents from './features/Documents'
import Review from './features/Review'
export default function App() {
  const [token, setToken] = useState(sessionStorage.getItem('doc-rag-token') || '')
  const [saved, setSaved] = useState(false)
  return <div className="layout"><aside><NavLink className="brand" to="/chat"><span className="brand-icon">D</span> doc rag<span className="version">/ 0.1</span></NavLink><p className="eyebrow">SEU ACERVO, CONECTADO</p><nav><NavLink to="/chat">01 <span>Consultar documentos</span></NavLink><NavLink to="/documents">02 <span>Base de conhecimento</span></NavLink><NavLink to="/review">03 <span>Revisão humana</span></NavLink></nav><div className="aside-bottom"><span className="local-dot"/> Processamento local<p>Conhecimento rastreável.<br/>Respostas com evidências.</p><details><summary>Token de acesso</summary><TextField size="small" type="password" label="Token" value={token} onChange={e => { setToken(e.target.value); setSaved(false) }} fullWidth/><Button onClick={() => { sessionStorage.setItem('doc-rag-token', token); setSaved(true) }}>{saved ? 'Salvo nesta sessão' : 'Salvar token'}</Button></details></div></aside><main><Routes><Route path="/chat" element={<Chat/>}/><Route path="/documents" element={<Documents/>}/><Route path="/review" element={<Review/>}/><Route path="*" element={<Navigate to="/chat" replace/>}/></Routes></main></div>
}
