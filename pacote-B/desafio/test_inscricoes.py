"""DESAFIO B - Trabalho 2: inscrições em minicursos (Selenium + pytest).

Casos especificados em matriz_casos_inscricoes.csv (CT01 a CT12 + extras).
Cada teste zera o estado (POST /api/reset) e, quando precisa, prepara inscrições
pela API (POST /api/inscricoes). A ação avaliada e a verificação principal são
feitas pela tela. Nos casos de rejeição, a tela é recarregada e a lista conferida
para provar que nada indevido foi gravado.

Rodar em SEQUÊNCIA (nunca com -n / xdist): o estado é compartilhado.
    HEADLESS=1 python -m pytest test_inscricoes.py -v --junitxml=resultado.xml
"""
import json
import urllib.error
import urllib.request

import pytest

from pages.inscricoes_page import InscricoesPage


# ------------------------------------------------------------------ apoio (API)
def _post(base_url, caminho, corpo=None):
    req = urllib.request.Request(base_url + caminho, method="POST",
                                 data=json.dumps(corpo or {}).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def inscrever_pela_api(base_url, nome, email, curso):
    status, corpo = _post(base_url, "/api/inscricoes", {"nome": nome, "email": email, "curso": curso})
    assert status == 201, f"pré-condição falhou: {status} {corpo}"
    return corpo


@pytest.fixture(autouse=True)
def estado_zerado(base_url):
    status, _ = _post(base_url, "/api/reset")
    assert status == 200


@pytest.fixture
def tela(driver, base_url):
    return InscricoesPage(driver, base_url).abrir()


def assert_rejeitado(tela, mensagem, itens_antes=0):
    assert tela.mensagem_erro() == mensagem
    assert tela.mensagem_sucesso() == ""
    assert len(tela.abrir().itens()) == itens_antes      # recarrega: nada foi gravado


# ------------------------------------------------------------------ fluxos válidos
def test_ct01_inscricao_valida(tela):
    tela.inscrever("Maria Silva", "maria@ads.local", "1")
    assert tela.mensagem_sucesso() == "Inscrição realizada"
    itens = tela.aguardar_itens(1)
    assert itens[0][1] == "Maria Silva / maria@ads.local / curso 1"


def test_ct02_mesmo_email_em_outro_curso_e_aceito(tela, base_url):
    inscrever_pela_api(base_url, "Maria Silva", "maria@ads.local", 1)
    tela.abrir().aguardar_itens(1)
    tela.inscrever("Maria Silva", "maria@ads.local", "2")
    assert tela.mensagem_sucesso() == "Inscrição realizada"
    textos = [t for _, t in tela.aguardar_itens(2)]
    assert "Maria Silva / maria@ads.local / curso 2" in textos


# ------------------------------------------------------------------ obrigatórios e formato
@pytest.mark.parametrize("nome", ["", "   "], ids=["vazio", "so_espacos"])
def test_ct03_nome_vazio_rejeitado(tela, nome):
    tela.inscrever(nome, "joao@ads.local", "1")
    assert_rejeitado(tela, "Nome deve ter de 3 a 60 caracteres")


@pytest.mark.parametrize("email", [
    "joaoads.local",        # sem @
    "@ads.local",           # nada antes do @
    "joao@adslocal",        # domínio sem ponto
    "jo ao@ads.local",      # espaço no meio
    "",                     # vazio
], ids=["sem_arroba", "sem_usuario", "dominio_sem_ponto", "com_espaco", "vazio"])
def test_ct04_email_invalido_rejeitado(tela, email):
    tela.inscrever("João Souza", email, "1")
    assert_rejeitado(tela, "E-mail inválido")


def test_ct05_curso_ausente_rejeitado(tela):
    tela.inscrever("João Souza", "joao@ads.local", "")
    assert_rejeitado(tela, "Curso obrigatório")


# ------------------------------------------------------------------ valores-limite do nome
@pytest.mark.parametrize("tamanho, aceito", [
    pytest.param(2, False, id="nome_2_rejeita"),
    pytest.param(3, True, id="nome_3_aceita"),
    pytest.param(60, True, id="nome_60_aceita"),
    pytest.param(61, False, id="nome_61_rejeita"),
])
def test_ct06_a_ct09_limites_do_nome(tela, tamanho, aceito):
    nome = "A" * tamanho
    tela.inscrever(nome, "limite@ads.local", "3")
    if aceito:
        assert tela.mensagem_sucesso() == "Inscrição realizada"
        assert tela.aguardar_itens(1)[0][1].startswith(nome + " / ")
    else:
        assert_rejeitado(tela, "Nome deve ter de 3 a 60 caracteres")


def test_ct06b_espacos_nas_pontas_nao_contam(tela):
    """'  Ana  ' tem 7 caracteres, mas 3 depois de aparar: deve ser aceito e gravado aparado."""
    tela.inscrever("  Ana  ", "  ana@ads.local  ", "1")
    assert tela.mensagem_sucesso() == "Inscrição realizada"
    assert tela.aguardar_itens(1)[0][1] == "Ana / ana@ads.local / curso 1"


def test_ct06c_nome_curto_com_espacos_rejeitado(tela):
    """'  Al  ' tem 6 caracteres, mas só 2 depois de aparar: deve ser rejeitado."""
    tela.inscrever("  Al  ", "al@ads.local", "1")
    assert_rejeitado(tela, "Nome deve ter de 3 a 60 caracteres")


# ------------------------------------------------------------------ regras com estado
def test_ct10_duplicidade_ignora_maiusculas_e_espacos(tela, base_url):
    inscrever_pela_api(base_url, "Maria Silva", "maria@ads.local", 1)
    tela.abrir().aguardar_itens(1)
    tela.inscrever("Maria S.", "  MARIA@Ads.Local ", "1")
    assert_rejeitado(tela, "Inscrição já existente", itens_antes=1)


def test_ct11_terceira_inscricao_no_curso_lotado(tela, base_url):
    inscrever_pela_api(base_url, "Aluno Um", "um@ads.local", 2)
    inscrever_pela_api(base_url, "Aluno Dois", "dois@ads.local", 2)
    tela.abrir().aguardar_itens(2)
    tela.inscrever("Aluno Tres", "tres@ads.local", "2")
    assert_rejeitado(tela, "Curso sem vagas", itens_antes=2)


def test_ct12_cancelamento_libera_vaga(tela, base_url):
    primeiro = inscrever_pela_api(base_url, "Aluno Um", "um@ads.local", 3)
    inscrever_pela_api(base_url, "Aluno Dois", "dois@ads.local", 3)
    tela.abrir().aguardar_itens(2)

    tela.cancelar(primeiro["id"])
    assert tela.mensagem_sucesso() == "Inscrição cancelada"
    assert [i for i, _ in tela.aguardar_itens(1)] != [primeiro["id"]]

    tela.inscrever("Aluno Tres", "tres@ads.local", "3")           # a vaga liberada é usada
    assert tela.mensagem_sucesso() == "Inscrição realizada"
    textos = [t for _, t in tela.aguardar_itens(2)]
    assert "Aluno Tres / tres@ads.local / curso 3" in textos
