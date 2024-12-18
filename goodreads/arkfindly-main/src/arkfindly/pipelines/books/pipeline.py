"""
This is a boilerplate pipeline 'books'
generated using Kedro 0.19.6
"""

from kedro.pipeline import Pipeline, node, pipeline

from .nodes import (extrair_titulo_da_url, extract_book_urls, extrair_url_imagem, 
                    extrair_titulo, extrair_autor,extrair_sinopse, extrair_generos, extrair_paginas, 
                    extrair_informacoes_publicacao, extrair_nota, extrair_classificacao, 
                    extrair_resenhas, extrair_isbn, extrair_dados_livro, extrair_texto_resenhas, extrair_notas_total, extrair_likes, extrair_classificacoes, 
                    extrair_informacoes_perfil, extrair_dados_resenhas, abrir_url, clicar_com_espera)


def create_pipeline(**kwargs):

    pipe_url_books = Pipeline(
        [
            node(
                func=extract_book_urls,
                inputs=["params:param_url_books.base_url"],
                outputs="url_books",
                name="extract_book_urls_node"
            )
        ]
    )
    pipe_info_books = Pipeline(
        [
            node(
            func=extrair_dados_livro,
            inputs=["url_books"],
            outputs="info_books",
            name="extrair_dados_livro_node"
            )
        ]
    )

    pipe_profile_reviews_book = Pipeline(
        [
            node(
                func=extrair_dados_resenhas,
                inputs=["url_books"],
                outputs="profile_books",
                name="extrair_dados_resenhas_node"
            )
        ],
    )
    return pipe_url_books + pipe_info_books + pipe_profile_reviews_book
