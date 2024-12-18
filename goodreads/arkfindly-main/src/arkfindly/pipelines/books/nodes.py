import requests
import re
import pandas as pd
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
    TimeoutException
)

''' Funções para capturar URLs de livros '''
def extrair_titulo_da_url(url: str) -> str:
    ultima_parte = url.rstrip('/').split('/')[-1]
    if '.' in ultima_parte:
        titulo = ultima_parte.split('.', 1)[-1]
    else:
        titulo = ultima_parte
    titulo_formatado = titulo.replace('_', ' ')
    return titulo_formatado

def extract_book_urls(base_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    page_num = 1
    urls = []  

    titulo_base = extrair_titulo_da_url(base_url)
    print(f"Título extraído da URL base: {titulo_base}")

    while True:
        url = f"{base_url}?page={page_num}" 
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print(f"Sucesso na página {page_num}!")
            soup = BeautifulSoup(response.content, 'html.parser')
            a_tags = soup.find_all('a', class_='bookTitle') 

            if not a_tags:
                print("Nenhum título de livro encontrado.")
                break

            extracted_urls = ['https://www.goodreads.com' + a_tag['href'] for a_tag in a_tags]
            urls.extend(extracted_urls)
        else:
            print(f"Falha ao recuperar a página {page_num}. Status code: {response.status_code}")
            break

        if page_num == 1:
            break

        page_num += 1
        
    df_urls = pd.DataFrame(urls, columns=['URL'])
    df_urls['Base_Title'] = titulo_base  
    # Verifique se o DataFrame não está vazio
    if df_urls.empty:
        print("DataFrame vazio, nenhum URL de livro foi extraído.")
    else:
        print(f"{len(df_urls)} URLs de livros extraídos.")

    return df_urls



''' Funções para extrair informações dos livros '''
def extrair_url_imagem(soup, classe_da_imagem):
    img_element = soup.find('img', class_=classe_da_imagem)
    if img_element:
        img_url = img_element['src']
        print("URL da imagem:", img_url)
        return img_url
    else:
        print("Nenhuma imagem encontrada.")
        return None
    
def extrair_titulo(soup, classe_do_titulo):
    title_element = soup.find('h1', class_=classe_do_titulo)
    if title_element:
        title = title_element.text.strip()
        print("Título:", title)
        return title
    else:
        print("Nenhum título encontrado.")
        return None
    
def extrair_autor(soup, classe_do_autor):
    author_element = soup.find('span', class_=classe_do_autor)
    if author_element:
        author = author_element.text.strip()
        print("Autor:", author)
        return author
    else:
        print("Nenhum autor encontrado.")
        return None
    
def extrair_generos(soup, classe_lista, classe_item, palavra_remover="...more"):
    collapsible_list = soup.find('ul', class_=classe_lista)
    if collapsible_list:
        genre_elements = collapsible_list.find_all(class_=classe_item)
        genres = [element.text.strip() for element in genre_elements]
        genres_without_word = [genre for genre in genres if palavra_remover not in genre]
        genres_string = ", ".join(genres_without_word)
        return genres_string
    else:
        return ""

def extrair_paginas(soup, classe_detalhes, atributo):
    detailspage = soup.find('div', class_=classe_detalhes)
    if detailspage:
        pagenumber_elements = detailspage.find_all(attrs={"data-testid": atributo})
        pages = [element.text.strip() for element in pagenumber_elements]
        pages_string = ", ".join(pages)
        return pages_string
    else:
        return ""
    
def extrair_informacoes_publicacao(soup, classe_detalhes, atributo):
    publication = soup.find('div', class_=classe_detalhes)
    if publication:
        publi_elements = publication.find_all(attrs={"data-testid": atributo})
        publicacoes = [element.text.strip() for element in publi_elements]
        publicacoes_string = ", ".join(publicacoes)
        return publicacoes_string
    else:
        return ""
    
def extrair_sinopse(soup, classe_detalhes):
    sinopse_section = soup.find('div', class_=classe_detalhes)
    if sinopse_section:
        sinopse_element = sinopse_section.find('span', class_='Formatted')
        if sinopse_element:
            sinopse = sinopse_element.text.strip()
            return sinopse
    else:
        return ""


def extrair_nota(soup, classe_nota):
    nota_element = soup.find('div', class_=classe_nota)
    if nota_element:
        nota = nota_element.text.strip()  
        return nota
    else:
        return None
    
def extrair_classificacao(soup, classe_conteiner):
    classificacoes = set()  
    rating_containers = soup.find_all('div', class_=classe_conteiner)

    if rating_containers:
        for container in rating_containers:
            aria_label = container.get('aria-label', '')
            if aria_label:
                classificacao = aria_label.split('ratings')[0].strip()
                classificacoes.add(classificacao)  
    return list(classificacoes)  

def extrair_resenhas(soup, classe_resenhas, atributo):
    reviews = []
    review_container = soup.find('div', class_=classe_resenhas)
    if review_container:
        all_reviews = review_container.find_all(attrs={"data-testid": atributo})
        reviews = [element.text.replace('\xa0', ' ').strip() for element in all_reviews]
        reviews_string = "\n".join(reviews)
        return reviews_string
    else:
        return ""

def extrair_isbn(soup):
    # Padrão regex para capturar ISBN-10 ou ISBN-13
    isbn_pattern = r'\b(?:ISBN(?:-1[03])?:?\s*)?(\d{9}[\dXx]|\d{13})\b'

    # Busca por todas as divs ou spans que possam conter o ISBN no texto
    possible_containers = soup.find_all(text=re.compile(isbn_pattern))

    for container in possible_containers:
        match = re.search(isbn_pattern, container)
        if match:
            isbn = match.group(1)
            print(f"ISBN encontrado: {isbn}")
            return isbn
    
    print("ISBN não encontrado.")
    return "não encontrado"


def extrair_dados_livro(df_urls: pd.DataFrame) -> pd.DataFrame:
    dados = []

    for index, linha in df_urls.iterrows():
        url = linha['URL']  

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        titulo = extrair_titulo(soup, 'Text Text__title1')
        imagem = extrair_url_imagem(soup, 'ResponsiveImage')
        autor = extrair_autor(soup, 'ContributorLink__name')
        generos = extrair_generos(soup, 'CollapsableList', 'Button__labelItem')
        paginas = extrair_paginas(soup, 'FeaturedDetails', 'pagesFormat')
        sinopse = extrair_sinopse(soup,'DetailsLayoutRightParagraph')
        publicacao = extrair_informacoes_publicacao(soup, 'FeaturedDetails', 'publicationInfo')
        nota = extrair_nota(soup, 'RatingStatistics__rating')
        classificacoes = extrair_classificacao(soup, 'RatingStatistics__meta')
        quantidade_resenhas = extrair_resenhas(soup, 'RatingStatistics__meta', 'reviewsCount')
        isbn = extrair_isbn(soup)

        # Append the extracted data to the list
        dados.append({
            'URL': url,
            'Titulo': titulo,
            'Imagem': imagem,
            'Autor': autor,
            'Generos': generos,
            'Paginas': paginas,
            'Sinopse': sinopse,
            'Publicacao': publicacao,
            'Nota': nota,
            'Quantidade_Avaliacoes': ", ".join(classificacoes),
            'Quantidade_Resenhas': quantidade_resenhas,
            'ISBN': isbn
        })


    # Create a DataFrame from the extracted data
    df_resultado = pd.DataFrame(dados, columns=[
        'URL', 'Titulo', 'Imagem', 'Autor', 'Generos', 'Paginas', 'Sinopse',
        'Publicacao', 'Nota', 'Quantidade_Avaliacoes', 'Quantidade_Resenhas', 'ISBN'
    ])
    
    
    return df_resultado


'''Funções para extrair informações de perfis no Goodreads '''
def extrair_texto_resenhas(soup, classe_resenhas):
    texto_resenhas = []
    sections = soup.find_all('section', class_=classe_resenhas)
    
    if sections:
        for section in sections:
            # Remove tags HTML e substitui quebras de linha por espaços
            text = re.sub('<[^>]+?>', '', str(section)).strip()
            text = text.replace('\n', ' ')  # Substitui as quebras de linha por espaços
            if text.endswith("Show more"):
                text = text.rsplit("Show more", 1)[0].strip()
            texto_resenhas.append(text)
            print(texto_resenhas)
    
    return texto_resenhas


def extrair_likes(soup):
    like_buttons = soup.find_all('button', class_='Button Button--inline Button--medium Button--subdued')
    
    likes = []
    for like_button in like_buttons:
        span_likes = like_button.find('span', class_='Button__labelItem')
        if span_likes:
            like_text = span_likes.text.strip()
            if "likes" in like_text.lower(): 
                likes.append(like_text)
    
    return likes

def extrair_notas_total(soup):
    classificacoes = {}
    for i in range(5, 0, -1):  # Loop de 5 a 1 para as estrelas
        rating_bar = soup.find('div', {'data-testid': f'ratingBar-{i}'})
        if rating_bar:
            label_total = rating_bar.find('div', {'data-testid': f'labelTotal-{i}'})
            if label_total:
                classificacao = label_total.get_text().strip()  # Ex: "15,133 (28%)"
                classificacoes[f'{i} estrelas'] = classificacao  # Armazena o valor com a chave como '5 estrelas'
    
    return classificacoes


def extrair_classificacoes(soup, classe_conteiner, classe_rating):
    classificacoes = []
    rating_containers = soup.find_all('div', class_=classe_conteiner)
    if rating_containers:
        for container in rating_containers:
            rating_element = container.find('span', class_=classe_rating)
            if rating_element and rating_element.has_attr('aria-label'):
                classificacao = rating_element['aria-label']
                classificacoes.append(classificacao)
    return classificacoes

def extrair_informacoes_perfil(soup, classe_perfil):
    perfis = []
    profile_info_list = soup.find_all('section', class_=classe_perfil)
    if profile_info_list:
        for profile_info in profile_info_list:
            name_div = profile_info.find('div', class_='ReviewerProfile__name')
            name = name_div.text.strip() if name_div else "Nome não encontrado"
            meta_div = profile_info.find('div', class_='ReviewerProfile__meta')
            if meta_div:
                reviews_span = meta_div.find('span')
                num_reviews = reviews_span.text.split()[0] if reviews_span else "Número de resenhas não encontrado"
                follower_spans = meta_div.find_all('span')
                followers = follower_spans[1].text.split()[0] if len(follower_spans) >= 2 else "Seguidores não encontrados"
            else:
                num_reviews = "Número de resenhas não encontrado"
                followers = "Seguidores não encontrados"
            perfis.append({
                'Nome': name,
                'Numero_Resenhas': num_reviews,
                'Seguidores': followers
            })
    return perfis

def clicar_com_espera(driver, xpath):
    try:
        element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        driver.execute_script("arguments[0].click();", element)
    except (ElementClickInterceptedException, TimeoutException, NoSuchElementException) as e:
        print(f"Erro ao tentar encontrar ou clicar no botão: {e}")

def abrir_url(url):
    chrome_driver_path = r'C:\Users\mresc\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'
    service = Service(executable_path=chrome_driver_path)
    options = Options()
    options.add_argument('--headless') 
    options.add_argument('--disable-gpu')  

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    return driver


def extrair_dados_resenhas(df_urls: pd.DataFrame) -> pd.DataFrame:
    dados = []

    for index, linha in df_urls.iterrows():
        url = linha['URL']
        url_completa = url + "/reviews?reviewFilters"
        print(f"Abrindo URL: {url_completa}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        try:
            response = requests.get(url_completa, headers=headers)
            response.raise_for_status()  
            soup = BeautifulSoup(response.text, 'html.parser')

            notas_totais = extrair_notas_total(soup)
            texto_resenhas = extrair_texto_resenhas(soup, 'ReviewText')
            classificacoes_usuario = extrair_classificacoes(soup, 'ShelfStatus', 'RatingStars RatingStars__small')
            perfil_info = extrair_informacoes_perfil(soup, 'ReviewerProfile__info')
            likes = extrair_likes(soup)  

            limite = 30
            texto_resenhas = texto_resenhas[:limite]
            classificacoes_usuario = classificacoes_usuario[:limite]
            likes = likes[:limite]
            perfil_info = perfil_info[:limite]

            max_len = max(len(texto_resenhas), len(classificacoes_usuario), len(perfil_info), len(likes))
            for i in range(max_len):
                dados.append({
                    'URL': url,
                    'Notas_Totais': notas_totais,
                    'Nome': perfil_info[i]['Nome'] if i < len(perfil_info) else '',
                    'Numero_Resenhas': perfil_info[i]['Numero_Resenhas'] if i < len(perfil_info) else '',
                    'Seguidores': perfil_info[i]['Seguidores'] if i < len(perfil_info) else '',
                    'Classificacoes_Usuario': classificacoes_usuario[i] if i < len(classificacoes_usuario) else '',
                    'Likes': likes[i] if i < len(likes) else '',
                    'Texto_Resenhas': texto_resenhas[i] if i < len(texto_resenhas) else ''
                })

        except requests.exceptions.RequestException as e:
            print(f"Erro ao processar a URL {url_completa}: {e}")

    df_resultado = pd.DataFrame(dados, columns=[
        'URL', 'Notas_Totais', 'Nome', 'Numero_Resenhas', 'Seguidores', 'Classificacoes_Usuario', 'Likes', 'Texto_Resenhas'
    ])

    return df_resultado