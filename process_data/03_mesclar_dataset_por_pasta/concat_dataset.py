import os
import pandas as pd

# Diretório principal
root_dir = r"C:\Users\Mariana Escorcer\Desktop\arkfindly-main (2)\arkfindly-main\arkfindly-main\data\01_raw\info_books.csv"

# Lista para acumular os dados de todas as subpastas
all_data = []

# Percorre todas as subpastas e arquivos CSV
for root, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith(".csv"):
            file_path = os.path.join(root, file)
            
            # Lê o arquivo CSV
            try:
                df = pd.read_csv(file_path)
                all_data.append(df)  # Adiciona o DataFrame à lista
            except Exception as e:
                print(f"Erro ao processar {file_path}: {e}")

# Concatena todos os DataFrames em um único
if all_data:
    combined_data = pd.concat(all_data, ignore_index=True)
    
    # Salva o arquivo consolidado
    output_path = os.path.join(root_dir, "dados_consolidados_infobooks.csv")
    combined_data.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Dados consolidados salvos em {output_path}")
else:
    print("Nenhum dado encontrado para consolidar.")
