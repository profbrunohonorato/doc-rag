import { useEffect, useState } from 'react'
import { Alert, Button, Chip, LinearProgress, Paper } from '@mui/material'
import { list, scan, upload } from './service'
import { errorMessage } from '../../_config/axios'
const labels = { indexed: 'Indexado', indexing: 'Processando', error: 'Falha', removed: 'Removido', pending: 'Aguardando' }
export default function Documents() {
  const [items, setItems] = useState([]), [busy, setBusy] = useState(false), [error, setError] = useState(''), [message, setMessage] = useState('')
  useEffect(() => { let mounted = true; const refresh = () => list().then(data => { if (mounted) setItems(data) }).catch(e => { if (mounted) setError(errorMessage(e)) }); refresh(); const timer = setInterval(refresh, 5000); return () => { mounted = false; clearInterval(timer) } }, [])
  async function process(files) {
    setBusy(true); setError(''); setMessage('')
    try { for (const file of files) await upload(file); setItems(await scan()); setMessage('Verificação concluída. Confira o estado de cada arquivo abaixo.') } catch (e) { setError(errorMessage(e)) } finally { setBusy(false) }
  }
  return <><header><span className="eyebrow">BASE DE CONHECIMENTO</span><h1>Seus arquivos.<br/><span>Prontos para conversar.</span></h1><p>A pasta configurada é verificada automaticamente a cada 30 segundos.</p></header><Paper variant="outlined" className="upload"><span className="upload-icon">↑</span><h2>Amplie sua base</h2><p>PDF com texto, DOCX, TXT, Markdown, CSV e JSON. Até 20 MB por arquivo.</p><Button variant="contained" component="label" disabled={busy}>Selecionar arquivos<input hidden type="file" multiple accept=".pdf,.docx,.txt,.md,.csv,.json" onChange={e => { process([...e.target.files]); e.target.value = '' }}/></Button><Button disabled={busy} onClick={() => process([])}>Verificar pasta agora</Button></Paper>{busy && <LinearProgress/>}{error && <Alert severity="error">{error}</Alert>}{message && <Alert severity="info">{message}</Alert>}<div className="section-heading"><h2>Documentos</h2><span>{items.filter(x => x.status === 'indexed').length} indexados</span></div><div className="cards">{items.map(item => <Paper variant="outlined" key={item.id} className="document-row"><div><strong>{item.name}</strong><p className="muted">{item.chunks} trechos · {new Date(item.updated_at).toLocaleString('pt-BR')}</p>{item.error && <p role="alert">{item.error}</p>}</div><Chip size="small" label={labels[item.status]} color={item.status === 'indexed' ? 'success' : item.status === 'error' ? 'error' : 'default'}/></Paper>)}</div>{!items.length && <div className="empty">Adicione arquivos ou aponte DOCUMENTS_PATH para uma pasta com documentos.</div>}</>
}
