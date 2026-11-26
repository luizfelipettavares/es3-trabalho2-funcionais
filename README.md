# Trabalho 2 – Testes funcionais (ES III)

Equipe: Luiz Felipe de Lima Silva Tavares da Costa e Samuel Alves de Sousa · Testes em **Python**: Selenium 4 + pytest (+ pytest-html)

| Parte | Sistema / tela | Onde está | Casos |
|---|---|---|---|
| Exemplo A – Fluxo de pedido | Sabor Express `localhost:5000/login` | `pacote-A/exemplo/` (solução do professor, sem alterações) | 5 |
| **Desafio A – Portal de matrícula** | `localhost:5000/matricula/login` | `pacote-A/desafio/` | 13 especificados, 12 automatizados (14 execuções com as variações) |
| Exemplo B – Login | `127.0.0.1:8000/login` | `pacote-B/exemplo/` (sem alterações) | 2 |
| **Desafio B – Inscrições** | `127.0.0.1:8000/inscricoes` | `pacote-B/desafio/` | 14 especificados e automatizados (19 execuções) |
| **Projeto anterior** | *produtos-web* (Prog. para Internet II) `localhost:4173` | `projeto-anterior/` | 10 especificados e automatizados (15 execuções) |
| Sistemas testados (cópia do kit do professor, sem alterações) | Pacote A (Flask) e Pacote B | `sistemas/` | |
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

## Passo a passo no Windows (Git CMD)

**Pré-requisitos**
- Python 3 (testado com 3.13 e 3.15). No instalador, marque *Add python.exe to PATH*.
- Git for Windows (instala o terminal **Git CMD**, usado em todos os passos).
- Google Chrome instalado. O Selenium baixa o driver sozinho na primeira execução (precisa de internet).

Use sempre `127.0.0.1` nos endereços, não `localhost`: no Windows, `localhost` deixou cada requisição cerca de 2 s mais lenta.

**1. Baixar o trabalho** (uma vez)
```bat
cd C:\
mkdir Projetos
cd Projetos
git clone https://github.com/luizfelipettavares/es3-trabalho2-funcionais
```

**2. Criar o ambiente e instalar as dependências** (uma vez)
```bat
cd C:\Projetos\es3-trabalho2-funcionais
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m pip install -r sistemas\pacote-A\requirements.txt
```
Certo quando a linha começa com `(.venv)` e o `pip` termina sem erro.
Em toda janela nova, entre na pasta e rode `.venv\Scripts\activate.bat` de novo.

**3. Subir os sistemas** (uma janela do Git CMD para cada; não feche)

Janela 1 – Pacote A (porta 5000):
```bat
cd C:\Projetos\es3-trabalho2-funcionais
.venv\Scripts\activate.bat
cd sistemas\pacote-A
python app.py
```
Certo quando aparece `Running on http://127.0.0.1:5000`.

Janela 2 – Pacote B (porta 8000):
```bat
cd C:\Projetos\es3-trabalho2-funcionais
.venv\Scripts\activate.bat
cd sistemas\pacote-B
python app.py
```
Certo quando aparece `Aplicação local em http://127.0.0.1:8000`.

**4. Rodar os testes** (janela 3; o Chrome abre e fecha sozinho)

Pacote A – portal de matrícula (precisa da janela 1):
```bat
cd C:\Projetos\es3-trabalho2-funcionais
.venv\Scripts\activate.bat
cd pacote-A\desafio
set BASE_URL=http://127.0.0.1:5000
pytest -v -k ct09
pytest -v
```
- `pytest -v -k ct09` roda só um caso (alguns segundos). Esperado: `1 passed`.
- `pytest -v` roda a suíte toda (cerca de 1 min com o Chrome visível). Esperado: `14 passed`.
- O `set` vale só para a janela onde foi digitado.

Pacote B – inscrições (precisa da janela 2):
```bat
cd C:\Projetos\es3-trabalho2-funcionais\pacote-B\desafio
python -m pytest test_inscricoes.py -v
```
Esperado: `19 passed`.

Para não abrir o navegador, rode antes `set HEADLESS=1`. Rode uma suíte por vez, nunca duas ao mesmo tempo.
Para o projeto anterior (produtos-web), ver as seções 2 e 3 abaixo.

**5. Encerrar**: `Ctrl+C` nas janelas 1 e 2.

**Se algo der errado**

| Aparece | Fazer |
|---|---|
| `'python' não é reconhecido` | Reinstale o Python marcando *Add python.exe to PATH* e abra um Git CMD novo. |
| `'pytest' não é reconhecido` | Ambiente não ativado: `.venv\Scripts\activate.bat` na pasta do trabalho. |
| `ModuleNotFoundError: No module named 'flask'` | Faltou o passo 2: `python -m pip install -r sistemas\pacote-A\requirements.txt`. |
| Todos os testes falham logo no início | O sistema não está no ar ou faltou o `set BASE_URL=...` nesta janela. |
| Erro ao abrir o Chrome / baixar o driver | Confira se o Chrome está instalado e se há internet na primeira execução. |
| Testes muito lentos (vários segundos cada) | Ficou `localhost`: use `set BASE_URL=http://127.0.0.1:5000`. |

## Passo a passo completo (Linux/macOS e todas as execuções)

As seções abaixo trazem todos os comandos usados para gerar os resultados registrados.

## 1. Preparar o ambiente

```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```
Ativação no Windows: Git CMD/CMD `.venv\Scripts\activate.bat` · PowerShell `.venv\Scripts\Activate.ps1` · Git Bash `source .venv/Scripts/activate`.

O sistema do Pacote A (`python app.py`) precisa do Flask, que não está no `requirements.txt` acima.
Com o ambiente ativado, instale também:

```bash
python -m pip install -r sistemas/pacote-A/requirements.txt
```
O sistema do Pacote B usa só a biblioteca padrão do Python e não precisa de nada extra.

Google Chrome instalado. O Selenium Manager baixa o driver na primeira execução (precisa de internet).

## 2. Subir os sistemas

```bash
cd sistemas/pacote-A && python app.py      # :5000
cd sistemas/pacote-B && python app.py           # :8000

# projeto anterior – usar a cópia com data-testid (patch em projeto-anterior/patch/)
git clone https://github.com/luizfelipettavares/produtos-web && cd produtos-web
git apply <pasta-deste-repositorio>/projeto-anterior/patch/0001-data-testid.patch
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

> **Windows: aponte os testes para `127.0.0.1`.** O padrão dos testes do Pacote A é `http://localhost:5000`;
> num teste em Windows 11, com `localhost` cada requisição levou cerca de 2 s a mais e o CT09 demorou 27,6 s.
> Com `127.0.0.1` o CT09 levou 6,9 s e a suíte do Desafio A passou inteira (14 passed). Exemplo no Git CMD/CMD:
>
> ```bat
> cd pacote-A\desafio
> set BASE_URL=http://127.0.0.1:5000
> pytest -v -k ct09
> ```
> O `set` vale só para a janela onde foi digitado.

Variáveis: `BASE_URL`, `HEADLESS=1`, `CI=1` (Linux como root/contêiner: `--no-sandbox`), `CHROMEDRIVER`, `CHROME_BINARY`.
