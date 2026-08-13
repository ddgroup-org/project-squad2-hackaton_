@isTest
private class ConcentracaoReceitaServiceTest {

    @isTest
    static void deveSinalizarVendedorEContaAcimaDoLimite() {
        Account contaConcentrada = new Account(Name = '[TESTE] Conta Concentrada', TipoPessoa__c = 'PJ');
        Account contaPequena = new Account(Name = '[TESTE] Conta Pequena', TipoPessoa__c = 'PJ');
        insert new List<Account>{ contaConcentrada, contaPequena };

        // 70% do volume total em uma unica conta/oportunidade -> deve ser sinalizada (> 40%)
        Opportunity oppGrande = new Opportunity(
            Name = '[TESTE] Opp Concentrada',
            AccountId = contaConcentrada.Id,
            StageName = 'Closed Won',
            CloseDate = Date.today(),
            Amount = 700
        );
        // 30% restante distribuido em outra conta -> nao deve ser sinalizada
        Opportunity oppPequena = new Opportunity(
            Name = '[TESTE] Opp Pequena',
            AccountId = contaPequena.Id,
            StageName = 'Closed Won',
            CloseDate = Date.today(),
            Amount = 300
        );
        insert new List<Opportunity>{ oppGrande, oppPequena };

        Test.startTest();
        List<ConcentracaoResultado> resultados = ConcentracaoReceitaService.verificarConcentracao();
        Test.stopTest();

        Boolean encontrouContaConcentrada = false;
        Boolean encontrouContaPequena = false;
        Boolean encontrouVendedor = false;
        for (ConcentracaoResultado r : resultados) {
            if (r.tipo == 'Conta' && r.nome == contaConcentrada.Name) {
                encontrouContaConcentrada = true;
                System.assert(r.percentual > 40, 'Percentual deveria ser > 40%, foi: ' + r.percentual);
            }
            if (r.tipo == 'Conta' && r.nome == contaPequena.Name) {
                encontrouContaPequena = true;
            }
            if (r.tipo == 'Vendedor') {
                encontrouVendedor = true;
            }
        }
        System.assert(encontrouContaConcentrada, 'A conta com 70% da receita deveria ter sido sinalizada.');
        System.assert(!encontrouContaPequena, 'A conta com 30% da receita NAO deveria ter sido sinalizada.');
        // as duas oportunidades tem o mesmo Owner (usuario de teste) somando 100% -> vendedor tambem e sinalizado
        System.assert(encontrouVendedor, 'O vendedor unico dono de 100% da receita deveria ter sido sinalizado.');
    }

    @isTest
    static void naoDeveSinalizarQuandoDistribuicaoEquilibrada() {
        Account contaA = new Account(Name = '[TESTE] Conta A', TipoPessoa__c = 'PJ');
        Account contaB = new Account(Name = '[TESTE] Conta B', TipoPessoa__c = 'PJ');
        Account contaC = new Account(Name = '[TESTE] Conta C', TipoPessoa__c = 'PJ');
        insert new List<Account>{ contaA, contaB, contaC };

        List<Opportunity> opps = new List<Opportunity>{
            new Opportunity(Name = '[TESTE] Opp A', AccountId = contaA.Id, StageName = 'Closed Won', CloseDate = Date.today(), Amount = 340),
            new Opportunity(Name = '[TESTE] Opp B', AccountId = contaB.Id, StageName = 'Closed Won', CloseDate = Date.today(), Amount = 330),
            new Opportunity(Name = '[TESTE] Opp C', AccountId = contaC.Id, StageName = 'Closed Won', CloseDate = Date.today(), Amount = 330)
        };
        insert opps;

        Test.startTest();
        List<ConcentracaoResultado> resultados = ConcentracaoReceitaService.verificarConcentracao();
        Test.stopTest();

        for (ConcentracaoResultado r : resultados) {
            System.assert(r.tipo != 'Conta', 'Nenhuma conta deveria ser sinalizada com distribuicao equilibrada (~33% cada).');
        }
    }

    @isTest
    static void naoDeveFalharSemOportunidadesClosedWon() {
        Test.startTest();
        List<ConcentracaoResultado> resultados = ConcentracaoReceitaService.verificarConcentracao();
        Test.stopTest();
        System.assertEquals(0, resultados.size(), 'Sem receita Closed Won, nao deveria haver concentracao a sinalizar.');
    }
}