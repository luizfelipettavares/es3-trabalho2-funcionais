"""
DESAFIO A - Trabalho 2: portal de Matrícula Acadêmica (Selenium + pytest)

Casos especificados em matriz_casos_matricula.csv (CT01 a CT13, regras R1 a R7).
Cada teste começa com o sistema zerado (fixture autouse) e prepara pela API só o
que a tela não monta rápido (vagas ocupadas por outros alunos, matrícula prévia).
A ação avaliada e a verificação principal são sempre feitas pela interface.

Executar:  HEADLESS=1 pytest -v --html=relatorio.html --self-contained-html
"""
import json
import re
import urllib.error
import urllib.request

import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.matricula_pages import ComprovantePage, DisciplinasPage, LoginMatriculaPage

ALUNO, SENHA = "20260001", "senha123"
VAGAS_INICIAIS = {"ES3": 40, "BD2": 40, "PW2": 35, "RED": 30, "IHC": 30, "EMP": 50, "MOB": 5}


# ------------------------------------------------------------------ apoio (API)
def _post(base_url, caminho, corpo=None):
    req = urllib.request.Request(f"{base_url}{caminho}", method="POST",
                                 data=json.dumps(corpo or {}).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def matricular_pela_api(base_url, aluno, disciplinas):
    status, corpo = _post(base_url, "/api/matriculas", {"aluno": aluno, "disciplinas": disciplinas})
    assert status == 201, f"pré-condição falhou: {status} {corpo}"
    return corpo


@pytest.fixture(autouse=True)
def sistema_zerado(base_url):
    status, _ = _post(base_url, "/api/admin/reset")
    assert status == 200


@pytest.fixture
def oferta(driver, base_url):
    """Pré-condição comum: aluno 20260001 logado na oferta de disciplinas."""
    LoginMatriculaPage(driver, base_url).abrir().entrar(ALUNO, SENHA)
    pagina = DisciplinasPage(driver, base_url)
    assert pagina.esta_aberta()
    return pagina


# ------------------------------------------------------------------ R1 - Login
def test_ct01_login_valido_abre_oferta(driver, base_url):
    LoginMatriculaPage(driver, base_url).abrir().entrar(ALUNO, SENHA)
    pagina = DisciplinasPage(driver, base_url)
    assert pagina.esta_aberta()
    assert driver.current_url.endswith("/matricula/disciplinas")
    assert pagina.aluno_logado() == ALUNO


@pytest.mark.parametrize("matricula, senha", [
    pytest.param("20260001", "senha-errada", id="senha_errada"),
    pytest.param("20269999", "senha123", id="matricula_inexistente"),
    pytest.param("", "", id="campos_vazios"),
])
def test_ct02_login_invalido_e_rejeitado(driver, base_url, matricula, senha):
    login = LoginMatriculaPage(driver, base_url).abrir().entrar(matricula, senha)
    assert login.mensagem_erro() == "Matrícula ou senha inválidas."
    assert login.esta_aberta()
    assert not driver.find_elements(*DisciplinasPage.TABELA)   # a oferta não abriu


# ------------------------------------------------------------------ R2 - Acesso
def test_ct03_oferta_sem_login_redireciona(driver, base_url):
    DisciplinasPage(driver, base_url).abrir()
    WebDriverWait(driver, 5).until(EC.url_contains("/matricula/login"))
    assert not driver.find_elements(*DisciplinasPage.TABELA)


# ------------------------------------------------------------------ R3 - Quantidade (valor-limite)
SEM_CHOQUE = ["ES3", "BD2", "PW2", "IHC", "EMP", "MOB"]   # 6 horários distintos


@pytest.mark.parametrize("qtd", [1, 5], ids=["limite_1", "limite_5"])
def test_ct04_ct05_quantidade_valida_matricula(driver, base_url, oferta, qtd):
    escolha = SEM_CHOQUE[:qtd]
    oferta.selecionar(*escolha).confirmar()
    comp = ComprovantePage(driver)
    assert comp.mensagem() == "Matrícula realizada com sucesso!"
    assert comp.disciplinas() == escolha


@pytest.mark.parametrize("qtd, mensagem", [
    pytest.param(0, "Selecione ao menos uma disciplina.", id="limite_0"),
    pytest.param(6, "Máximo de 5 disciplinas por semestre.", id="limite_6"),
])
def test_ct06_ct07_quantidade_invalida_rejeitada(oferta, qtd, mensagem):
    oferta.selecionar(*SEM_CHOQUE[:qtd]).confirmar()
    assert oferta.mensagem_erro() == mensagem
    assert oferta.todas_as_vagas() == VAGAS_INICIAIS            # nada foi gravado


# ------------------------------------------------------------------ R4 - Horário
def test_ct08_choque_de_horario_rejeitado(oferta):
    oferta.selecionar("ES3", "RED").confirmar()                  # ambas SEG-19h
    assert oferta.mensagem_erro() == "Choque de horário entre disciplinas selecionadas."
    assert oferta.todas_as_vagas() == VAGAS_INICIAIS


# ------------------------------------------------------------------ R5 - Vagas
def test_ct09_disciplina_sem_vagas_rejeitada(driver, base_url):
    for n in range(2, 7):                                         # 5 outros alunos ocupam MOB
        matricular_pela_api(base_url, f"2026{n:04d}", ["MOB"])
    LoginMatriculaPage(driver, base_url).abrir().entrar(ALUNO, SENHA)
    oferta = DisciplinasPage(driver, base_url)
    assert oferta.vagas("MOB") == 0
    oferta.selecionar("ES3", "MOB").confirmar()
    assert oferta.mensagem_erro() == "Vagas esgotadas: MOB."
    assert oferta.vagas("ES3") == 40                              # ES3 não foi descontada
    assert oferta.vagas("MOB") == 0                               # nunca negativa


# ------------------------------------------------------------------ R6 - Matrícula única
def test_ct10_segunda_matricula_do_aluno_rejeitada(driver, base_url):
    matricular_pela_api(base_url, ALUNO, ["ES3"])
    LoginMatriculaPage(driver, base_url).abrir().entrar(ALUNO, SENHA)
    oferta = DisciplinasPage(driver, base_url)
    oferta.selecionar("BD2").confirmar()
    assert oferta.mensagem_erro() == "Aluno já possui matrícula neste semestre."
    assert oferta.vagas("BD2") == 40
    assert oferta.vagas("ES3") == 39                              # só a matrícula prévia


# ------------------------------------------------------------------ R7 - Sucesso
def test_ct11_sucesso_gera_comprovante_e_desconta_vagas(driver, base_url, oferta):
    oferta.selecionar("ES3", "BD2", "IHC").confirmar()
    comp = ComprovantePage(driver)
    assert comp.mensagem() == "Matrícula realizada com sucesso!"
    assert re.fullmatch(r"COMP-\d{6}", comp.numero())
    assert comp.disciplinas() == ["ES3", "BD2", "IHC"]
    vagas = DisciplinasPage(driver, base_url).abrir().todas_as_vagas()
    esperado = dict(VAGAS_INICIAIS, ES3=39, BD2=39, IHC=29)       # 1 a menos em cada, só nelas
    assert vagas == esperado


def test_ct12_ultima_vaga_pode_ser_ocupada(driver, base_url):
    """Valor-limite de R5: com 1 vaga restante a matrícula é aceita e a vaga vai a 0."""
    for n in range(2, 6):                                         # 4 de 5 vagas de MOB
        matricular_pela_api(base_url, f"2026{n:04d}", ["MOB"])
    LoginMatriculaPage(driver, base_url).abrir().entrar(ALUNO, SENHA)
    oferta = DisciplinasPage(driver, base_url)
    assert oferta.vagas("MOB") == 1
    oferta.selecionar("MOB").confirmar()
    assert ComprovantePage(driver).mensagem() == "Matrícula realizada com sucesso!"
    assert DisciplinasPage(driver, base_url).abrir().vagas("MOB") == 0
