# Validação local — 13/11/2026

Verificações realizadas:

- 12 testes pytest aprovados, incluindo banco PostgreSQL real, Chroma persistente, ingestão incremental, invalidação de conteúdo antigo, remoção, extração DOCX/CSV/JSON/PDF, autenticação, limites de upload e revisão com auditoria.
- `npm run lint` e `npm run build` aprovados. Build dividido em bundles de React, Material UI e aplicação.
- `pip check` sem dependências incompatíveis.
- Imagens Docker construídas e serviços executados pelo Compose. Inicializador baixou os dois modelos automaticamente e terminou com código zero.
- `/health/ready` retornou `ok`; exemplo indexado automaticamente.
- Três consultas HTTP reais com `qwen2.5:3b` e `nomic-embed-text` retornaram estado `pending`, fontes e citações. As respostas trataram de documentos para abertura de conta, horário de atendimento e prazo de contestação, de acordo com o exemplo fictício.
- Avaliação demonstrativa: precisão e recall por documento iguais a 1 nas três consultas, com latência média aproximada de 3,9 segundos nessa execução. Há apenas um documento relevante no conjunto; esses resultados verificam o funcionamento e não demonstram qualidade geral de recuperação ou ausência de alucinações.

O navegador integrado não estava disponível na sessão. Não foi realizada inspeção visual nem navegação automatizada da interface. Compilação e lint não substituem essa conferência.

O relatório JSON da avaliação fica em `data/evaluation.json` na máquina de desenvolvimento, ignorado pelo Git. Execute novamente conforme README para medir sua instalação e seu conjunto de documentos.
