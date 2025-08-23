from datetime import datetime
import pandas as pd

from .siop_utils import (
    forma_url_siop,
    carregar_dataframe_dimensoes,
    download_siop,
    json_para_dataframe,
    constroi_siop_query_detalhe_anual,
)


def despesa_detalhada(
    exercicio: int | None = None,
    esfera: bool | int | str = False,
    orgao: bool | int | str = False,
    uo: bool | int | str = False,
    funcao: bool | int | str = False,
    sub_funcao: bool | int | str = False,
    programa: bool | int | str = False,
    acao: bool | int | str = False,
    plano_orcamentario: bool | int | str = False,
    subtitulo: bool | int | str = False,
    categoria_economica: bool | int | str = False,
    gnd: bool | int | str = False,
    modalidade_aplicacao: bool | int | str = False,
    elemento_despesa: bool | int | str = False,
    fonte: bool | int | str = False,
    id_uso: bool | int | str = False,
    resultado_primario: bool | int | str = False,
    valor_ploa: bool = True,
    valor_loa: bool = True,
    valor_loa_mais_credito: bool = True,
    valor_empenhado: bool = True,
    valor_liquidado: bool = True,
    valor_pago: bool = True,
    inclui_descricoes: bool = True,
    detalhe_maximo: bool = False,
    ignore_secure_certificate: bool = False,
    timeout: int = 0,
    print_url: bool = False,
):
    """
    Download expenditure data from the Brazilian federal budget.

    Queries the SIOP API to retrieve expenditure data for a given fiscal year,
    with options to disaggregate by various qualitative and quantitative
    dimensions and to include selected financial metrics. Dimension parameters
    may be:
    - `bool`: `True` for full breakdown, `False` for aggregation
    - `int` or `str`: a specific code or identifier to filter that dimension

    Parameters
    ----------
    exercicio : int or None, default None
        Fiscal year to query. If None, uses the package’s internal `.last_year()`.
    esfera, orgao, uo, funcao, sub_funcao, programa, acao,
    plano_orcamentario, subtitulo, categoria_economica, gnd,
    modalidade_aplicacao, elemento_despesa, fonte, id_uso,
    resultado_primario : bool, int, or str, optional
        Dimension flags or filters (default False).
        - If `bool`: `True` to break down by this dimension, `False` to aggregate.
        - If `int` or `str`: filter results to the given code only.

        - esfera: Esfera Orçamentária
        - orgao: Órgão
        - uo: Unidade Orçamentária
        - funcao: Função
        - sub_funcao: Subfunção
        - programa: Programa
        - acao: Ação
        - plano_orcamentario: Plano Orçamentário
        - subtitulo: Subtítulo
        - categoria_economica: Categoria Econômica
        - gnd: Grupo Natureza da Despesa
        - modalidade_aplicacao: Modalidade de Aplicação
        - elemento_despesa: Elemento da Despesa
        - fonte: Fonte de Recursos
        - id_uso: Contrapartida (Identificador de uso)
        - resultado_primario: Identificador de resultado primário

    valor_ploa, valor_loa, valor_loa_mais_credito,
    valor_empenhado, valor_liquidado, valor_pago : bool, optional
        Which monetary fields to include (default True).

    inclui_descricoes : bool, optional
        Include descriptive labels for each selected dimension (default True).

    detalhe_maximo : bool, optional
        Override all other flags and disaggregate by all dimensions (default False).

    ignore_secure_certificate : bool, optional
        Skip SSL certificate validation if True (default False).

    timeout : int, optional
        Request timeout in milliseconds (default 0). Values <1000 are ignored.

    print_url : bool, optional
        Print the constructed API URL before request if True (default False).

    Returns
    -------
    pandas.DataFrame
        DataFrame with expenditure figures. Columns depend on flags provided.

    References
    ----------
    Manual Técnico do Orçamento, SIOP:
    https://www1.siop.planejamento.gov.br/mto/lib/exe/fetch.php/mto2025:mto2025.pdf
    """
    if exercicio is None:
        exercicio = datetime.now().year - 1

    args = dict(locals())
    args['exercicio'] = int(args['exercicio'])

    if args['detalhe_maximo']:
        dimensoes_df = carregar_dataframe_dimensoes()
        params = dimensoes_df['param'][1:17]  # dimensões de detalhe
        for param in params:
            args[param] = True

    args_para_query = {
        k: v for k, v in args.items()
        if k not in ['detalhe_maximo', 'ignore_secure_certificate', 'timeout', 'print_url']
    }

    query = constroi_siop_query_detalhe_anual(**args_para_query)
    xurl = forma_url_siop(query, timeout)

    if print_url:
        print(xurl)

    dados = download_siop(xurl, ignore_secure_certificate)
    df = json_para_dataframe(dados)

    # Transform numeric columns
    for col in ['ploa', 'loa', 'loa_mais_credito', 'empenhado', 'liquidado', 'pago']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col])

    # Rename columns
    novos_nomes = []
    for nome in df.columns:
        if nome == "codExercicio":
            novos_nomes.append("exercicio")
        elif nome.startswith("cod"):
            novos_nomes.append(f"{nome[3:]}_cod")
        elif nome.startswith("desc"):
            novos_nomes.append(f"{nome[4:]}_desc")
        else:
            novos_nomes.append(nome)
    df.columns = novos_nomes

    return df


