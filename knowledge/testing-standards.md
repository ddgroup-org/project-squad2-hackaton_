---
title: "Padrões de teste e validação"
description: "Estratégia de testes Salesforce, testes Apex e Jest, testes de Flow, análise estática, gates de qualidade e critérios de aprovação."
category: "knowledge"
status: "active"
version: "1.0"
last_reviewed: "2026-08-05"
owner: "Paulo Carvalho"
tags:
  - salesforce
  - testing
  - quality
  - code-analyzer
  - jest
applies_to:
  - global
source_of_truth: true
source_references:
  - desenvolvimento.md
  - arquitetura.md
  - metaprompt-salesforce.md
---

# Padrões de teste e validação

## Objetivo

Definir a estratégia de testes, os critérios de qualidade e os gates que precisam ser satisfeitos antes de uma entrega ser considerada concluída.

Este documento é a **fonte da verdade** para testes, análise estática e gates de qualidade.

## Escopo

Testes Apex, testes Jest para LWC, testes de Flow, análise estática, validação de deploy, homologação em UAT e validação pós-deploy.

## Princípio central

**Teste comprova comportamento. Cobertura é consequência, nunca objetivo.**

Uma classe com cobertura alta e asserts triviais não prova nada e cria falsa confiança. Um teste que executa o código sem verificar o resultado apenas registra que o código não lançou exceção.

---

## 1. Pirâmide de testes adaptada ao Salesforce

| Nível | O que valida | Onde |
| --- | --- | --- |
| **Unidade** | lógica isolada de uma classe, método ou componente | Apex, Jest |
| **Integração interna** | interação entre automações, triggers, Flows e classes na mesma transação | Apex, Flow Test |
| **Integração externa** | contrato com sistemas externos | mocks nos testes; validação real em ambiente de homologação do parceiro |
| **Regressão** | comportamentos existentes preservados | suíte de testes do projeto + cenários manuais |
| **Segurança** | comportamento por perfil e permissão | Apex com execução sob outro usuário; validação manual |
| **Volume e bulk** | comportamento sob carga | Apex com massa; validação em ambiente com dados representativos |
| **UAT** | aderência à regra de negócio aprovada | manual, com evidências |
| **Pós-deploy** | comportamento confirmado no ambiente de destino | manual, com evidências |

Na plataforma Salesforce, a fronteira entre unidade e integração é naturalmente difusa: qualquer DML aciona automações reais do objeto. Isso é vantagem — o teste exercita o comportamento real — e exige atenção, porque a falha pode vir de uma automação que não é objeto do teste.

---

## 2. Testes Apex

### 2.1 Requisitos

- criar a própria massa de dados;
- não depender de dados existentes na org;
- `@TestSetup` quando vários métodos compartilharem a mesma massa;
- `Test.startTest()` e `Test.stopTest()` delimitando a operação em teste — isso reinicia os limites e força a conclusão do processamento assíncrono;
- `System.runAs()` para validar comportamento por perfil e permissão;
- mocks para callouts;
- asserts comportamentais com mensagem explicativa;
- **não** usar `SeeAllData=true` como atalho.

### 2.2 Estrutura

```apex
@IsTest
private class ExemploServiceTest {

    @TestSetup
    static void prepararDados() {
        // massa mínima e determinística
    }

    @IsTest
    static void deveProcessarRegistroValido() {
        List<Account> contas = [SELECT Id FROM Account LIMIT 1];

        Test.startTest();
        ExemploService.processar(contas);
        Test.stopTest();

        Account resultado = [SELECT Id, Description FROM Account WHERE Id = :contas[0].Id];
        Assert.areEqual(
            'Processado',
            resultado.Description,
            'A descrição deveria ser atualizada após o processamento.'
        );
    }

    @IsTest
    static void deveLancarErroQuandoEntradaInvalida() {
        Test.startTest();
        try {
            ExemploService.processar(null);
            Assert.fail('Era esperada uma exceção para entrada nula.');
        } catch (IllegalArgumentException e) {
            Assert.isTrue(
                String.isNotBlank(e.getMessage()),
                'A exceção deveria conter mensagem explicativa.'
            );
        }
        Test.stopTest();
    }

    @IsTest
    static void deveProcessarLoteCompleto() {
        List<Account> lote = new List<Account>();
        for (Integer i = 0; i < 200; i++) {
            lote.add(new Account(Name = 'Conta ' + i));
        }
        insert lote;

        Test.startTest();
        ExemploService.processar(lote);
        Test.stopTest();

        Integer processados = [
            SELECT COUNT() FROM Account
            WHERE Id IN :lote AND Description = 'Processado'
        ];
        Assert.areEqual(200, processados, 'Todos os registros do lote deveriam ser processados.');
    }
}
```

### 2.3 Cenários obrigatórios

