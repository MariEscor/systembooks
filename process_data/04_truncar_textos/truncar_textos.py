import os
import pandas as pd
import numpy as np
from transformers import pipeline, AutoTokenizer
from sklearn import metrics

# Caminho da pasta que contém os CSVs
input_directory = r"C:\Users\Mariana Escorcer\Desktop\arkfindly-main (2)\arkfindly-main\arkfindly-main\data\01_raw\info_profile_reviews.csv"
# Caminho da pasta onde os resultados serão salvos
output_directory = r"C:\Users\Mariana Escorcer\Desktop\emotions_predictions"

# Criação do pipeline de classificação
classifier = pipeline(task="text-classification", model="SamLowe/roberta-base-go_emotions", top_k=None)
tokenizer = AutoTokenizer.from_pretrained("SamLowe/roberta-base-go_emotions")

# Verifica se o diretório de saída existe; se não, cria
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Percorre todos os arquivos e subpastas no diretório de entrada
for root, dirs, files in os.walk(input_directory):
    for file in files:
        if file.endswith(".csv"):
            dataset_path = os.path.join(root, file)
            df = pd.read_csv(dataset_path)

            print(f"Processando: {dataset_path}")

            # Extrai os textos e remove entradas inválidas
            texts = df["Texto_Resenhas"].tolist()
            texts = [text if isinstance(text, str) else "" for text in texts]  # substitui valores inválidos por string vazia

            # Truncar textos para o limite de 256 tokens
            texts_truncated = []
            for text in texts:
                tokens = tokenizer.encode(text, truncation=True, max_length=256) 
                texts_truncated.append(tokenizer.decode(tokens, skip_special_tokens=True))

            # Classificação dos textos válidos
            model_outputs = classifier(texts_truncated)

            # Prepara os dados de saída
            labels = list(classifier.model.config.id2label.values())
            num_items, num_labels = len(texts), len(labels)
            emotion_probabilities = np.zeros((num_items, num_labels), dtype=float)

            for i, item_probas in enumerate(model_outputs):
                for item_proba in item_probas:
                    label, score = item_proba["label"], item_proba["score"]
                    label_index = labels.index(label)
                    emotion_probabilities[i, label_index] = score

            # Cria o DataFrame de emoções e concatena com os dados originais
            emotion_df = pd.DataFrame(emotion_probabilities, columns=labels)
            emotion_df = pd.concat([df, emotion_df], axis=1)

            # Cria uma subpasta para cada arquivo CSV processado
            subfolder_name = os.path.relpath(root, input_directory).replace("\\", "_") + "_" + os.path.splitext(file)[0]
            output_subfolder = os.path.join(output_directory, subfolder_name)

            if not os.path.exists(output_subfolder):
                os.makedirs(output_subfolder)

            # Salva o resultado
            output_file_path = os.path.join(output_subfolder, f"emotion_predictions_{subfolder_name}.csv")
            emotion_df.to_csv(output_file_path, index=False)

            print(f"Resultados salvos em: {output_file_path}")