def detailed_expenditure(
    exercicio: int | None = None,
    esfera: bool | int | str = False,
    orgao: bool | int | str = False,
    uo: bool | int | str = False,
    funcao: bool | int | str = False,
    sub_funcao: bool | int | str = False,
    programa: bool | int | str = False,
    acao: bool | int | str = False,
    plano_orcamentario: bool | int | str = False,
    subtitulo: bool | int | str = False,
    categoria_economica: bool | int | str = False,
    gnd: bool | int | str = False,
    modalidade_aplicacao: bool | int | str = False,
    elemento_despesa: bool | int | str = False,
    fonte: bool | int | str = False,
    id_uso: bool | int | str = False,
    resultado_primario: bool | int | str = False,
    valor_ploa: bool = True,
    valor_loa: bool = True,
    valor_loa_mais_credito: bool = True,
    valor_empenhado: bool = True,
    valor_liquidado: bool = True,
    valor_pago: bool = True,
    inclui_descricoes: bool = True,
    detalhe_maximo: bool = False,
    ignore_secure_certificate: bool = False,
    timeout: int = 0,
    print_url: bool = False,
):
    """
    Download expenditure data from the Brazilian federal budget.

    Queries the SIOP API to retrieve expenditure data for a given fiscal year,
    with options to disaggregate by various qualitative and quantitative
    dimensions and to include selected financial metrics. Dimension parameters
    may be:
    - `bool`: `True` for full breakdown, `False` for aggregation
    - `int` or `str`: a specific code or identifier to filter that dimension

    Parameters
    ----------
    exercicio : int or None, default None
        Fiscal year to query. If None, uses the package’s internal `.last_year()`.
    esfera, orgao, uo, funcao, sub_funcao, programa, acao,
    plano_orcamentario, subtitulo, categoria_economica, gnd,
    modalidade_aplicacao, elemento_despesa, fonte, id_uso,
    resultado_primario : bool, int, or str, optional
        Dimension flags or filters (default False).
        - If `bool`: `True` to break down by this dimension, `False` to aggregate.
        - If `int` or `str`: filter results to the given code only.

        - esfera: Esfera Orçamentária
        - orgao: Órgão
        - uo: Unidade Orçamentária
        - funcao: Função
        - sub_funcao: Subfunção
        - programa: Programa
        - acao: Ação
        - plano_orcamentario: Plano Orçamentário
        - subtitulo: Subtítulo
        - categoria_economica: Categoria Econômica
        - gnd: Grupo Natureza da Despesa
        - modalidade_aplicacao: Modalidade de Aplicação
        - elemento_despesa: Elemento da Despesa
        - fonte: Fonte de Recursos
        - id_uso: Contrapartida (Identificador de uso)
        - resultado_primario: Identificador de resultado primário

    valor_ploa, valor_loa, valor_loa_mais_credito,
    valor_empenhado, valor_liquidado, valor_pago : bool, optional
        Which monetary fields to include (default True).

    inclui_descricoes : bool, optional
        Include descriptive labels for each selected dimension (default True).

    detalhe_maximo : bool, optional
        Override all other flags and disaggregate by all dimensions (default False).

    ignore_secure_certificate : bool, optional
        Skip SSL certificate validation if True (default False).

    timeout : int, optional
        Request timeout in milliseconds (default 0). Values <1000 are ignored.

    print_url : bool, optional
        Print the constructed API URL before request if True (default False).

    Returns
    -------
    pandas.DataFrame
        DataFrame with expenditure figures. Columns depend on flags provided.

    References
    ----------
    Manual Técnico do Orçamento, SIOP:
    https://www1.siop.planejamento.gov.br/mto/lib/exe/fetch.php/mto2025:mto2025.pdf
    """
    return despesa_detalhada(
        exercicio=exercicio,
        esfera=esfera,
        orgao=orgao,
        uo=uo,
        funcao=funcao,
        sub_funcao=sub_funcao,
        programa=programa,
        acao=acao,
        plano_orcamentario=plano_orcamentario,
        subtitulo=subtitulo,
        categoria_economica=categoria_economica,
        gnd=gnd,
        modalidade_aplicacao=modalidade_aplicacao,
        elemento_despesa=elemento_despesa,
        fonte=fonte,
        id_uso=id_uso,
        resultado_primario=resultado_primario,
        valor_ploa=valor_ploa,
        valor_loa=valor_loa,
        valor_loa_mais_credito=valor_loa_mais_credito,
        valor_empenhado=valor_empenhado,
        valor_liquidado=valor_liquidado,
        valor_pago=valor_pago,
        inclui_descricoes=inclui_descricoes,
        detalhe_maximo=detalhe_maximo,
        ignore_secure_certificate=ignore_secure_certificate,
        timeout=timeout,
        print_url=print_url,
    )