| Cenário | Verifica |
| --- | --- |
| Positivo | comportamento esperado com dado válido |
| Negativo | tratamento de dado inválido, nulo ou regra não atendida |
| Bulk | comportamento com volume representativo (tipicamente 200) |
| Permissão | comportamento para usuário com e sem acesso |
| Exceção | erro esperado é lançado e tratado |
| Assíncrono | processamento em Queueable, Batch, `@future` ou evento se completa |
| Callout | sucesso, erro e timeout com mock |
| Regressão | comportamento existente preservado |
| Registro relacionado ausente | ausência tratada sem exceção não controlada |

### 2.4 Asserts

```apex
// Fraco — não comprova comportamento
Assert.isNotNull(resultado);

// Forte — comprova o resultado esperado
Assert.areEqual(3, resultado.size(), 'Deveriam ser retornados três registros ativos.');
Assert.areEqual('Aprovado', resultado[0].Status__c, 'O primeiro registro deveria estar aprovado.');
```

Toda asserção deve ter mensagem explicando o que se esperava — quando o teste falhar meses depois, essa mensagem é o que economiza tempo de diagnóstico.

### 2.5 Independência

Testes não podem depender de ordem de execução, de dados preexistentes na org, de configuração específica de um ambiente nem de data ou hora do sistema sem controle explícito. Um teste que passa em DEV e falha na pipeline geralmente viola alguma dessas condições.

---

## 3. Testes Jest para LWC

Componentes com lógica em JavaScript exigem testes Jest.

Cobrir: renderização condicional dos estados de loading, empty, sucesso e erro; interação do usuário; emissão de eventos com o `detail` correto; tratamento de erro de chamadas ao servidor; transformação e formatação de dados; comportamento de acessibilidade que possa ser verificado programaticamente.

Diretrizes:

- isolar o componente com mocks para chamadas Apex e adaptadores `@wire`;
- aguardar a conclusão do ciclo de renderização antes de verificar o DOM;
- verificar comportamento observável, não estrutura interna;
- snapshot isolado não substitui asserção — ele detecta mudança, não comprova correção.

Ver [lwc-standards.md](./lwc-standards.md).

---

## 4. Testes de Flow

Cenários mínimos: caminho positivo; caminho negativo, em que o Flow não deve executar; execução em massa; fault path acionado; recursão; contexto de execução por perfil; regressão nos processos relacionados ao objeto.

Flow Test permite automatizar cenários de Flows acionados por registro. A disponibilidade e os tipos suportados variam por release — quando não houver suporte, registrar plano de teste manual com evidências.

Ver [flow-standards.md](./flow-standards.md).

---

## 5. Análise estática e lint

**Salesforce Code Analyzer** deve ser executado sobre o código criado ou alterado antes da conclusão da entrega. Revisão manual não substitui análise estática: a ferramenta é a evidência de que as regras de qualidade foram seguidas.

- tratar violações críticas e altas antes de declarar conclusão;
- documentar falsos positivos com justificativa — nunca suprimir silenciosamente;
- executar o lint de JavaScript configurado no projeto;
- quando a ferramenta não estiver disponível no ambiente, registrar a limitação, o risco residual e como executá-la posteriormente.

---

## 6. Validação de deploy

Validar antes de aplicar, sempre que o ambiente permitir. A validação executa a verificação completa sem persistir a alteração, o que antecipa falhas de dependência, de teste e de metadata.

```bash
sf project deploy validate \
  --manifest {MANIFEST_PATH} \
  --target-org {UAT_ORG_ALIAS} \
  --test-level RunSpecifiedTests \
  --tests {TEST_CLASS_NAME}
```

O nível de teste exigido varia por ambiente e por política do projeto. Confirmar na configuração da pipeline. Ver [retrieve-and-deploy-policy.md](./retrieve-and-deploy-policy.md).

---

## 7. Cobertura

A plataforma exige um percentual mínimo de cobertura para implantar código em ambientes produtivos. Esse número é um piso operacional, não um critério de qualidade.

- cobertura alta com asserts fracos é pior que cobertura média com asserts fortes, porque cria confiança injustificada;
- não escrever teste com o único objetivo de aumentar percentual;
- não excluir código do cálculo para atingir o mínimo;
- avaliar o que **não** está coberto: caminhos de erro e cenários de exceção costumam ser as lacunas mais relevantes.

> Confirmar o percentual mínimo exigido e as regras de cálculo na documentação oficial correspondente à release do projeto.

---

## 8. Estratégia de massa de dados

- massa criada pelo próprio teste, mínima e determinística;
- factory ou classe utilitária de dados de teste quando o projeto já tiver esse padrão — reduz duplicação e centraliza ajustes quando campos obrigatórios mudam;
- respeitar campos obrigatórios, Validation Rules e automações do objeto;
- para testes de volume, gerar registros programaticamente, sem depender de carga externa;
- **nunca** usar dados reais de produção, dados pessoais ou informação confidencial em testes;
- quando o teste depender de configuração específica da org (Custom Metadata, Custom Setting, Record Type), tratar essa dependência explicitamente e registrar a limitação quando não for possível criá-la no teste.

