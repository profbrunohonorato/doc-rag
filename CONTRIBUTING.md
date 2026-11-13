# Contribuir

Abra uma issue com o problema, caso mínimo e comportamento esperado, usando dados fictícios. Evite documentos, tokens e credenciais reais. Faça alterações mantendo casos de uso em `Application`, entidades em `Domain`, integrações em `Infra` e interfaces de entrada em `Presentation`.

Para adicionar um formato, implemente a extração e preserve a localização das fontes. Para um novo provedor de IA ou índice, siga os protocolos em `Application/interfaces` e registre o adaptador em `Infra/IoC`. Inclua teste de regressão para mudanças de comportamento e execute pytest, lint e build conforme README.

Atualize os locks de dependência em ambiente limpo ao alterar versões. A licença MIT abrange as contribuições de código; verifique direitos e licenças de documentos, datasets e modelos antes de distribuí-los.
