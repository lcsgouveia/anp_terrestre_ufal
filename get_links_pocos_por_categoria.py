import pandas as pandas
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
import os
import tempfile
import time

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

# Inicia o navegador
# service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(options=chrome_options)

# Abre uma página de exemplo
url_base = "https://reate.cprm.gov.br/arquivos/index.php/s/UIgVZobfQwyLeA1"
url = url_base + "?path=%2FPOCO"
driver.get(url)
# driver.minimize_window()

# Aguarda alguns segundos para garantir que o conteúdo seja carregado
time.sleep(1)

# Encontra todos os elementos <a> (links) na página
links_poco = driver.find_elements(By.TAG_NAME, 'a')

# Exibe os links encontrados
categorias_dict = {}
print(f"Links encontrados na página {url}:")
for link_poco in links_poco:
    href_poco = link_poco.get_attribute('href')
    text_poco = link_poco.text.strip()
    if href_poco and "Categoria" in text_poco:  # Filtra apenas links válidos
        print(f"Texto do link: {text_poco}")
        print(f"URL do link: {href_poco}")
        print("-" * 50)

        categorias_dict[text_poco] = {}
        categorias_dict[text_poco]["link"] = href_poco + '?path=%%2FPOCO%%2F%s' %text_poco

        # link_categoria = href_poco
        # driver.get(link_categoria)
        # time.sleep(5)
        # links_categoria = driver.find_elements(By.TAG_NAME, 'a')
        # driver.quit()
        # for link_codigo in links_categoria:
        #     href_codigo = link_codigo.get_attribute('href')
        #     text_codigo = link_codigo.text.strip()
        #     if href_poco:  # Filtra apenas links válidos
        #         print(f"Texto do link: {text_codigo}")
        #         print(f"URL do link: {href_codigo}")
        #         print("-" * 75)


# Fecha o navegador
driver.quit()


def scroll_ate_o_final(_driver):
    container = _driver.find_element(By.CSS_SELECTOR, "#content-wrapper")

    # Obtém a altura da página
    last_height = _driver.execute_script("return arguments[0].scrollHeight", container)

    while True:
        # Rola a página até o final
        _driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", container)

        # Espera um pouco para o conteúdo carregar
        time.sleep(2)

        # Calcula a nova altura da página após o scroll
        new_height = _driver.execute_script("return arguments[0].scrollHeight", container)

        # Verifica se a altura da página mudou
        if new_height == last_height:
            break  # Se a altura não mudou, significa que chegamos ao final da página
        last_height = new_height


for categoria_text, categoria_content in categorias_dict.items():
    url = categoria_content["link"]
    categoria_content["wells"] = []
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)
    # driver.minimize_window()
    time.sleep(1)

    scroll_ate_o_final(driver)

    links = driver.find_elements(By.TAG_NAME, 'a')
    valid_texts = []
    for link in links:
        href = link.get_attribute('href')
        text = link.text.strip()

        if href and text:  # Filtra apenas links válidos
            valid_texts.append(text)

    for text in valid_texts:
        if text[0] == categoria_text[-1]:
            print(f"Texto do link: {text}")
            print("-" * 75)
            categoria_content["wells"].append(url + '%%2F%s' % text)

        elif "parte" in text:
            driver.get('%s%%2F%s' % (url, text))
            time.sleep(1)

            scroll_ate_o_final(driver)

            sublinks = driver.find_elements(By.TAG_NAME, 'a')

            for sublink in sublinks:
                subhref = sublink.get_attribute('href')
                subtext = sublink.text.strip()

                if subhref and subtext:
                    if subtext[0] == categoria_text[-1]:
                        print(f"Texto do link: {subtext}")
                        print("-" * 75)
                        categoria_content["wells"].append(url + '%%2F%s%%2F%s' % (text, subtext))

            driver.back()

    driver.quit()

df_categorias = pandas.DataFrame([cat["wells"] for key, cat in categorias_dict.items()],
                                 index=categorias_dict.keys()).transpose()
df_categorias.to_excel("todos_pocos_por_categoria.xlsx")
