# orcamentobr
Download Official Data on Brazil's Federal Budget

PT-BR: Baixe Dados Oficiais sobre o Orçamento Federal do Brasil

## Description
The `orcamentobr` Python library allows users to download and analyze official data on Brazil's federal budget through the SPARQL endpoint provided by the Integrated Budget and Planning System (SIOP). This library enables access to detailed information on budget allocations and expenditures of the federal government, making it easier to analyze and visualize these data.

PT-BR: A biblioteca `orcamentobr` em Python permite aos usuários baixar e analisar dados oficiais sobre o orçamento federal do Brasil através do endpoint SPARQL fornecido pelo Sistema Integrado de Planejamento e Orçamento (SIOP). Esta biblioteca facilita o acesso a informações detalhadas sobre alocações e despesas orçamentárias do governo federal, tornando mais fácil analisar e visualizar esses dados.

Technical information on the Brazilian federal budget is available (Portuguese only) at the Budget Technical Manual.

PT-BR: Informações técnicas sobre o orçamento federal brasileiro estão disponíveis (apenas em português) no Manual Técnico do Orçamento.

## Installation
```bash
pip install orcamentobr
```

## Usage
Here are some examples of how to use the library functions:

PT-BR: Aqui estão alguns exemplos de como usar as funções da biblioteca:

Main Functions
PT-BR: Funções Principais

### quais_membros / which_members
Lists all members in a Brazilian Federal Budget dimension for a given year.

PT-BR: Lista todos os membros em uma dimensão do orçamento federal brasileiro para um determinado ano.

#### Example of using the quais_membros function
```bash
from orcamentobr import quais_membros
members = quais_membros(2023, dimensao="funcao")
```

### despesa_detalhada / detailed_expenditure
Downloads expenditure data from the Brazilian federal budget.

PT-BR: Baixa dados de despesas do orçamento federal brasileiro.

#### Examples of using the despesa_detalhada function
```bash
from orcamentobr import despesa_detalhada

detailed_expenses_2017 = despesa_detalhada(2017, detalhe_maximo=True)
expenses_fcdf = despesa_detalhada(2020, uo = "73901", valor_ploa = False)
expenses_2023 = despesa_detalhada(exercicio = 2023, resultado_primario = "6")
```

```bash
expenses = despesa_detalhada(
    exercicio = None,
    esfera = False,
    orgao = False,
    uo = False,
    funcao = False,
    sub_funcao = False,
    programa = False,
    acao = False,
    plano_orcamentario = False,
    subtitulo = False,
    categoria_economica = False,
    gnd = False,
    modalidade_aplicacao = False,
    elemento_despesa = False,
    fonte = False,
    id_uso = False,
    resultado_primario = False,
    valor_ploa = True,
    valor_loa = True,
    valor_loa_mais_credito = True,
    valor_empenhado = True,
    valor_liquidado = True,
    valor_pago = True,
    inclui_descricoes = True,
    detalhe_maximo = False,
    ignore_secure_certificate = False,
    timeout = 0,
    print_url = False,
)
```
## References
Read the [Budget Technical Manual][docs] for more information.

PT-BR: Leia o [Manual Técnico do Orçamento][docs] para mais informações.

[docs]: https://www1.siop.planejamento.gov.br/mto/lib/exe/fetch.php/mto2025:mto2025.pdf


## License
This project is licensed under the terms of the GPL (>= 3). See the LICENSE file for more details.

PT-BR: Este projeto está licenciado sob os termos da licença GPL (>= 3). Veja o arquivo LICENSE para mais detalhes.

## Authors
Daniel G. Reiss (author and creator) - ORCID: 0000-0003-1634-760X

Gabriel S. Vera (co-author) - ORCID: 0009-0006-8693-6732

Gustavo José de Guimarães e Souza (contribuitor) - ORCID: 0000-0002-0718-2295

Ministério do Planejamento e Orçamento (co-author and funder)