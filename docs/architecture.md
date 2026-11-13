# Arquitetura

O `joe` de referência possui runtime determinístico para consultas SQL e experimentos de IA fora do fluxo principal. O Doc RAG reaproveita a stack e os padrões estruturais; o fluxo funcional aqui é RAG sobre documentos.

```text
Domain/
  document_model.py               Entidades SQLAlchemy e eventos de auditoria
  interfaces/                    Contratos de persistência
Application/
  dto/                           Validação de entradas
  helpers/                       Fragmentação de texto
  interfaces/                    Contratos de IA e índice
  services/                      Casos de uso de ingestão e consulta
Infra/
  Data/db_context.py             Conexões e sessões
  Data/repositories/             Repositórios e transações
  External/ai/                   Adaptador HTTP do Ollama
  External/documents/            Extração por formato
  External/vector/               Chroma persistente
  IoC/dependencies_helper.py     Composição e ciclo de vida
Presentation/
  API/controllers/               Rotas FastAPI
  API/settings.py                Configuração por ambiente
  API/security.py                Token de instalação
  GUI/src/features/              Chat, Documents e Review: interface e serviços
  GUI/src/_config/               Cliente Axios
  GUI/src/_assets/styles/        Estilos compartilhados
```

## Fluxo

A API inicia a varredura em thread de trabalho. Cada arquivo recebe ID estável pelo caminho relativo e checksum pelo conteúdo e configuração de fragmentação/embeddings. A extração preserva a página de PDFs e gera trechos sobrepostos. O Ollama produz os embeddings em lotes; o Chroma armazena vetores, texto e metadados. Uma falha invalida os trechos antigos e deixa o documento com erro para nova tentativa. Arquivos que desaparecem são retirados do índice, preservando o registro de auditoria.

A consulta gera um embedding, recupera até seis trechos por similaridade de cosseno e aplica limiar mínimo. O prompt pede uso exclusivo das fontes e citações numeradas. Ausência de evidências ou de números de citação válidos produz abstenção. Resposta, fontes, modelo, latência e evento de auditoria são persistidos na mesma transação antes do retorno. Não existe memória conversacional: cada pergunta é independente e o histórico preserva as consultas.

A revisão permite uma transição de `pending` para `approved` ou `rejected`, com revisor, observação e evento transacional. PostgreSQL bloqueia a linha durante a decisão. Respostas pendentes ficam visíveis como rascunhos na interface de trabalho, nunca marcadas como aprovadas. `REQUIRE_REVIEW=false` usa estado `generated`, distinto de aprovação humana. O serviço de revisão não edita o texto gerado.

## Limites explícitos

- Instalação de um único acervo compartilhado. Token de instalação opcional, sem usuários, papéis, tenants ou controle de acesso por documento. O nome informado no campo de revisão é autodeclarado.
- Uma instância da API e um worker Uvicorn. Um lock local serializa alteração do índice e consulta para evitar leituras intermediárias. Não execute múltiplas réplicas nem a CLI em paralelo com a API. Uma tarefa lenta pode atrasar outras operações; não há fila distribuída.
- SQL e índice vetorial não compartilham uma transação. Após falha/reinício a varredura retoma documentos incompletos. O índice é derivado e reconstruível; não fornece garantias de transação distribuída.
- A auditoria é persistente, mas não imutável: um administrador do banco pode alterá-la. Não há certificação regulatória, anonimização automática, DLP ou integração bancária/Open Finance nesta entrega.
- A checagem das citações valida apenas a presença e os índices. Não prova que a evidência sustenta cada afirmação. Similaridade, instruções de prompt e revisão reduzem riscos, mas não eliminam alucinação nem prompt injection.
- PDF sem texto exige OCR externo. Não extrai imagens, gráficos, macros ou fórmulas de planilhas. Não processa XLSX, URLs ou conectores financeiros.
- Os exemplos financeiros são fictícios. Protótipos de atendimento e consulta documental compartilham o mesmo pipeline; automação de relatórios pode consumir a API, sem um gerador especializado incluído.
- Formação de bolsistas, estudos com operadores e publicações do projeto de pesquisa são atividades de pesquisa externas ao código. O relatório de avaliação não substitui esses estudos.
