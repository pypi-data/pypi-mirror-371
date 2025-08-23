import urllib.parse
import urllib3
import json
import requests
import pandas as pd
from importlib.resources import files, as_file


def escreve_descritores(
    query,
    esfera,
    orgao,
    uo,
    funcao,
    sub_funcao,
    programa,
    acao,
    subtitulo,
    plano_orcamentario,
    fonte,
    categoria_economica,
    gnd,
    modalidade_aplicacao,
    id_uso,
    resultado_primario,
    elemento_despesa,
    inclui_descricoes,
):
    """Adiciona descritores de dimensão à query SPARQL."""

    if esfera is not False:
        query += " ?codEsfera"
        if inclui_descricoes:
            query += " ?descEsfera"
    if orgao is not False:
        query += " ?codOrgao"
        if inclui_descricoes:
            query += " ?descOrgao"
    if uo is not False:
        query += " ?codUO"
        if inclui_descricoes:
            query += " ?descUO"
    if funcao is not False:
        query += " ?codFuncao"
        if inclui_descricoes:
            query += " ?descFuncao"
    if sub_funcao is not False:
        query += " ?codSubfuncao"
        if inclui_descricoes:
            query += " ?descSubfuncao"
    if programa is not False:
        query += " ?codPrograma"
        if inclui_descricoes:
            query += " ?descPrograma"
    if acao is not False:
        query += " ?codAcao"
        if inclui_descricoes:
            query += " ?descAcao"
    if subtitulo is not False:
        query += " ?codSubtitulo"
        if inclui_descricoes:
            query += " ?descSubtitulo"
    if plano_orcamentario is not False:
        query += " ?codPlanoOrcamentario"
        if inclui_descricoes:
            query += " ?descPlanoOrcamentario"
    if fonte is not False:
        query += " ?codFonte"
        if inclui_descricoes:
            query += " ?descFonte"
    if categoria_economica is not False:
        query += " ?codCategoriaEconomica"
        if inclui_descricoes:
            query += " ?descCategoriaEconomica"
    if gnd is not False:
        query += " ?codGND"
        if inclui_descricoes:
            query += " ?descGND"
    if modalidade_aplicacao is not False:
        query += " ?codModalidadeAplicacao"
        if inclui_descricoes:
            query += " ?descModalidadeAplicacao"
    if id_uso is not False:
        query += " ?codIdUso"
        if inclui_descricoes:
            query += " ?descIdUso"
    if resultado_primario is not False:
        query += " ?codResultadoPrimario"
        if inclui_descricoes:
            query += " ?descResultadoPrimario"
    if elemento_despesa is not False:
        query += " ?codElementoDespesa"
        if inclui_descricoes:
            query += " ?descElementoDespesa"

    return query


