# from webdriver_manager.chrome import ChromeDriverManager
import tempfile
import time

import pandas as pandas
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Cria um diretório temporário único para o user-data-dir
user_data_dir = tempfile.mkdtemp()

# Configurações do Chrome
chrome_options = Options()
chrome_options.add_argument(f"--user-data-dir={user_data_dir}")  # Define um diretório único
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--headless")  # Modo sem interface gráfica
chrome_options.add_argument("--disable-gpu")  # Necessário para alguns sistemas
chrome_options.add_argument("--no-sandbox")  # Para evitar problemas em alguns ambientes
chrome_options.add_argument("--disable-dev-shm-usage")  # Melhor uso de memória
# chrome_options.add_argument("--window-size=1920,1080")

url_base = "https://reate.cprm.gov.br/arquivos/index.php/s/UIgVZobfQwyLeA1"

df_categorias = pandas.read_excel("todos_pocos_por_categoria.xlsx", index_col=0)

links_direcionais = []
for categoria_text, categoria_content in df_categorias.items():
    for url in categoria_content:
        if not pandas.isnull(url):
            driver = webdriver.Chrome(options=chrome_options)
            # driver.minimize_window()

            driver.get(url)

            time.sleep(1)
            links = driver.find_elements(By.TAG_NAME, 'a')
            valid_texts = []
            for link in links:
                href = link.get_attribute('href')
                text = link.text.strip()

                if href and text:  # Filtra apenas links válidos
                    valid_texts.append(text)

            for text in valid_texts:
                pasta_direcional = ""
                if text == "Dados Direcionais":
                    pasta_direcional = "%2FDados%20Direcionais"
                    driver.get(url + pasta_direcional)
                elif text == "Dados_direcionais":
                    pasta_direcional = "%2FDados_direcionais"
                    driver.get(url + pasta_direcional)

                if pasta_direcional != "":
                    print("url %s contém Dados Direcionais" % url)
                    time.sleep(1)

                    sublinks = driver.find_elements(By.TAG_NAME, 'a')
                    for sublink in sublinks:
                        subhref = sublink.get_attribute('href')
                        subtext = sublink.text.strip()
                        if subhref and subtext:
                            # print(subtext)
                            if ".txt" in subtext or ".pdf" in subtext or ".las" in subtext:
                                links_direcionais.append(url[:len(url_base)] + "/download" + url[len(url_base):] +
                                                         pasta_direcional + "&files=%s" % subtext)
                                pd_links_direcionais = pandas.Series(links_direcionais)
                                pd_links_direcionais.to_excel("link_direcionais.xlsx")

            driver.quit()
