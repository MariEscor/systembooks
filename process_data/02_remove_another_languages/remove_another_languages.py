import os
import pandas as pd
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException

# Garante consistência na detecção de idiomas
DetectorFactory.seed = 0

def find_csv_files(root_dir):
    """
    Procura arquivos CSV no diretório especificado.
    """
    csv_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.csv'):
                csv_files.append(os.path.join(dirpath, filename))
    return csv_files

def filter_english_comments(file_list, comment_column="Texto_Resenhas"):
    """
    Filtra comentários que estão em inglês nos arquivos CSV fornecidos.
    """
    for file in file_list:
        df = pd.read_csv(file)
        
        if comment_column in df.columns:
            # Detecta e mantém apenas os comentários em inglês
            initial_length = len(df)
            df["is_english"] = df[comment_column].apply(
                lambda x: detect(x) == 'en' if isinstance(x, str) else False
            )
            df = df[df["is_english"]].drop(columns=["is_english"])
            filtered_length = len(df)
            
            # Salva o DataFrame filtrado de volta no mesmo arquivo
            df.to_csv(file, index=False)
            
            print(f"Processing {file}: Removed {initial_length - filtered_length} non-English rows")
        else:
            print(f"Column '{comment_column}' not found in {file}. Skipping...")

def main():
    root_dir = r"C:\Users\Mariana Escorcer\Desktop\arkfindly-main (2)\arkfindly-main\arkfindly-main\data\01_raw\info_profile_reviews.csv"
    csv_files = find_csv_files(root_dir)
    filter_english_comments(csv_files, comment_column="comments")  # Substitua "comments" pelo nome da coluna de comentários, se necessário

if __name__ == "__main__":
    main()