---

## 9. Gates de qualidade

Uma implementação não está concluída porque os arquivos foram criados.

### 9.1 Gates comuns

- [ ] Escopo atendido integralmente.
- [ ] Apenas os arquivos previstos foram alterados.
- [ ] Segurança avaliada.
- [ ] Erros tratados.
- [ ] Testes criados ou ajustados.
- [ ] Testes **executados**, com resultado real reportado.
- [ ] Análise estática executada e apontamentos relevantes tratados.
- [ ] Documentação atualizada no projeto.
- [ ] Rollback definido.
- [ ] Dependências mapeadas.
- [ ] Compatibilidade de API Version verificada.
- [ ] Resultado de deploy ou validação registrado.
- [ ] Evidências reunidas.

### 9.2 Apex

- [ ] Cenários positivo, negativo e bulk.
- [ ] Segurança e exceções testadas.
- [ ] Processamento assíncrono validado.
- [ ] Mocks de callout implementados.
- [ ] Sem SOQL ou DML em laço.
- [ ] Sharing, CRUD e FLS revisados.
- [ ] Code Analyzer executado.

### 9.3 LWC

- [ ] Testes Jest presentes e executados.
- [ ] Estados de loading, empty, sucesso e erro tratados.
- [ ] Acessibilidade e navegação por teclado verificadas.
- [ ] Segurança validada no backend.
- [ ] Performance avaliada.
- [ ] Apex relacionado revisado.

### 9.4 Flow

- [ ] Critérios de entrada validados.
- [ ] Testes positivo e negativo executados.
- [ ] Comportamento em massa validado.
- [ ] Fault paths verificados.
- [ ] Recursão e Order of Execution analisadas.
- [ ] Contexto de execução e segurança revisados.
- [ ] Versão ativada confirmada no ambiente de destino.

---

## 10. Quando uma validação não puder ser executada

Registrar explicitamente:

1. **qual** validação não foi executada;
2. **por que** não foi executada;
3. **qual risco** permanece;
4. **como** executá-la posteriormente;
5. **quem** deve validar.

Não usar "pronto", "validado" ou "funcionando" sem evidência compatível. Uma entrega com validação pendente declarada é profissional; uma entrega com validação pendente omitida é defeito de processo.

---

## 11. Homologação em UAT

O plano de teste entregue para homologação deve conter, por cenário: identificador, descrição, perfil ou usuário utilizado, pré-condição, massa de dados necessária, passos de execução, resultado esperado e evidência recomendada.

| Cenário | Pré-condição | Passos | Resultado esperado | Evidência |
| --- | --- | --- | --- | --- |
| Positivo | massa disponível e usuário autorizado | executar a ação prevista | ação concluída com sucesso | print da tela ou log |
| Negativo | usuário sem permissão ou dado inválido | executar ação restrita | sistema bloqueia e informa adequadamente | print da mensagem |
| Regressão | funcionalidade relacionada disponível | executar processo relacionado | processo permanece funcional | evidência de execução completa |

---

## 12. Validação pós-deploy

Após o deploy em Produção, confirmar com evidências: execução dos cenários críticos; configurações manuais previstas aplicadas; automações ativadas na versão correta; permissões atribuídas; integrações operando; ausência de erros novos no período de monitoramento definido.

Registrar o resultado no projeto. Deploy sem validação pós-deploy é entrega incompleta.

---

## 13. Critérios de aprovação

Uma entrega está apta a seguir quando:

- os critérios de aceite foram transformados em cenários verificáveis e testados;
- os testes automatizados foram executados com resultado real registrado;
- a análise estática não apresenta violação crítica ou alta pendente sem justificativa;
- a segurança foi revisada;
- riscos residuais e limitações estão declarados;
- o plano de rollback existe e é executável;
- as evidências estão reunidas e são verificáveis por outra pessoa.

---

## Referências cruzadas

- [apex-standards.md](./apex-standards.md) · [lwc-standards.md](./lwc-standards.md) · [flow-standards.md](./flow-standards.md) · [security-standards.md](./security-standards.md) · [integration-standards.md](./integration-standards.md) · [retrieve-and-deploy-policy.md](./retrieve-and-deploy-policy.md)

## Fontes oficiais recomendadas

Apex Developer Guide (capítulo de testes); Lightning Web Components Developer Guide (testes Jest); documentação oficial de Flow Test; Salesforce Code Analyzer Documentation; Salesforce CLI Reference; Salesforce Help para requisitos de cobertura em implantação.

## Limitações

Requisitos de cobertura, comportamento de `Test.startTest`/`Test.stopTest` em cenários assíncronos, suporte do Flow Test e regras do Code Analyzer variam por release. Confirmar na documentação oficial correspondente à API Version do projeto.

## Critérios de revisão

Revisar a cada release com mudança em testes ou cobertura, ao adotar nova ferramenta de qualidade na pipeline e quando o projeto redefinir seus critérios de aceite padrão.
