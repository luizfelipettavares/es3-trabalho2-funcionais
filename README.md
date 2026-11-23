# Trabalho 2 – Testes funcionais (ES III)

Equipe: Luiz Felipe de Lima Silva Tavares da Costa e Samuel Alves de Sousa · Testes em **Python**: Selenium 4 + pytest (+ pytest-html)

| Parte | Sistema / tela | Onde está | Casos |
|---|---|---|---|
| Exemplo A – Fluxo de pedido | Sabor Express `localhost:5000/login` | `pacote-A/exemplo/` (solução do professor, sem alterações) | 5 |
| **Desafio A – Portal de matrícula** | `localhost:5000/matricula/login` | `pacote-A/desafio/` | 13 especificados, 12 automatizados (14 execuções com as variações) |
| Exemplo B – Login | `127.0.0.1:8000/login` | `pacote-B/exemplo/` (sem alterações) | 2 |
| **Desafio B – Inscrições** | `127.0.0.1:8000/inscricoes` | `pacote-B/desafio/` | 14 especificados e automatizados (19 execuções) |
| **Projeto anterior** | *produtos-web* (Prog. para Internet II) `localhost:4173` | `projeto-anterior/` | 10 especificados e automatizados (15 execuções) |
| Resultados das 3 execuções | JUnit XML, HTML, logs | `resultados/` | |
| Relatório | | `relatorio.md` / `relatorio.pdf` | |
| Slides da apresentação (Pacote A, com apêndices do B e do projeto) | | `slides.pdf` | |

Versões usadas nas execuções registradas: `versoes_utilizadas.txt`.

## Estrutura de cada suíte

```
desafio/
  conftest.py              fixtures: driver (Chrome), base_url, print automático em evidencias/ se falhar
  pages/                   Page Objects: localizadores (id / data-testid) + ações; nenhum assert
  test_*.py                casos (asserts), dados de teste, preparação de estado pela API
  matriz_casos_*.csv       matriz no formato do modelo, com resultado das 3 execuções
```

Boas práticas aplicadas: só `id`/`data-testid` (nenhum XPath); só esperas explícitas
(`WebDriverWait`, `implicitly_wait(0)`, nenhum `sleep`); um Page Object por tela; cada teste
zera e prepara o próprio estado (suíte roda em qualquer ordem); nos casos de rejeição a tela é
conferida de novo para provar que nada foi gravado; `pytest.mark.parametrize` para os dados.

## 1. Preparar o ambiente

```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```
Google Chrome instalado. O Selenium Manager baixa o driver na primeira execução (precisa de internet).

## 2. Subir os sistemas

```bash
cd ESIII_Testes_Funcionais/02_Pacote_A_SaborExpress_Matricula/app && python app.py      # :5000
cd ESIII_Testes_Funcionais/03_Pacote_B_Biblioteca_Minicursos && python app.py           # :8000

# projeto anterior – usar a cópia com data-testid (patch em projeto-anterior/patch/)
git clone https://github.com/luizfelipettavares/produtos-web && cd produtos-web
git apply ../trabalho2-funcionais/projeto-anterior/patch/0001-data-testid.patch
npm install && cd api && npm install && npm run build && PORT=3000 node dist/server.js &   # API :3000
cd .. && echo "VITE_API_URL=http://localhost:3000" > .env && npx vite build && npx vite preview --port 4173   # tela :4173
```
O patch (gerado com `git diff`) só acrescenta atributos `id`/`data-testid` em 5 componentes; não muda
comportamento. Justificativa no relatório (seção do projeto anterior).

## 3. Rodar (cada suíte em sequência, nunca em paralelo)

```bash
export HEADLESS=1          # PowerShell: $env:HEADLESS="1"   (omita para ver o navegador)
cd pacote-A/exemplo  && pytest -v --html=relatorio.html --self-contained-html
cd pacote-A/desafio  && pytest -v --html=relatorio.html --self-contained-html
cd pacote-B/exemplo  && python -m pytest test_login.py -v --junitxml=resultado_login.xml
cd pacote-B/desafio  && python -m pytest test_inscricoes.py -v --html=relatorio.html --self-contained-html
cd projeto-anterior  && python -m pytest test_produtos.py -v --html=relatorio.html --self-contained-html
```
As 3 execuções registradas foram feitas com `bash ferramentas/rodar_3x.sh` (grava em `resultados/`) e a matriz
foi preenchida com `python ferramentas/gerar_matrizes.py`.

Variáveis: `BASE_URL`, `HEADLESS=1`, `CI=1` (Linux como root/contêiner: `--no-sandbox`), `CHROMEDRIVER`, `CHROME_BINARY`.
