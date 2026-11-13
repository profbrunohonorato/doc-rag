import { useEffect, useState } from 'react'
import { Alert, Button, TextField } from '@mui/material'
import AnswerCard from '../Chat/components/AnswerCard'
import { pending, review } from './service'
import { errorMessage } from '../../_config/axios'
export default function Review() {
  const [items, setItems] = useState([]), [reviewer, setReviewer] = useState(''), [note, setNote] = useState(''), [error, setError] = useState(''), [busy, setBusy] = useState(false)
  async function refresh() { try { setItems(await pending()); setError('') } catch (e) { setError(errorMessage(e)) } }
  useEffect(() => { refresh() }, [])
  async function decide(id, decision) {
    setBusy(true)
    try { await review(id, { decision, reviewer, note }); setNote(''); await refresh() } catch (e) { setError(errorMessage(e)) } finally { setBusy(false) }
  }
  return <><header><span className="eyebrow">SUPERVISÃO HUMANA</span><h1>Confira a evidência.<br/><span>Registre sua decisão.</span></h1><p>A aprovação registra a conferência humana e permanece na trilha de auditoria.</p></header><div className="review-fields"><TextField label="Seu nome" value={reviewer} onChange={e => setReviewer(e.target.value)} slotProps={{ htmlInput: { maxLength: 100 } }}/><TextField label="Observação da revisão" value={note} onChange={e => setNote(e.target.value)} fullWidth slotProps={{ htmlInput: { maxLength: 2000 } }}/><Button onClick={refresh}>Atualizar</Button></div>{error && <Alert severity="error">{error}</Alert>}<div className="section-heading"><h2>Respostas pendentes</h2><span>{items.length} nesta página</span></div><div className="cards">{items.map(item => <div key={item.id}><AnswerCard item={item}/><div className="review-actions"><Button disabled={busy || reviewer.trim().length < 2} color="error" onClick={() => decide(item.id, 'rejected')}>Rejeitar</Button><Button disabled={busy || reviewer.trim().length < 2} variant="contained" onClick={() => decide(item.id, 'approved')}>Aprovar resposta</Button></div></div>)}</div>{!items.length && <div className="empty">Nenhuma resposta aguardando revisão.</div>}</>
}
