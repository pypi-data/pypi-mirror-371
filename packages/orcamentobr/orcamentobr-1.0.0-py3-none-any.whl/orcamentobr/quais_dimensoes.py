from datetime import datetime
from .siop_utils import (
    constroi_siop_query_dimensoes,
    forma_url_siop,
    carregar_dataframe_dimensoes,
    download_siop,
    json_para_dataframe,
)


def quais_membros(
    exercicio: int | None = None,
    dimensao: str | None = None,
    ignore_secure_certificate: bool = False,
):
    """Lista os membros de uma dimensão do Orçamento Federal para um dado ano.

    Parameters
    ----------
    exercicio : int
        O ano a que se refere a extração.
    dimensao : str
        A dimensão do orçamento a ser listada.
        Valores válidos: "Esfera", "Orgao", "UO", "Funcao", etc.
    ignore_secure_certificate : bool, optional
        Se True, o download dos dados do SIOP ignora o certificado de
        segurança. O padrão é False.

    Returns
    -------
    pandas.DataFrame
        Um DataFrame com os membros da dimensão, contendo tanto o código
        quanto a descrição de cada membro.

    Examples
    --------
    >>> # Listar todos os membros da dimensão 'Funcao' para o ano de 2023
    >>> quais_membros(exercicio=2023, dimensao="Funcao")

    >>> # Listar membros de outra dimensão, ignorando o certificado de segurança
    >>> quais_membros(
    ...     exercicio=2024, dimensao="Orgao", ignore_secure_certificate=True
    ... )
    """
    if exercicio is None:
        exercicio = datetime.now().year - 1

    dimensoes_df = carregar_dataframe_dimensoes()

    if not isinstance(dimensao, str):
        raise ValueError(
            "Erro: 'dimensao' deve ser uma string!\n"
            f"Valores válidos: {dimensoes_df['param'][1:17].tolist()}"
        )

    if dimensao not in dimensoes_df['param'][1:17].values:
        raise ValueError(
            "Erro: 'dimensao' não contém um valor válido!\n"
            f"Valores válidos: {', '.join(dimensoes_df['param'][1:17])}"
        )

    query = constroi_siop_query_dimensoes(exercicio=exercicio, dimensao=dimensao)
    url = forma_url_siop(query)
    dados = download_siop(url, ignore_secure_certificate)
    df = json_para_dataframe(dados)
    df.columns = [f"{dimensao}_cod", f"{dimensao}_desc"]

    return df


def which_members(
    exercicio: int | None = None,
    dimensao: str | None = None,
    ignore_secure_certificate: bool = False,
):
    """Lists the members in a Brazilian Federal Budget dimension.

    This function is a wrapper for `quais_membros`, providing an English
    interface.

    Parameters
    ----------
    exercicio : int
        The year to which the extracted data refers.
    dimensao : str
        The budget dimension to be listed.
        Valid values: "Esfera", "Orgao", "UO", "Funcao", etc.
    ignore_secure_certificate : bool, optional
        If True, the SIOP data download ignores the secure certificate.
        Default is False.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the dimension members, including both the
        code and description for each member.

    Examples
    --------
    >>> # List all members of the 'Funcao' dimension for the year 2023
    >>> which_members(exercicio=2023, dimensao="Funcao")

    >>> # List members of another dimension, ignoring the secure certificate
    >>> which_members(
    ...     exercicio=2024, dimensao="Orgao", ignore_secure_certificate=True
    ... )
    """
    return quais_membros(
        exercicio=exercicio,
        dimensao=dimensao,
        ignore_secure_certificate=ignore_secure_certificate,
    )

