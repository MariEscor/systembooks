import pandas as pd

# Carregar o CSV com os dados
caminho_csv = "c:/Users/Mariana Escorcer/Desktop/emotions_predictions/dados_consolidados.csv"
df = pd.read_csv(caminho_csv)

# Lista de emoções a serem somadas
emocoes = [
    'admiration', 'amusement', 'anger', 'annoyance', 'approval', 'caring', 
    'confusion', 'curiosity', 'desire', 'disappointment', 'disapproval', 
    'disgust', 'embarrassment', 'excitement', 'fear', 'gratitude', 'grief', 
    'joy', 'love', 'nervousness', 'optimism', 'pride', 'realization', 'relief', 
    'remorse', 'sadness', 'surprise', 'neutral'
]

# Agrupar os dados pela URL e somar as emoções e as notas totais
df_agrupado = df.groupby('URL', as_index=False).agg({
    'Notas_Totais': 'first',  # Manter a primeira nota total para cada URL
    **{emocoes[i]: 'sum' for i in range(len(emocoes))}  # Somar as emoções
})

# Salvar o resultado em um novo arquivo CSV
novo_caminho = "C:/Users/Mariana Escorcer/Desktop/dataset_agrupado.csv"
df_agrupado.to_csv(novo_caminho, index=False)

print("Resultado agrupado e salvo com sucesso.")