def constroi_siop_query_detalhe_anual(
    exercicio,
    esfera,
    orgao,
    uo,
    funcao,
    sub_funcao,
    programa,
    acao,
    plano_orcamentario,
    subtitulo,
    categoria_economica,
    gnd,
    modalidade_aplicacao,
    elemento_despesa,
    fonte,
    id_uso,
    resultado_primario,
    valor_ploa,
    valor_loa,
    valor_loa_mais_credito,
    valor_empenhado,
    valor_liquidado,
    valor_pago,
    inclui_descricoes,
):
    """Constrói query SPARQL detalhada anual."""

    query = "SELECT ?codExercicio"

    query = escreve_descritores(
        query=query,
        esfera=esfera,
        orgao=orgao,
        uo=uo,
        funcao=funcao,
        sub_funcao=sub_funcao,
        programa=programa,
        acao=acao,
        subtitulo=subtitulo,
        plano_orcamentario=plano_orcamentario,
        fonte=fonte,
        categoria_economica=categoria_economica,
        gnd=gnd,
        modalidade_aplicacao=modalidade_aplicacao,
        id_uso=id_uso,
        resultado_primario=resultado_primario,
        elemento_despesa=elemento_despesa,
        inclui_descricoes=inclui_descricoes,
    )

    if valor_ploa:
        query += " (sum(?val1) as ?ploa)"
    if valor_loa:
        query += " (sum(?val2) as ?loa)"
    if valor_loa_mais_credito:
        query += " (sum(?val3) as ?loa_mais_credito)"
    if valor_empenhado:
        query += " (sum(?val4) as ?empenhado)"
    if valor_liquidado:
        query += " (sum(?val5) as ?liquidado)"
    if valor_pago:
        query += " (sum(?val6) as ?pago)"

    query += f" WHERE {{ GRAPH <http://orcamento.dados.gov.br/{exercicio}/> {{"
    query += """
        ?i                     loa:temExercicio      ?exercicio .
        ?exercicio             loa:dataUltimaAtualizacao  ?data .
        ?exercicio             loa:identificador     ?codExercicio ."""


    if esfera is not False:
        query += """
        ?i                     loa:temEsfera         ?esfera .
        ?esfera                loa:codigo            ?codEsfera ."""
        if inclui_descricoes:
            query += " ?esfera                rdfs:label            ?descEsfera ."

    if orgao is not False:
        query += """
        ?UO                    loa:temOrgao          ?orgao .
        ?orgao                 loa:codigo            ?codOrgao ."""
        if inclui_descricoes:
            query += " ?orgao                 rdfs:label            ?descOrgao ."

    if uo is not False:
        query += """
        ?i                     loa:temUnidadeOrcamentaria  ?UO .
        ?UO                    loa:codigo            ?codUO ."""
        if inclui_descricoes:
            query += " ?UO                    rdfs:label            ?descUO ."

    if funcao is not False:
        query += """
        ?i                     loa:temFuncao         ?funcao .
        ?funcao                loa:codigo            ?codFuncao ."""
        if inclui_descricoes:
            query += " ?funcao                rdfs:label            ?descFuncao ."

    if sub_funcao is not False:
        query += """
        ?i                     loa:temSubfuncao      ?sub_funcao .
        ?sub_funcao             loa:codigo            ?codSubfuncao ."""
        if inclui_descricoes:
            query += " ?sub_funcao             rdfs:label            ?descSubfuncao ."

    if programa is not False:
        query += """
        ?i                     loa:temPrograma       ?programa .
        ?programa              loa:codigo            ?codPrograma ."""
        if inclui_descricoes:
            query += " ?programa              rdfs:label            ?descPrograma ."

    if acao is not False:
        query += """
        ?i                     loa:temAcao           ?acao .
        ?acao                  loa:codigo            ?codAcao ."""
        if inclui_descricoes:
            query += " ?acao                  rdfs:label            ?descAcao ."

    if subtitulo is not False:
        query += """
        ?i                     loa:temSubtitulo      ?subtitulo .
        ?subtitulo             loa:codigo            ?codSubtitulo ."""
        if inclui_descricoes:
            query += " ?subtitulo             rdfs:label            ?descSubtitulo ."

    if plano_orcamentario is not False:
        query += """
        ?i                     loa:temPlanoOrcamentario  ?plano_orcamentario .
        ?plano_orcamentario     loa:codigo            ?codPlanoOrcamentario ."""
        if inclui_descricoes:
            query += " ?plano_orcamentario     rdfs:label            ?descPlanoOrcamentario ."

    if fonte is not False:
        query += """
        ?i                     loa:temFonteRecursos  ?fonte .
        ?fonte                 loa:codigo            ?codFonte ."""
        if inclui_descricoes:
            query += " ?fonte                 rdfs:label            ?descFonte ."

    if categoria_economica is not False:
        query += """
        ?i                     loa:temCategoriaEconomica  ?categoria_economica .
        ?categoria_economica    loa:codigo            ?codCategoriaEconomica ."""
        if inclui_descricoes:
            query += " ?categoria_economica    rdfs:label            ?descCategoriaEconomica ."

    if gnd is not False:
        query += """
        ?i                     loa:temGND            ?gnd .
        ?gnd                   loa:codigo            ?codGND ."""
        if inclui_descricoes:
            query += " ?gnd                   rdfs:label            ?descGND ."

    if modalidade_aplicacao is not False:
        query += """
        ?i                     loa:temModalidadeAplicacao  ?modalidade_aplicacao .
        ?modalidade_aplicacao   loa:codigo            ?codModalidadeAplicacao ."""
        if inclui_descricoes:
            query += " ?modalidade_aplicacao   rdfs:label            ?descModalidadeAplicacao ."

    if id_uso is not False:
        query += """
        ?i                     loa:temIdentificadorUso  ?id_uso .
        ?id_uso                 loa:codigo            ?codIdUso ."""
        if inclui_descricoes:
            query += " OPTIONAL  {?id_uso      rdfs:label            ?descIdUso }."

    if resultado_primario is not False:
        query += """
        ?i                     loa:temResultadoPrimario  ?resultado_primario .
        ?resultado_primario     loa:codigo            ?codResultadoPrimario ."""
        if inclui_descricoes:
            query += " OPTIONAL {?resultado_primario rdfs:label ?descResultadoPrimario }."

    if elemento_despesa is not False:
        query += """
        ?i                     loa:temElementoDespesa  ?elemento_despesa .
        ?elemento_despesa       loa:codigo            ?codElementoDespesa ."""
        if inclui_descricoes:
            query += " ?elemento_despesa       rdfs:label            ?descElementoDespesa ."

    # FILTERS
    if isinstance(esfera, str):
        query += f' ?esfera                 loa:codigo "{esfera}" .'
    if isinstance(orgao, str):
        query += f' ?orgao                  loa:codigo "{orgao}" .'
    if type(uo) in (str, int):
        query += f' ?UO                     loa:codigo "{uo}" .'
    if isinstance(funcao, str):
        query += f' ?funcao                 loa:codigo  "{funcao}" .'
    if isinstance(sub_funcao, str):
        query += f' ?sub_funcao              loa:codigo  "{sub_funcao}" .'
    if isinstance(programa, str):
        query += f' ?programa               loa:codigo  "{programa}" .'
    if isinstance(acao, str):
        query += f' ?acao                   loa:codigo  "{acao}" .'
    if isinstance(subtitulo, str):
        query += f' ?subtitulo              loa:codigo  "{subtitulo}" .'
    if isinstance(plano_orcamentario, str):
        query += f' ?plano_orcamentario      loa:codigo  "{plano_orcamentario}" .'
    if isinstance(fonte, str):
        query += f' ?fonte                  loa:codigo  "{fonte}" .'
    if isinstance(categoria_economica, str):
        query += f' ?categoria_economica     loa:codigo  "{categoria_economica}" .'
    if isinstance(gnd, str):
        query += f' ?gnd                    loa:codigo  "{gnd}" .'
    if isinstance(modalidade_aplicacao, str):
        query += f' ?modalidade_aplicacao    loa:codigo  "{modalidade_aplicacao}" .'
    if isinstance(id_uso, str):
        query += f' ?id_uso                  loa:codigo  "{id_uso}" .'
    if type(resultado_primario) in (str, int):
        query += f' ?resultado_primario      loa:codigo  "{resultado_primario}" .'
    if isinstance(elemento_despesa, str):
        query += f' ?elemento_despesa        loa:codigo  "{elemento_despesa}" .'

    # Valores
    if valor_ploa:
        query += " ?i loa:valorProjetoLei      ?val1 ."
    if valor_loa:
        query += " ?i loa:valorDotacaoInicial ?val2 ."
    if valor_loa_mais_credito:
        query += " ?i loa:valorLeiMaisCredito ?val3 ."
    if valor_empenhado:
        query += " ?i loa:valorEmpenhado       ?val4 ."
    if valor_liquidado:
        query += " ?i loa:valorLiquidado       ?val5 ."
    if valor_pago:
        query += " ?i loa:valorPago            ?val6 ."

    query += " } } GROUP BY ?codExercicio"

    query = escreve_descritores(
        query=query,
        esfera=esfera,
        orgao=orgao,
        uo=uo,
        funcao=funcao,
        sub_funcao=sub_funcao,
        programa=programa,
        acao=acao,
        subtitulo=subtitulo,
        plano_orcamentario=plano_orcamentario,
        fonte=fonte,
        categoria_economica=categoria_economica,
        gnd=gnd,
        modalidade_aplicacao=modalidade_aplicacao,
        id_uso=id_uso,
        resultado_primario=resultado_primario,
        elemento_despesa=elemento_despesa,
        inclui_descricoes=inclui_descricoes,
    )

    return query


