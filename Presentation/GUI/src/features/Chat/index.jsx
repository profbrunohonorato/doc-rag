import { useEffect, useState } from 'react'
import { Alert, Button, CircularProgress, TextField } from '@mui/material'
import { ask, history } from './service'
import { errorMessage } from '../../_config/axios'
import AnswerCard from './components/AnswerCard'
export default function Chat() {
  const [question, setQuestion] = useState(''), [items, setItems] = useState([]), [busy, setBusy] = useState(false), [error, setError] = useState(''), [more, setMore] = useState(false)
  useEffect(() => { history().then(data => { setItems(data); setMore(data.length === 100) }).catch(e => setError(errorMessage(e))) }, [])
  async function submit(e) {
    e.preventDefault(); if (!question.trim()) return
    setBusy(true); setError('')
    try { const result = await ask(question.trim()); setItems(old => [result, ...old]); setQuestion('') } catch (e) { setError(errorMessage(e)) } finally { setBusy(false) }
  }
  async function loadMore() { try { const data = await history(items.length); setItems(old => [...old, ...data]); setMore(data.length === 100) } catch (e) { setError(errorMessage(e)) } }
  return <><header><span className="eyebrow">ESPAÇO DE CONSULTA</span><h1>Uma pergunta.<br/><span>O conhecimento da sua base.</span></h1><p>Explore seus documentos e confira a origem de cada resposta.</p></header><form className="question-form" onSubmit={submit}><TextField label="O que você quer saber?" placeholder="Ex.: Quais são os requisitos para abrir uma conta?" multiline minRows={3} fullWidth value={question} onChange={e => setQuestion(e.target.value)} slotProps={{ htmlInput: { maxLength: 2000 } }}/><div className="form-footer"><small>Respostas baseadas nos documentos indexados</small><Button type="submit" variant="contained" disabled={busy || question.trim().length < 3}>{busy ? <><CircularProgress size={16} color="inherit"/> Consultando…</> : 'Consultar a base →'}</Button></div></form>{error && <Alert severity="error" onClose={() => setError('')}>{error}</Alert>}<div className="section-heading"><h2>Suas consultas</h2><span>Fontes sempre à vista</span></div>{!items.length && !busy && <div className="empty"><h3>Comece pelo que você já sabe.</h3><p>Adicione arquivos em Base de conhecimento e faça sua primeira pergunta.</p></div>}<div className="cards">{items.map(item => <AnswerCard key={item.id} item={item}/>)}</div>{more && <Button onClick={loadMore}>Carregar consultas anteriores</Button>}</>
}
