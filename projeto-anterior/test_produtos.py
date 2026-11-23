"""PROJETO ANTERIOR - Trabalho 2: produtos-web (Programação para Internet II).

Sistema: front React/Vite (http://localhost:4173) + API Express (http://localhost:3000).
Fluxos cobertos: (1) busca por nome, (2) filtro "só em estoque", e a combinação dos dois,
além do carregamento com fonte de dados e da regra de contingência (API fora -> dados locais).

O sistema é só de leitura (não grava nada), então não há reset de estado: cada teste
abre a página do zero num navegador novo, e a suíte roda em qualquer ordem.
Matriz de casos: matriz_casos_produtos.csv.

    HEADLESS=1 python -m pytest test_produtos.py -v
"""
import json
import urllib.parse
import urllib.request

import pytest

from pages.produtos_page import ProdutosPage

TODOS = ["Maçã", "Pitaya", "Maracujá", "Espinafre", "Abóbora", "Ervilha"]
EM_ESTOQUE = ["Maçã", "Pitaya", "Espinafre", "Ervilha"]
EM_FALTA = {"Maracujá", "Abóbora"}
MSG_VAZIA = "Nenhum produto encontrado. Tente outro nome ou desmarque o filtro de estoque."


@pytest.fixture
def tela(driver, base_url):
    return ProdutosPage(driver, base_url).abrir()


# ------------------------------------------------------------------ carregamento
def test_p01_carrega_catalogo_da_api_agrupado(tela):
    tela.aguardar_quantidade(6)
    assert tela.nomes() == TODOS
    assert tela.categorias() == ["Frutas", "Verduras"]
    assert tela.fonte_dos_dados() == "Dados da API REST."


def test_p02_api_fora_usa_dados_locais(driver, base_url):
    """Contingência: se a API não responde, a tela mostra os dados locais e avisa."""
    driver.execute_cdp_cmd("Network.enable", {})
    driver.execute_cdp_cmd("Network.setBlockedURLs", {"urls": ["*:3000/*"]})
    tela = ProdutosPage(driver, base_url).abrir()
    assert tela.fonte_dos_dados() == "Dados locais."
    assert tela.aguardar_quantidade(6).nomes() == TODOS


# ------------------------------------------------------------------ fluxo 1: busca por nome
@pytest.mark.parametrize("texto, esperado", [
    pytest.param("maçã", ["Maçã"], id="nome_exato"),
    pytest.param("MA", ["Maçã", "Maracujá"], id="parcial_maiusculas"),
    pytest.param("  ervilha  ", ["Ervilha"], id="espacos_nas_pontas"),
    pytest.param("a", ["Maçã", "Pitaya", "Maracujá", "Espinafre", "Abóbora", "Ervilha"], id="uma_letra"),
])
def test_p03_busca_por_nome(tela, texto, esperado):
    tela.buscar(texto).aguardar_quantidade(len(esperado))
    assert tela.nomes() == esperado


def test_p04_busca_sem_resultado_mostra_mensagem(tela):
    tela.buscar("chocolate").aguardar_quantidade(0)
    assert tela.mensagem_vazia() == MSG_VAZIA
    assert tela.nomes() == [] and tela.categorias() == []


def test_p05_categoria_sem_itens_nao_aparece(tela):
    tela.buscar("pitaya").aguardar_quantidade(1)
    assert tela.categorias() == ["Frutas"]


# ------------------------------------------------------------------ fluxo 2: filtro de estoque
def test_p06_so_em_estoque(tela):
    tela.marcar_so_estoque().aguardar_quantidade(4)
    assert tela.nomes() == EM_ESTOQUE
    assert not any(falta for _, _, falta in tela.produtos())


def test_p07_desmarcar_estoque_restaura_lista(tela):
    tela.marcar_so_estoque().aguardar_quantidade(4)
    tela.marcar_so_estoque(False).aguardar_quantidade(6)
    assert tela.nomes() == TODOS


# ------------------------------------------------------------------ regra combinada (tabela de decisão)
@pytest.mark.parametrize("texto, so_estoque, esperado", [
    pytest.param("ma", False, ["Maçã", "Maracujá"], id="busca_sem_filtro"),
    pytest.param("ma", True, ["Maçã"], id="busca_com_filtro"),
    pytest.param("abóbora", True, [], id="so_em_falta_com_filtro"),
])
def test_p08_busca_combinada_com_estoque(tela, texto, so_estoque, esperado):
    tela.buscar(texto).marcar_so_estoque(so_estoque).aguardar_quantidade(len(esperado))
    assert tela.nomes() == esperado
    if not esperado:
        assert tela.mensagem_vazia() == MSG_VAZIA


# ------------------------------------------------------------------ apresentação
def test_p09_em_falta_tem_selo_e_precos_em_reais(tela):
    tela.aguardar_quantidade(6)
    produtos = {nome: (preco, falta) for nome, preco, falta in tela.produtos()}
    assert {n for n, (_, f) in produtos.items() if f} == EM_FALTA
    assert produtos["Maçã"][0] == "R$ 1,00"
    assert produtos["Abóbora"][0] == "R$ 4,00"


# ------------------------------------------------------------------ defeito registrado (API)
@pytest.mark.xfail(strict=True, reason="Defeito D1: a API não apara espaços do parâmetro q, a tela apara")
def test_d01_api_busca_com_espacos_igual_a_tela(api_url):
    """Mesma regra do caso 'espacos_nas_pontas' (P03), conferida direto na API.
    xfail estrito: vira falha (XPASS) quando o defeito for corrigido, lembrando de tirar a marca."""
    url = f"{api_url}/api/products?q=" + urllib.parse.quote("  ervilha  ")
    with urllib.request.urlopen(url, timeout=5) as r:
        nomes = [p["name"] for p in json.loads(r.read())]
    assert nomes == ["Ervilha"]
