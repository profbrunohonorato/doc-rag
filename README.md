# Doc RAG

Framework open source para consultar documentos com RAG local, fontes rastreáveis e revisão humana. Implementa os módulos tecnológicos do [projeto de pesquisa](PROJETO%20DE%20PESQUISA.pdf) e segue a organização do `joe`: Python/FastAPI, SQLAlchemy/PostgreSQL, React/Vite/Material UI e camadas `Domain`, `Application`, `Infra` e `Presentation`. O índice usa ChromaDB e os modelos usam Ollama.

## Baixar, apontar os arquivos e executar

Requisitos: Docker Engine com Compose v2, acesso à internet na primeira execução e espaço para imagens e modelos (reserve pelo menos 15 GB). Para os modelos padrão, recomenda-se uma máquina com 8 GB de RAM disponíveis; CPU funciona, com maior latência. GPU é opcional e requer configuração própria do Ollama.

Na raiz do projeto:

```bash
cp .env.example .env
# Edite DOCUMENTS_PATH no .env: caminho absoluto da sua pasta de arquivos.
docker compose up -d --build
```

Acesse **http://localhost:8080**. Sem configurar nada, a base inicial contém o exemplo fictício da Cooperativa Aurora. Pergunte: “Quais documentos preciso para abrir uma conta?”.

O Compose prepara PostgreSQL, Ollama, baixa o modelo de geração e o modelo de embeddings e inicia a indexação automática. A primeira execução pode levar vários minutos e baixar vários GB. Acompanhe:

```bash
docker compose logs -f models api
docker compose ps -a
```

Depois do download, os modelos ficam em volume persistente. Não é necessária chave de API de provedor externo. Os documentos e as consultas são processados nos serviços locais. As bibliotecas e os modelos possuem suas próprias licenças.

## Uso

1. Aponte `DOCUMENTS_PATH` para uma pasta ou envie arquivos em **Base de conhecimento**.
2. Confira se o estado passou para **Indexado**. A pasta é verificada a cada 30 segundos; “Verificar pasta agora” antecipa a leitura.
3. Faça perguntas em **Consultar documentos** e expanda as fontes para ver os trechos e sua localização.
4. Em **Revisão humana**, identifique o revisor e aprove ou rejeite os rascunhos. O histórico registra o estado e a API mantém os eventos de auditoria.

Formatos: PDF com camada de texto, DOCX (parágrafos e tabelas), TXT, Markdown, CSV com cabeçalho e JSON. Textos devem usar UTF-8. Limite padrão: 20 MB por arquivo. PDF digitalizado sem texto precisa de OCR externo. A localização é página para PDFs e bloco 1 para os demais formatos.

Arquivos novos e alterados são processados automaticamente. Arquivos sem alteração não geram embeddings novamente. Remover um arquivo da pasta remove seus trechos do índice na próxima varredura; o registro permanece marcado como removido. Para remover um upload, exclua-o do volume `uploads`. O arquivo original montado em `source` é somente leitura. Documentos de subpastas são incluídos; links simbólicos externos são ignorados.

## Configuração

| Variável no `.env` do Compose | Padrão | Uso |
| --- | --- | --- |
| `DOCUMENTS_PATH` | `./examples/documents` | Pasta de origem no host |
| `CHAT_MODEL` | `qwen2.5:3b` | Modelo de geração no Ollama |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Modelo de embeddings |
| `REQUIRE_REVIEW` | `true` | Respostas recebem estado pendente |
| `API_TOKEN` | vazio | Quando definido, exige Bearer token em todos os endpoints de dados |
| `POSTGRES_PASSWORD` | `doc_rag_local` | Credencial interna de desenvolvimento |

Após editar, rode `docker compose up -d`. Para trocar modelos e executar o download novamente: `docker compose up -d --force-recreate models api`. A troca do modelo de embeddings usa outra coleção e invalida o checksum de ingestão. Aguarde a reindexação antes de consultar. Não altere o conteúdo de um modelo mantendo o mesmo nome sem reconstruir o índice.

Configurações adicionais da API estão em `Presentation/API/settings.py`, incluindo `SCAN_INTERVAL`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `MAX_FILE_BYTES`, `MIN_SIMILARITY` e `CORS_ORIGINS`. Para usar no Compose, adicione-as ao bloco `api.environment`. A similaridade é um critério de recuperação, não uma probabilidade de correção.

## Desenvolvimento

Python 3.12 e Node 20.19+ ou 22.12+. Em desenvolvimento, SQLite dispensa PostgreSQL; a distribuição Docker usa PostgreSQL, como o `joe`.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r Presentation/API/requirements.lock.txt
pip install -r requirements-dev.txt
# Com Ollama instalado e executando localmente:
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
uvicorn Presentation.API.main:app --host 127.0.0.1 --port 9090
```

Em outro terminal:

```bash
cd Presentation/GUI
npm ci
npm run dev
```

Abra http://localhost:5173. O Vite encaminha a API para a porta 9090. `VITE_API_BASE_URL` permite alterar a URL no build da interface. A pasta local padrão é `examples/documents`; uploads locais ficam na subpasta `_uploads`.

Indexação pela linha de comando: `.venv/bin/python scripts/ingest.py /caminho/dos/documentos`. Use a mesma configuração de banco, modelos e índice da API. Execute a CLI com o servidor parado: esta versão suporta um único processo escritor do índice.

## Verificação e avaliação

```bash
.venv/bin/python -m pytest -q
cd Presentation/GUI
npm run lint
npm run build
```

Os testes usam banco SQLite temporário, Chroma real e um provedor de IA determinístico; não baixam modelos e não medem a qualidade do LLM. A CI verifica adicionalmente PostgreSQL e a construção das imagens.

Com o Compose em execução, na raiz:

```bash
.venv/bin/python scripts/evaluate.py --output data/evaluation.json
```

O conjunto demonstrativo mede precisão e recall por **documento recuperado** e latência da consulta. Usa nomes com prefixo `source/`, conforme a montagem do Compose. Adapte o JSON para seu acervo (no desenvolvimento local os nomes não têm esse prefixo). A avaliação cria consultas reais e rascunhos na fila de revisão. Factualidade, alucinação e usabilidade exigem anotação humana e um conjunto de avaliação representativo; estes três exemplos não são validação científica.

Veja [arquitetura e limites](docs/architecture.md), [operação](docs/operations.md) e [contribuição](CONTRIBUTING.md). Licença MIT para o código deste repositório.
