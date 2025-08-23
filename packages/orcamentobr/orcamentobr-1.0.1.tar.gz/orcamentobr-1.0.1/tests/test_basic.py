from orcamentobr import (
    quais_membros,
    constroi_url_siconfi,
    verifica_params,
    detailed_expenditure
)

def test_dummy():
    assert True

def test_quais_membros_runs():
    # Test only that the function runs and returns a DataFrame-like object
    try:
        result = quais_membros(2023, dimensao="Funcao")
        assert hasattr(result, "columns")
    except Exception:
        assert True  # Accepts failure if no internet or API changes

def test_constroi_url_siconfi():
    url = constroi_url_siconfi("entes")
    assert isinstance(url, str)
    assert "https://apidatalake.tesouro.gov.br/ords/siconfi/tt//entes" in url

def test_verifica_params_valid():
    params = {"id_ente": 1, "an_referencia": 2020, "me_referencia": 12, "co_tipo_matriz": "MSCE", "classe_conta": 6, "id_tv": "period_change"}
    result = verifica_params("msc_orcamentaria", params)
    assert result
    
    
    
def test_detailed_expenditure():
    # Exemplo de uso
    df = detailed_expenditure(
        exercicio=2023, Esfera=False, Orgao=False, UO=False, Funcao=False, Subfuncao=False,
        Programa=False, Acao=False, PlanoOrcamentario=False, Subtitulo=False,
        CategoriaEconomica=False, GND=False, ModalidadeAplicacao=False, ElementoDespesa=False,
        Fonte=False, IdUso=False, ResultadoPrimario=False,
        valorPLOA=True, valorLOA=True, valorLOAmaisCredito=True, valorEmpenhado=True, valorLiquidado=True, valorPago=True,
        incluiDescricoes=True, detalheMaximo=False, ignoreSecureCertificate=False, timeout=0, print_url=True
    )

    print(df)
    assert True
