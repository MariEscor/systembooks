import pandas as pd

# Caminhos dos arquivos
caminho_agrupado = r"c:\Users\Mariana Escorcer\Desktop\arquivos concatenados\dataset_agrupado.csv"
caminho_outro_arquivo = r"c:\Users\Mariana Escorcer\Desktop\arquivos concatenados\dados_consolidados_infobooks.csv"
caminho_resultado = "C:/Users/Mariana Escorcer/Desktop/dataset_concatenado.csv"

# Carregar os arquivos CSV
df_agrupado = pd.read_csv(caminho_agrupado)
df_outro = pd.read_csv(caminho_outro_arquivo)

# Concatenar os dados com base na coluna 'url'
df_concatenado = pd.merge(df_agrupado, df_outro, on='URL', how='inner')

# Salvar o resultado em um novo arquivo CSV
df_concatenado.to_csv(caminho_resultado, index=False)

print("Arquivos concatenados e salvos com sucesso.")