def constroi_siop_query_dimensoes(exercicio, dimensao):
    """Constroi a query SPARQL para listar membros de uma dimensão específica."""
    dimensoes_df = carregar_dataframe_dimensoes()
    var = dimensoes_df.loc[dimensoes_df['param'] == dimensao, 'var'].iloc[0]

    query = (
        "SELECT ?cod ?desc WHERE { "
        f"GRAPH <http://orcamento.dados.gov.br/{exercicio}/> {{ "
        f"?i loa:{var} ?dimensao . "
        "?dimensao loa:codigo ?cod . "
        "?dimensao rdfs:label ?desc . "
        "} } "
        "GROUP BY ?cod ?desc ORDER BY ?cod"
    )
    return query


def forma_url_siop(query, timeout=0):
    query = ' '.join(query.split())
    query_encoded = urllib.parse.quote(query, safe='')
    url = (
        "https://www1.siop.planejamento.gov.br/sparql/?default-graph-uri=&query="
        + query_encoded
        + "&format=application%2Fsparql-results%2Bjson"
        + f"&timeout={timeout}&debug=on"
    )
    return url


def download_siop(url_completo, ignore_secure_certificate):
    """Baixa dados do SIOP, com ou sem verificação SSL."""

    response = None

    if not ignore_secure_certificate:
        try:
            res = files('orcamentobr.certs') / 'fullchainsiop.pem'
            with as_file(res) as cert_path:
                response = requests.get(url_completo, verify=str(cert_path))

        except requests.exceptions.SSLError as e:
            raise Exception(f"Error using the certificate: {e}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error accessing endpoint with certificate: {e}")
        except FileNotFoundError as e:
            raise Exception(f"Certificate file error: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error during secure request: {e}")
    else:
        try:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.get(url_completo, verify=False)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error accessing endpoint (SSL ignored): {e}")
        except Exception as e:
            raise Exception(f"Unexpected error during insecure request: {e}")

    if response is None:
        raise Exception("Failed to get a response from the URL.")

    if response.status_code != 200:
        conteudo_erro = response.text.split("\n")[0] if response.text else "No error content."
        raise Exception(
            f"Error in downloading from endpoint. Code: {response.status_code}\n"
            f"{conteudo_erro}"
        )

    text_content = response.text.strip()

    if text_content.startswith("{") or text_content.startswith("["):
        try:
            json_data = json.loads(text_content)
            return json_data
        except json.JSONDecodeError as e:
            raise Exception(
                f"Failed to decode JSON: {e}. Content: {text_content[:200]}..."
            )
    else:
        raise Exception(
            f"Response is not JSON or does not start with '{{' or '['. "
            f"Content preview: {text_content[:100]}..."
        )


def json_para_dataframe(json_data):
    """Converte JSON retornado pelo SIOP em DataFrame do pandas."""
    df = pd.DataFrame(
        [
            {k: v['value'] for k, v in item.items()}
            for item in json_data['results']['bindings']
        ]
    )
    return df


def carregar_dataframe_dimensoes():
    dimensoes = pd.DataFrame(
        {
            'param': [
                "exercicio", "esfera", "orgao", "uo", "funcao", "sub_funcao",
                "programa", "acao", "plano_orcamentario", "subtitulo",
                "categoria_economica", "gnd", "modalidade_aplicacao",
                "elemento_despesa", "fonte", "id_uso", "resultado_primario"
            ],
            'var': [
                "temExercicio", "temEsfera", "temOrgao", "temUnidadeOrcamentaria",
                "temFuncao", "temSubfuncao", "temPrograma", "temAcao",
                "temPlanoOrcamentario", "temSubtitulo", "temCategoriaEconomica",
                "temGND", "temModalidadeAplicacao", "temElementoDespesa",
                "temFonteRecursos", "temIdentificadorUso", "temResultadoPrimario"
            ]
        }
    )
    return dimensoes
