/**
 * Calcula a concentração de receita (Opportunity Closed Won) por Vendedor (Owner) e por Conta,
 * sinalizando quando algum ultrapassa o limite de risco (40% do volume total da carteira,
 * ver business-scenario.md/BRD 4.1). Chamado por um Scheduled Flow (Amostra... nao, Alerta_Concentracao_Receita)
 * porque o Flow nao suporta agregacao SOQL (SUM ... GROUP BY) de forma declarativa
 * (ver architecture.md: "1) config declarativa -> 2) Flow -> 3) Approval Process -> 4) Apex/LWC
 * so se 1-3 forem comprovadamente insuficientes" — este e exatamente esse caso).
 * Ver demanda-11.
 */
public with sharing class ConcentracaoReceitaService {

    public static final Decimal LIMITE_PERCENTUAL = 40;

    /**
     * Ponto de entrada chamado pelo Flow Alerta_Concentracao_Receita — retorna um único objeto
     * com tipos primitivos (Boolean/String), já que o Flow não suporta acessar campos de um tipo
     * Apex-defined dentro de um loop (erro encontrado: "invalid reference to Loop_Resultados.descricao").
     */
    @InvocableMethod(label='Preparar Alerta de Concentração de Receita' description='Monta o corpo do e-mail de alerta quando algum vendedor/conta ultrapassa 40% do volume total de Opportunities Closed Won.')
    public static List<AlertaConcentracaoResposta> prepararAlertaConcentracao() {
        List<ConcentracaoResultado> resultados = verificarConcentracao();
        AlertaConcentracaoResposta resp = new AlertaConcentracaoResposta();
        resp.temAlerta = !resultados.isEmpty();
        String corpo = '';
        for (ConcentracaoResultado r : resultados) {
            corpo += r.descricao + '\n';
        }
        resp.corpoEmail = corpo;
        return new List<AlertaConcentracaoResposta>{ resp };
    }

    public static List<ConcentracaoResultado> verificarConcentracao() {
        List<ConcentracaoResultado> resultados = new List<ConcentracaoResultado>();

        List<AggregateResult> totalGeral = [
            SELECT SUM(Amount) total
            FROM Opportunity
            WHERE StageName = 'Closed Won'
        ];
        Decimal total = (totalGeral.isEmpty() || totalGeral[0].get('total') == null)
            ? 0
            : (Decimal) totalGeral[0].get('total');

        if (total <= 0) {
            return resultados;
        }

        for (AggregateResult ar : [
            SELECT OwnerId, Owner.Name ownerName, SUM(Amount) soma
            FROM Opportunity
            WHERE StageName = 'Closed Won'
            GROUP BY OwnerId, Owner.Name
        ]) {
            Decimal soma = (Decimal) ar.get('soma');
            Decimal percentual = (soma / total) * 100;
            if (percentual > LIMITE_PERCENTUAL) {
                ConcentracaoResultado r = new ConcentracaoResultado();
                r.tipo = 'Vendedor';
                r.nome = (String) ar.get('ownerName');
                r.percentual = percentual.setScale(1);
                r.descricao = 'Vendedor ' + r.nome + ' concentra ' + r.percentual + '% da receita da carteira (limite: ' + LIMITE_PERCENTUAL + '%).';
                resultados.add(r);
            }
        }

        for (AggregateResult ar : [
            SELECT AccountId, Account.Name accountName, SUM(Amount) soma
            FROM Opportunity
            WHERE StageName = 'Closed Won' AND AccountId != null
            GROUP BY AccountId, Account.Name
        ]) {
            Decimal soma = (Decimal) ar.get('soma');
            Decimal percentual = (soma / total) * 100;
            if (percentual > LIMITE_PERCENTUAL) {
                ConcentracaoResultado r = new ConcentracaoResultado();
                r.tipo = 'Conta';
                r.nome = (String) ar.get('accountName');
                r.percentual = percentual.setScale(1);
                r.descricao = 'Conta ' + r.nome + ' concentra ' + r.percentual + '% da receita da carteira (limite: ' + LIMITE_PERCENTUAL + '%).';
                resultados.add(r);
            }
        }

        return resultados;
    }
}