/**
 * Wrapper de resultado usado por ConcentracaoReceitaService — classe de nivel superior
 * (nao aninhada) para ser referenciavel diretamente como tipo Apex-defined em variaveis de Flow.
 * Ver demanda-11.
 */
public class ConcentracaoResultado {
    @InvocableVariable(label='Tipo (Vendedor ou Conta)')
    public String tipo;

    @InvocableVariable(label='Nome')
    public String nome;

    @InvocableVariable(label='Percentual da Carteira')
    public Decimal percentual;

    @InvocableVariable(label='Descrição')
    public String descricao;
}