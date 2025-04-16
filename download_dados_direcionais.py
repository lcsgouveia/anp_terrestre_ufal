import os
import re

import pandas as pd
import requests


def baixar_arquivos_da_planilha(caminho_planilha, coluna_links, pasta_destino="dados_direcionais"):
    """
    Baixa arquivos a partir de uma planilha Excel contendo links para download.

    Parâmetros:
        caminho_planilha (str): Caminho da planilha Excel.
        coluna_links (str): Nome da coluna que contém os links para download.
        pasta_destino (str): Nome da pasta onde os arquivos serão salvos.
    """
    # Ler a planilha Excel
    df = pd.read_excel(caminho_planilha)

    # Verificar se a coluna de links existe
    if coluna_links not in df.columns:
        raise ValueError(f"A coluna '{coluna_links}' não foi encontrada na planilha.")

    # Criar a pasta de destino, se não existir
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)

    # Iterar sobre os links e baixar os arquivos
    for index, row in df.iterrows():
        url = row[coluna_links]

        try:
            response = requests.get(url)
            response.raise_for_status()  # Verifica se o download foi bem-sucedido

            content_disposition = response.headers["Content-Disposition"]
            # Extrair o nome do arquivo usando regex
            nome_arquivo = re.findall("filename=(.+)", content_disposition)[0].strip('"')
            caminho_arquivo = os.path.join(pasta_destino, nome_arquivo)

            # Salvar o arquivo
            with open(caminho_arquivo, "wb") as file:
                file.write(response.content)
            print(f"{nome_arquivo} salvo em {caminho_arquivo}")
        except Exception as e:
            print(f"Erro ao baixar {url}: {e}")

# Exemplo de uso
caminho_planilha = "link_direcionais.xlsx"  # Substitua pelo caminho da sua planilha
coluna_links = 0  # Substitua pelo nome da coluna que contém os links
baixar_arquivos_da_planilha(caminho_planilha, coluna_links)

