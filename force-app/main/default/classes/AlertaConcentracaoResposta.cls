/**
 * Resposta simples (tipos primitivos) do ConcentracaoReceitaService, para o Flow nao precisar
 * acessar campos de um tipo Apex-defined dentro de um loop (limitacao encontrada na demanda-11:
 * "The element has an invalid reference to Loop_Resultados.descricao" ao tentar isso).
 * Ver demanda-11.
 */
public class AlertaConcentracaoResposta {x
    @InvocableVariable(label='Há concentração acima do limite?')
    public Boolean temAlerta;

    @InvocableVariable(label='Corpo do E-mail')
    public String corpoEmail;
}