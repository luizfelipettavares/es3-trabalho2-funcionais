"""Page Objects do portal de Matrícula Acadêmica (Desafio A).

Uma classe por tela. Cada classe guarda os localizadores (id / data-testid, nunca
XPath absoluto) e as ações. Os asserts ficam nos testes.

Telas: /matricula/login, /matricula/disciplinas e a página do comprovante.
"""
from selenium.common.exceptions import StaleElementReferenceException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ESPERA_S = 5


def pagina_trocou(elemento):
    """Condição de espera: o elemento da página antiga não existe mais.

    Faz o mesmo que EC.staleness_of, mas também aceita o erro "Node with given id
    does not belong to the document", que o Chrome às vezes devolve no meio da
    navegação em vez de StaleElementReferenceException (oscilação observada na
    3ª execução da suíte - ver relatório)."""
    def _condicao(_driver):
        try:
            elemento.is_enabled()
            return False
        except (StaleElementReferenceException, WebDriverException):
            return True
    return _condicao


class LoginMatriculaPage:
    CAMPO_MATRICULA = (By.ID, "matricula")
    CAMPO_SENHA = (By.ID, "senha")
    BOTAO_ENTRAR = (By.ID, "btn-entrar")
    MENSAGEM_ERRO = (By.ID, "mensagem-erro")

    def __init__(self, driver, base_url):
        self.driver, self.base_url = driver, base_url
        self.wait = WebDriverWait(driver, ESPERA_S)

    def abrir(self):
        self.driver.get(f"{self.base_url}/matricula/login")
        self.wait.until(EC.visibility_of_element_located(self.CAMPO_MATRICULA))
        return self

    def entrar(self, matricula, senha):
        campo = self.driver.find_element(*self.CAMPO_MATRICULA)
        campo.clear()
        campo.send_keys(matricula)
        self.driver.find_element(*self.CAMPO_SENHA).send_keys(senha)
        botao = self.driver.find_element(*self.BOTAO_ENTRAR)
        botao.click()
        # O envio do formulário recarrega a página: espera a página antiga sair.
        self.wait.until(pagina_trocou(botao))
        return self

    def mensagem_erro(self):
        return self.wait.until(EC.visibility_of_element_located(self.MENSAGEM_ERRO)).text

    def esta_aberta(self):
        return "/matricula/login" in self.driver.current_url and bool(
            self.driver.find_elements(*self.CAMPO_MATRICULA))


class DisciplinasPage:
    TABELA = (By.ID, "tabela-disciplinas")
    BOTAO_CONFIRMAR = (By.ID, "btn-confirmar")
    MENSAGEM_ERRO = (By.ID, "mensagem-erro")
    USUARIO_LOGADO = (By.ID, "usuario-logado")

    def __init__(self, driver, base_url):
        self.driver, self.base_url = driver, base_url
        self.wait = WebDriverWait(driver, ESPERA_S)

    def abrir(self):
        self.driver.get(f"{self.base_url}/matricula/disciplinas")
        return self

    def esta_aberta(self):
        return self.wait.until(EC.visibility_of_element_located(self.TABELA)).is_displayed()

    def aluno_logado(self):
        return self.driver.find_element(*self.USUARIO_LOGADO).text

    @staticmethod
    def _checkbox(codigo):
        return (By.ID, f"chk-{codigo}")

    @staticmethod
    def _vagas(codigo):
        return (By.CSS_SELECTOR, f"[data-testid='disc-{codigo}'] .vagas")

    def selecionar(self, *codigos):
        for codigo in codigos:
            caixa = self.wait.until(EC.element_to_be_clickable(self._checkbox(codigo)))
            if not caixa.is_selected():
                caixa.click()
        return self

    def confirmar(self):
        botao = self.driver.find_element(*self.BOTAO_CONFIRMAR)
        botao.click()
        self.wait.until(pagina_trocou(botao))     # POST + redirecionamento

    def vagas(self, codigo):
        return int(self.wait.until(EC.visibility_of_element_located(self._vagas(codigo))).text)

    def todas_as_vagas(self):
        self.esta_aberta()
        linhas = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid^='disc-']")
        return {l.get_attribute("data-testid").removeprefix("disc-"): int(l.find_element(By.CLASS_NAME, "vagas").text)
                for l in linhas}

    def mensagem_erro(self):
        return self.wait.until(EC.visibility_of_element_located(self.MENSAGEM_ERRO)).text


class ComprovantePage:
    MENSAGEM_SUCESSO = (By.ID, "mensagem-sucesso")
    COMPROVANTE = (By.ID, "comprovante")
    DISCIPLINAS = (By.ID, "disciplinas-matriculadas")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, ESPERA_S)

    def mensagem(self):
        return self.wait.until(EC.visibility_of_element_located(self.MENSAGEM_SUCESSO)).text

    def numero(self):
        return self.driver.find_element(*self.COMPROVANTE).text

    def disciplinas(self):
        texto = self.driver.find_element(*self.DISCIPLINAS).text
        return [c.strip() for c in texto.split(",") if c.strip()]
