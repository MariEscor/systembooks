import os
import pandas as pd

def find_csv_files(root_dir):
    csv_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.csv'):
                csv_files.append(os.path.join(dirpath, filename))
    return csv_files

def remove_duplicates_across_files(file_list):
    # Para manter o controle de todas as combinações únicas de links e outras colunas
    unique_entries = set()
    
    for file in file_list:
        df = pd.read_csv(file)
        
        # Cria uma tupla com as colunas que serão verificadas para duplicatas
        initial_length = len(df)
        df['unique_key'] = df[['URL', 'Nome', 'Numero_Resenhas', 'Seguidores', 'Classificacoes_Usuario']].apply(tuple, axis=1)
        
        # Filtra as linhas onde a combinação de colunas já foi vista em arquivos anteriores
        df = df[~df['unique_key'].isin(unique_entries)]
        filtered_length = len(df)
        
        # Atualiza o conjunto de entradas únicas
        unique_entries.update(df['unique_key'])
        
        # Remove a coluna 'unique_key' temporária antes de salvar
        df = df.drop(columns=['unique_key'])
        
        # Salva o DataFrame filtrado de volta no mesmo arquivo
        df.to_csv(file, index=False)
        
        # Print para acompanhamento
        print(f"Processing {file}: Removed {initial_length - filtered_length} duplicate rows")

def main():
    root_dir = r"C:\Users\Mariana Escorcer\Desktop\arkfindly-main (2)\arkfindly-main\arkfindly-main\data\01_raw\info_profile_reviews.csv"
    csv_files = find_csv_files(root_dir)
    remove_duplicates_across_files(csv_files)

if __name__ == "__main__":
    main()
