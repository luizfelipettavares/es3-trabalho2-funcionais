"""Page Object da única tela do produtos-web (http://localhost:4173).

Localizadores: id/data-testid adicionados ao sistema (patch/0001-data-testid.patch),
porque o original só tinha id no campo de busca. Sem XPath absoluto.
A lista é filtrada no navegador a cada tecla (React), então as esperas aguardam
a tabela refletir o filtro (condição), nunca um tempo fixo.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class ProdutosPage:
    CAMPO_BUSCA = (By.CSS_SELECTOR, "[data-testid='campo-busca']")
    FILTRO_ESTOQUE = (By.CSS_SELECTOR, "[data-testid='filtro-estoque']")
    TABELA = (By.CSS_SELECTOR, "[data-testid='tabela-produtos']")
    LINHAS = (By.CSS_SELECTOR, "[data-testid='linha-produto']")
    CATEGORIAS = (By.CSS_SELECTOR, "[data-testid='linha-categoria']")
    VAZIO = (By.CSS_SELECTOR, "[data-testid='mensagem-vazia']")
    FONTE = (By.CSS_SELECTOR, "[data-testid='fonte-dados']")
    CARREGANDO = (By.CSS_SELECTOR, "[data-testid='carregando']")

    def __init__(self, driver, base_url):
        self.driver, self.base_url = driver, base_url
        self.wait = WebDriverWait(driver, 5)

    def abrir(self):
        self.driver.get(self.base_url + "/")
        self.wait.until(EC.visibility_of_element_located(self.TABELA))
        self.wait.until(EC.visibility_of_element_located(self.FONTE))   # carga terminou
        return self

    # ------------------------------------------------------------ ações
    def buscar(self, texto):
        campo = self.driver.find_element(*self.CAMPO_BUSCA)
        campo.clear()
        campo.send_keys(texto)
        self.wait.until(lambda d: d.find_element(*self.CAMPO_BUSCA).get_attribute("value") == texto)
        return self

    def marcar_so_estoque(self, marcado=True):
        caixa = self.driver.find_element(*self.FILTRO_ESTOQUE)
        if caixa.is_selected() != marcado:
            caixa.click()
        self.wait.until(lambda d: d.find_element(*self.FILTRO_ESTOQUE).is_selected() == marcado)
        return self

    # ------------------------------------------------------------ leitura
    def aguardar_quantidade(self, n):
        """Espera a tabela mostrar n produtos (0 = mensagem de lista vazia)."""
        if n == 0:
            self.wait.until(EC.visibility_of_element_located(self.VAZIO))
        else:
            self.wait.until(lambda d: len(d.find_elements(*self.LINHAS)) == n)
        return self

    def produtos(self):
        """[(nome, preco_texto, em_falta)] na ordem exibida."""
        saida = []
        for linha in self.driver.find_elements(*self.LINHAS):
            nome_td = linha.find_element(By.CSS_SELECTOR, "[data-testid='nome-produto']")
            em_falta = bool(nome_td.find_elements(By.CSS_SELECTOR, "[data-testid='selo-em-falta']"))
            nome = nome_td.text.replace("em falta", "").strip()
            preco = linha.find_element(By.CSS_SELECTOR, "[data-testid='preco-produto']").text
            saida.append((nome, preco.replace(" ", " "), em_falta))
        return saida

    def nomes(self):
        return [n for n, _, _ in self.produtos()]

    def categorias(self):
        return [c.text for c in self.driver.find_elements(*self.CATEGORIAS)]

    def mensagem_vazia(self):
        return self.driver.find_element(*self.VAZIO).text

    def fonte_dos_dados(self):
        return self.driver.find_element(*self.FONTE).text.strip()
