# Operação

## Endpoints

Prefixo: `/doc-rag/api/v1`. OpenAPI disponível em `http://localhost:8080/docs` no Compose e `http://localhost:9090/docs` na execução direta da API.

| Método | Rota | Descrição |
| --- | --- | --- |
| GET | `/health/live` | Processo disponível, sem autenticação |
| GET | `/health/ready` | Verifica banco, índice e presença dos modelos |
| GET | `/documents` | Estado, checksum e falhas por arquivo |
| POST | `/documents/upload` | Multipart `file`, escrita atômica |
| POST | `/documents/scan` | Aguarda verificação da pasta |
| POST | `/chat/ask` | JSON `question`, `top_k` opcional |
| GET | `/answers` | Histórico, filtros `status` e `offset`, páginas de 100 |
| POST | `/answers/{id}/review` | `decision` approved/rejected, `reviewer`, `note` |
| GET | `/audit` | Eventos, `offset`, páginas de 100 |

Exemplo:

```bash
curl http://localhost:8080/doc-rag/api/v1/chat/ask \
  -H 'Content-Type: application/json' \
  -d '{"question":"Como abrir uma conta na Cooperativa Aurora?"}'
```

Se `API_TOKEN` estiver definido, adicione `Authorization: Bearer SEU_TOKEN`. A interface permite salvar o token apenas na sessão da aba. Todos que conhecem esse token acessam todo o acervo, histórico e revisão. Não o inclua em código público.

## Persistência e recuperação

Volumes: `postgres` (metadados, histórico e auditoria), `index` (Chroma), `models` (modelos) e `uploads` (documentos enviados). A pasta externa de origem não é copiada. Faça backup da origem, uploads e PostgreSQL; o índice pode ser reconstruído a partir dos documentos com a configuração original. O histórico retém os trechos recuperados mesmo após remoção do arquivo; isso é intencional para auditoria e precisa entrar na política de retenção da instituição.

`docker compose down` para os serviços e preserva os volumes. `docker compose down -v` apaga todos os volumes, histórico e uploads; use somente ao descartar a instalação. Esta versão inicial cria tabelas automaticamente na inicialização; mudanças futuras de esquema precisam de migrações explícitas antes de atualizações com dados existentes.

## Diagnóstico

- UI indisponível: `docker compose ps -a` e `docker compose logs ui`.
- API aguardando: acompanhe `docker compose logs -f models`; a primeira preparação baixa os modelos. O inicializador tenta novamente em falhas. Depois, confira `docker compose logs api`.
- Documento com erro: confira formato, UTF-8, limite de tamanho e presença de texto. Falhas são isoladas por arquivo e repetidas a cada varredura.
- Pasta vazia: confirme o caminho absoluto em `DOCUMENTS_PATH` e permissões de leitura do usuário UID 10001 do container. Reinicie após alterar o mount.
- Resposta sem evidência: confira a indexação e os trechos. Ajuste modelo ou limiar somente com avaliação em conjunto anotado.

## Implantação fora da máquina local

O Compose publica apenas `127.0.0.1:8080`; banco e Ollama não publicam portas no host. Para compartilhamento em rede, configure TLS/reverse proxy, credenciais próprias, autenticação de usuários e autorização adequada ao seu contexto. A versão atual é destinada a execução local e experimentos controlados, não fornece isolamento entre usuários. Não há promessa de conformidade com LGPD ou normas financeiras.

Os logs identificam requisições e tipos de erro sem imprimir corpo de consultas ou texto extraído. Banco, índice, uploads e histórico contêm texto original. Não há anonimização automática: utilize documentos públicos, fictícios ou previamente anonimizados nos experimentos.
