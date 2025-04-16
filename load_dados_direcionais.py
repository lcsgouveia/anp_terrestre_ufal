import os
import pandas as pd
import re
import chardet

def detect_encoding(filename):
    try:
        with open(filename, 'rb') as f:
            raw_data = f.read(10000)  # Read a sample
        return chardet.detect(raw_data)['encoding']
    except Exception as e:
        print(f"Erro ao detectar codificação do arquivo {filename}: {e}")
        return 'utf-8'  # Fallback para UTF-8

class WellDataConverter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None

    def extract_table(self):
        try:
            encoding = detect_encoding(self.file_path)
            with open(self.file_path, 'r', encoding=encoding, errors='replace') as file:
                lines = file.readlines()

            data = []
            capturing = False
            format_type = None  # Para identificar o formato do arquivo

            for line in lines:
                line = line.strip()

                # Verifica o formato do arquivo com base no cabeçalho
                if re.match(r'^PROFUNDIDADE\s+INCLINACAO', line):
                    format_type = "FORMATO_1"
                    capturing = True
                    continue
                elif re.match(r'^Trajet\.\s+Prof\.Med\.\s+\(m\)', line):
                    format_type = "FORMATO_2"
                    capturing = True
                    continue

                # Captura os dados de acordo com o formato detectado
                if capturing:
                    if format_type == "FORMATO_1" and re.match(r'^[\d\.]+\s+[\d\.]+\s+[\d\.]+', line):
                        data.append(re.split(r'\s+', line))
                    elif format_type == "FORMATO_2" and re.match(r'^\w+-\d+\s+[\d\.]+\s+[\d\.]+\s+[\w\d\.]+\s+[\d\.]+', line):
                        data.append(re.split(r'\s+', line))

            # Define as colunas com base no formato detectado
            if format_type == "FORMATO_1":
                columns = [
                    "Profundidade Medida (m)", "Inclinação (graus)", "Profundidade Vertical (m)",
                    "Azimute", "Rumo", "Afastamento N/S (m)", "Afastamento E/W (m)",
                    "Latitude", "Longitude", "UTM Norte (m)", "UTM Leste (m)"
                ]
            elif format_type == "FORMATO_2":
                columns = [
                    "Trajetória", "Profundidade Medida (m)", "Inclinação (graus)", "Direção",
                    "Profundidade Vertical (m)", "Cota (m)", "Afastamento (m)", "Coord. N/S (m)",
                    "Coord. L/W (m)", "UTM Norte (m)", "UTM Leste (m)", "Dog Leg Sev. (?/30m)"
                ]
            else:
                print(f"Formato de arquivo não reconhecido: {self.file_path}")
                return None

            self.df = pd.DataFrame(data, columns=columns)
            return self.df
        except Exception as e:
            print(f"Erro ao extrair tabela do arquivo {self.file_path}: {e}")
            return None

    def save_to_csv(self, output_path):
        if self.df is not None:
            self.df.to_csv(output_path, index=False)
            print(f"Arquivo salvo em {output_path}")
        else:
            print("Nenhuma tabela extraída para salvar.")

def list_txt_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.txt')]

# Diretório onde estão os arquivos
dir_path = "./dados_direcionais/"

# Dicionário para armazenar os DataFrames
df_dict = {}

# Processa todos os arquivos no diretório
list_of_files = list_txt_files(dir_path)

for file_path in list_of_files:
    file_name = os.path.basename(dir_path + file_path)  # Obtém apenas o nome do arquivo
    converter = WellDataConverter(dir_path + file_path)
    df = converter.extract_table()

    if df is not None and df.shape[0] != 0:
        df_dict[file_name] = df  # Armazena no dicionário

        # Salva cada DataFrame extraído em um CSV
        output_csv = os.path.join(dir_path, file_name.replace('.txt', '.csv'))
        df.to_csv(output_csv, index=False)
        print(f"Arquivo CSV salvo em: {output_csv}")

# Exibir os arquivos processados
print("Arquivos processados:", df_dict.keys())