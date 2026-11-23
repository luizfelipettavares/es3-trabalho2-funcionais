"""Page Object da tela /inscricoes (Desafio B).

A tela não recarrega: o envio usa fetch() e a lista #lista é redesenhada depois
que a resposta chega. Por isso as esperas são explícitas e baseadas em condições
da página (mensagem preenchida, quantidade de itens na lista, término da chamada
que carrega a lista), nunca em sleep fixo.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

ESPERA_S = 5

# Verdadeiro quando a última chamada a /api/inscricoes terminou há pelo menos 150 ms
# (tempo para o JavaScript da página redesenhar a lista depois da resposta).
_JS_LISTA_CARREGADA = """
const e = performance.getEntriesByType('resource')
            .filter(x => x.name.endsWith('/api/inscricoes') && x.initiatorType === 'fetch');
if (!e.length) return false;
const ultima = e[e.length - 1];
return ultima.responseEnd > 0 && performance.now() - ultima.responseEnd > 150;
"""


class InscricoesPage:
    NOME = (By.ID, "nome")
    EMAIL = (By.ID, "email")
    CURSO = (By.ID, "curso")
    CONFIRMAR = (By.ID, "confirmar")
    ERRO = (By.ID, "erro")
    SUCESSO = (By.ID, "sucesso")
    ITENS_LISTA = (By.CSS_SELECTOR, "#lista li")

    def __init__(self, driver, base_url):
        self.driver, self.base_url = driver, base_url
        self.wait = WebDriverWait(driver, ESPERA_S)

    # ------------------------------------------------------------ navegação
    def abrir(self):
        self.driver.get(f"{self.base_url}/inscricoes")
        self.wait.until(EC.element_to_be_clickable(self.CONFIRMAR))
        self.aguardar_lista_carregada()
        return self

    def aguardar_lista_carregada(self):
        self.wait.until(lambda d: d.execute_script(_JS_LISTA_CARREGADA))
        return self

    # ------------------------------------------------------------ ações
    def inscrever(self, nome="", email="", curso=""):
        """Preenche e envia. curso = "1" | "2" | "3" ou "" (deixa 'Selecione')."""
        for loc, valor in ((self.NOME, nome), (self.EMAIL, email)):
            campo = self.driver.find_element(*loc)
            campo.clear()
            campo.send_keys(valor)
        Select(self.driver.find_element(*self.CURSO)).select_by_value(str(curso))
        self.driver.find_element(*self.CONFIRMAR).click()
        # o submit limpa #erro/#sucesso e só preenche um deles quando o servidor responde
        self.wait.until(lambda d: d.find_element(*self.ERRO).text or d.find_element(*self.SUCESSO).text)
        return self

    def cancelar(self, inscricao_id):
        self.wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, f"[data-testid='cancelar-{inscricao_id}']"))).click()
        self.wait.until(EC.text_to_be_present_in_element(self.SUCESSO, "Inscrição cancelada"))
        self.wait.until_not(EC.presence_of_element_located((By.CSS_SELECTOR, f"#lista li[data-id='{inscricao_id}']")))
        return self

    # ------------------------------------------------------------ leitura
    def mensagem_erro(self):
        return self.driver.find_element(*self.ERRO).text

    def mensagem_sucesso(self):
        return self.driver.find_element(*self.SUCESSO).text

    def itens(self):
        """Lista de (id, texto) exibida na tela, depois de a lista terminar de carregar."""
        self.aguardar_lista_carregada()
        return [(int(li.get_attribute("data-id")), li.text.replace("Cancelar", "").strip())
                for li in self.driver.find_elements(*self.ITENS_LISTA)]

    def aguardar_itens(self, quantidade):
        self.wait.until(lambda d: len(d.find_elements(*self.ITENS_LISTA)) == quantidade)
        return self.itens()
