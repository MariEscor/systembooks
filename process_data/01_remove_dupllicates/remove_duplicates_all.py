import os
import pandas as pd

def remove_cross_duplicates(root_dir):
    all_data = []
    csv_paths = []

    # Percorre todas as pastas e subpastas no diretório raiz
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.csv'):
                file_path = os.path.join(dirpath, filename)
                
                # Carrega o CSV em um DataFrame e armazena o caminho
                df = pd.read_csv(file_path)
                all_data.append(df)
                csv_paths.append(file_path)
    
    # Concatena todos os dados para identificar duplicatas globais
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df_dedup = combined_df.drop_duplicates()

    # Divide novamente os dados para salvar em arquivos CSV separados
    start = 0
    for file_path, original_df in zip(csv_paths, all_data):
        # Calcula o tamanho do DataFrame original
        end = start + len(original_df)
        
        # Extrai as linhas deduplicadas correspondentes ao arquivo original
        df_dedup = combined_df_dedup.iloc[start:end]
        
        # Atualiza o índice inicial para o próximo arquivo
        start = end

        # Salva o DataFrame deduplicado no mesmo local
        df_dedup.to_csv(file_path, index=False)
        print(f"Duplicatas removidas entre pastas e CSV salvo: {file_path}")

# Caminho para o diretório raiz que contém as pastas
root_directory = 'C:/Users/Mariana Escorcer/Desktop/arkfindly-main/arkfindly-main/data/01_raw'
remove_cross_duplicates(root_directory)
