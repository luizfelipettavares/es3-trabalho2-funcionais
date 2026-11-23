"""Gera as matrizes de casos de teste (formato 04_Modelos/Modelo_Matriz_Casos_de_Teste.csv)
e preenche resultado_obtido/status a partir dos JUnit XML das 3 execuções.

Uso (da raiz do trabalho2-funcionais):  python ferramentas/gerar_matrizes.py

O resultado esperado de cada caso vem da regra (guia do aluno / README do sistema),
não do que a tela mostra hoje. Um caso só é "aprovado" se TODAS as variações
(parametrize) passaram nas 3 execuções.
"""
import csv
import pathlib
import xml.etree.ElementTree as ET

RAIZ = pathlib.Path(__file__).resolve().parent.parent
RES = RAIZ / "resultados"
CAMPOS = ["id", "regra", "fluxo", "tecnica", "pre_condicao", "dados", "passos", "resultado_esperado",
          "assercao_principal", "resultado_obtido", "status", "evidencia", "arquivo_funcao"]

A = [
    ("CT01", "R1 - Login", "Login", "Partição (válida)", "Sistema zerado", "20260001 / senha123",
     "1. Abrir /matricula/login 2. Preencher 3. Entrar", "Oferta de disciplinas aberta com o aluno no cabeçalho",
     "Tabela #tabela-disciplinas visível; URL /matricula/disciplinas", "test_matricula.py::test_ct01_login_valido_abre_oferta"),
    ("CT02", "R1 - Login", "Login", "Partição (inválidas) - orientado a dados", "Sistema zerado",
     "senha errada; matrícula inexistente 20269999; campos vazios", "1. Abrir login 2. Preencher dado inválido 3. Entrar",
     "\"Matrícula ou senha inválidas.\" e permanece no login", "Mensagem exata; tabela de disciplinas ausente",
     "test_matricula.py::test_ct02_login_invalido_e_rejeitado"),
    ("CT03", "R2 - Acesso", "Acesso direto", "Partição (sem sessão)", "Navegador sem login", "-",
     "1. Abrir /matricula/disciplinas direto", "Redireciona para /matricula/login", "URL contém /matricula/login; tabela ausente",
     "test_matricula.py::test_ct03_oferta_sem_login_redireciona"),
    ("CT04", "R3/R7 - Quantidade", "Matrícula", "Valor-limite (1)", "Logado, sistema zerado", "ES3",
     "1. Marcar 1 disciplina 2. Confirmar", "Matrícula realizada com sucesso!", "Mensagem de sucesso; disciplinas = [ES3]",
     "test_matricula.py::test_ct04_ct05_quantidade_valida_matricula[limite_1]"),
    ("CT05", "R3/R7 - Quantidade", "Matrícula", "Valor-limite (5)", "Logado, sistema zerado", "ES3,BD2,PW2,IHC,EMP",
     "1. Marcar 5 disciplinas sem choque 2. Confirmar", "Matrícula realizada com sucesso!", "Mensagem de sucesso; 5 disciplinas listadas",
     "test_matricula.py::test_ct04_ct05_quantidade_valida_matricula[limite_5]"),
    ("CT06", "R3 - Quantidade", "Matrícula", "Valor-limite (0)", "Logado, sistema zerado", "nenhuma",
     "1. Não marcar nada 2. Confirmar", "\"Selecione ao menos uma disciplina.\"", "Mensagem exata; todas as vagas iguais às iniciais",
     "test_matricula.py::test_ct06_ct07_quantidade_invalida_rejeitada[limite_0]"),
    ("CT07", "R3 - Quantidade", "Matrícula", "Valor-limite (6)", "Logado, sistema zerado", "ES3,BD2,PW2,IHC,EMP,MOB",
     "1. Marcar 6 disciplinas sem choque 2. Confirmar", "\"Máximo de 5 disciplinas por semestre.\"", "Mensagem exata; vagas inalteradas",
     "test_matricula.py::test_ct06_ct07_quantidade_invalida_rejeitada[limite_6]"),
    ("CT08", "R4 - Horário", "Matrícula", "Tabela de decisão (mesmo horário)", "Logado, sistema zerado", "ES3 + RED (SEG-19h)",
     "1. Marcar as duas 2. Confirmar", "\"Choque de horário entre disciplinas selecionadas.\"", "Mensagem exata; vagas inalteradas",
     "test_matricula.py::test_ct08_choque_de_horario_rejeitado"),
    ("CT09", "R5 - Vagas", "Matrícula", "Partição (sem vagas)", "5 outros alunos ocupam MOB via API", "ES3 + MOB",
     "1. Login 2. Conferir MOB=0 3. Marcar ES3 e MOB 4. Confirmar", "\"Vagas esgotadas: MOB.\"",
     "Mensagem exata; ES3 continua 40; MOB continua 0 (nunca negativa)", "test_matricula.py::test_ct09_disciplina_sem_vagas_rejeitada"),
    ("CT10", "R6 - Matrícula única", "Matrícula", "Partição (já matriculado)", "Matrícula prévia do 20260001 em ES3 via API", "BD2",
     "1. Login 2. Marcar BD2 3. Confirmar", "\"Aluno já possui matrícula neste semestre.\"", "Mensagem exata; BD2 continua 40; ES3 = 39",
     "test_matricula.py::test_ct10_segunda_matricula_do_aluno_rejeitada"),
    ("CT11", "R7 - Sucesso", "Matrícula", "Partição (válida) + verificação de efeito", "Logado, sistema zerado", "ES3,BD2,IHC",
     "1. Marcar 3 disciplinas 2. Confirmar 3. Reabrir oferta", "Sucesso, comprovante COMP-NNNNNN, disciplinas listadas, 1 vaga a menos em cada",
     "Regex COMP-\\d{6}; lista = [ES3,BD2,IHC]; vagas ES3 39, BD2 39, IHC 29 e demais inalteradas",
     "test_matricula.py::test_ct11_sucesso_gera_comprovante_e_desconta_vagas"),
    ("CT12", "R5/R7 - Vagas", "Matrícula", "Valor-limite (1 vaga restante)", "4 de 5 vagas de MOB ocupadas via API", "MOB",
     "1. Login 2. Conferir MOB=1 3. Marcar MOB 4. Confirmar 5. Reabrir", "Matrícula aceita e MOB vai a 0", "Mensagem de sucesso; vagas MOB = 0",
     "test_matricula.py::test_ct12_ultima_vaga_pode_ser_ocupada"),
    ("CT13", "R5/R6 - Concorrência", "API (não automatizado na UI)", "Teste exploratório de concorrência", "Sistema zerado",
     "20 POST /api/matriculas simultâneos do mesmo aluno", "Ver projeto: trabalho1-desempenho/ferramentas/teste_corrida_matricula.py",
     "Exatamente 1 x 201 e 19 x 409", "Contagem de 201", "trabalho1-desempenho/ferramentas/teste_corrida_matricula.py"),
]

B = [
    ("CT01", "Fluxo válido", "Inscrição", "Partição (válida)", "Estado zerado", "Maria Silva / maria@ads.local / Python",
     "1. Abrir /inscricoes 2. Preencher 3. Confirmar", "\"Inscrição realizada\" e item na lista", "#sucesso exato; lista com 1 item no formato nome / e-mail / curso",
     "test_inscricoes.py::test_ct01_inscricao_valida"),
    ("CT02", "Duplicidade (outro curso)", "Inscrição", "Tabela de decisão (mesmo e-mail, curso diferente)", "maria@ads.local já no curso 1 (API)",
     "maria@ads.local / Java", "1. Abrir 2. Preencher com curso 2 3. Confirmar", "Aceita: \"Inscrição realizada\"", "Lista com 2 itens, um no curso 2",
     "test_inscricoes.py::test_ct02_mesmo_email_em_outro_curso_e_aceito"),
    ("CT03", "Nome", "Inscrição", "Obrigatório - orientado a dados", "Estado zerado", "nome vazio; só espaços",
     "1. Preencher sem nome 2. Confirmar", "\"Nome deve ter de 3 a 60 caracteres\"", "#erro exato; após recarregar, lista vazia",
     "test_inscricoes.py::test_ct03_nome_vazio_rejeitado"),
    ("CT04", "E-mail", "Inscrição", "Partição (inválidas) - orientado a dados", "Estado zerado",
     "sem @; nada antes do @; domínio sem ponto; espaço no meio; vazio", "1. Preencher e-mail inválido 2. Confirmar", "\"E-mail inválido\"",
     "#erro exato; lista vazia", "test_inscricoes.py::test_ct04_email_invalido_rejeitado"),
    ("CT05", "Curso", "Inscrição", "Obrigatório", "Estado zerado", "curso = Selecione", "1. Preencher sem curso 2. Confirmar",
     "\"Curso obrigatório\"", "#erro exato; lista vazia", "test_inscricoes.py::test_ct05_curso_ausente_rejeitado"),
    ("CT06", "Nome", "Inscrição", "Valor-limite (2)", "Estado zerado", "'AA'", "1. Preencher 2. Confirmar", "Rejeita: \"Nome deve ter de 3 a 60 caracteres\"",
     "#erro; lista vazia", "test_inscricoes.py::test_ct06_a_ct09_limites_do_nome[nome_2_rejeita]"),
    ("CT07", "Nome", "Inscrição", "Valor-limite (3)", "Estado zerado", "'AAA'", "1. Preencher 2. Confirmar", "Aceita", "#sucesso; item na lista",
     "test_inscricoes.py::test_ct06_a_ct09_limites_do_nome[nome_3_aceita]"),
    ("CT08", "Nome", "Inscrição", "Valor-limite (60)", "Estado zerado", "60 x 'A'", "1. Preencher 2. Confirmar", "Aceita", "#sucesso; item na lista",
     "test_inscricoes.py::test_ct06_a_ct09_limites_do_nome[nome_60_aceita]"),
    ("CT09", "Nome", "Inscrição", "Valor-limite (61)", "Estado zerado", "61 x 'A'", "1. Preencher 2. Confirmar", "Rejeita: \"Nome deve ter de 3 a 60 caracteres\"",
     "#erro; lista vazia", "test_inscricoes.py::test_ct06_a_ct09_limites_do_nome[nome_61_rejeita]"),
    ("CT09b", "Nome/E-mail (aparar)", "Inscrição", "Valor-limite com espaços", "Estado zerado", "'  Ana  ' / '  ana@ads.local  '",
     "1. Preencher 2. Confirmar", "Aceita e grava aparado", "Lista mostra 'Ana / ana@ads.local / curso 1'", "test_inscricoes.py::test_ct06b_espacos_nas_pontas_nao_contam"),
    ("CT09c", "Nome (aparar)", "Inscrição", "Valor-limite com espaços", "Estado zerado", "'  Al  ' (2 após aparar)",
     "1. Preencher 2. Confirmar", "Rejeita: \"Nome deve ter de 3 a 60 caracteres\"", "#erro; lista vazia", "test_inscricoes.py::test_ct06c_nome_curto_com_espacos_rejeitado"),
    ("CT10", "Duplicidade", "Inscrição", "Tabela de decisão (mesmo e-mail normalizado, mesmo curso)", "maria@ads.local no curso 1 (API)",
     "'  MARIA@Ads.Local ' / Python", "1. Preencher 2. Confirmar", "\"Inscrição já existente\"", "#erro exato; lista continua com 1 item",
     "test_inscricoes.py::test_ct10_duplicidade_ignora_maiusculas_e_espacos"),
    ("CT11", "Lotação", "Inscrição", "Valor-limite (3ª inscrição)", "2 inscrições no curso 2 (API)", "tres@ads.local / Java",
     "1. Preencher 2. Confirmar", "\"Curso sem vagas\"", "#erro exato; lista continua com 2 itens", "test_inscricoes.py::test_ct11_terceira_inscricao_no_curso_lotado"),
    ("CT12", "Cancelamento", "Cancelamento + inscrição", "Transição de estado", "Curso 3 lotado com 2 inscrições (API)",
     "cancelar o 1º; nova inscrição tres@ads.local no curso 3", "1. Cancelar pelo botão 2. Conferir lista 3. Inscrever outro aluno no curso 3",
     "\"Inscrição cancelada\", item some; nova inscrição aceita", "Mensagens exatas; lista 2 -> 1 -> 2 itens", "test_inscricoes.py::test_ct12_cancelamento_libera_vaga"),
]

P = [
    ("P01", "Carregamento", "Abrir catálogo", "Partição (API no ar)", "API e front em localhost", "-", "1. Abrir a página",
     "6 produtos agrupados em Frutas e Verduras; rodapé 'Dados da API REST.'", "Nomes na ordem; categorias; fonte", "test_produtos.py::test_p01_carrega_catalogo_da_api_agrupado"),
    ("P02", "Contingência", "Abrir catálogo", "Partição (API fora)", "Requisições à porta 3000 bloqueadas no navegador (CDP)", "-",
     "1. Bloquear a API 2. Abrir a página", "Usa dados locais e mostra 'Dados locais.'", "Fonte = Dados locais.; 6 produtos", "test_produtos.py::test_p02_api_fora_usa_dados_locais"),
    ("P03", "Busca por nome", "Busca", "Partição - orientado a dados", "Página aberta", "'maçã'; 'MA'; '  ervilha  '; 'a'",
     "1. Digitar o termo", "Só produtos cujo nome contém o termo, sem diferenciar maiúsculas e ignorando espaços nas pontas",
     "Lista de nomes exata", "test_produtos.py::test_p03_busca_por_nome"),
    ("P04", "Busca por nome", "Busca", "Partição (sem resultado)", "Página aberta", "'chocolate'", "1. Digitar",
     "Mensagem 'Nenhum produto encontrado...'", "Mensagem exata; nenhuma linha nem categoria", "test_produtos.py::test_p04_busca_sem_resultado_mostra_mensagem"),
    ("P05", "Agrupamento", "Busca", "Partição", "Página aberta", "'pitaya'", "1. Digitar", "Só a categoria Frutas aparece",
     "categorias == [Frutas]", "test_produtos.py::test_p05_categoria_sem_itens_nao_aparece"),
    ("P06", "Filtro de estoque", "Filtro", "Partição (marcado)", "Página aberta", "checkbox marcado", "1. Marcar 'só em estoque'",
     "4 produtos, nenhum com selo 'em falta'", "Nomes; ausência de selo", "test_produtos.py::test_p06_so_em_estoque"),
    ("P07", "Filtro de estoque", "Filtro", "Transição (marcar/desmarcar)", "Página aberta", "-", "1. Marcar 2. Desmarcar",
     "Volta aos 6 produtos", "Nomes = catálogo completo", "test_produtos.py::test_p07_desmarcar_estoque_restaura_lista"),
    ("P08", "Busca + estoque", "Busca e filtro", "Tabela de decisão (termo x filtro)", "Página aberta",
     "'ma' sem/com filtro; 'abóbora' com filtro", "1. Digitar 2. Marcar/desmarcar", "[Maçã, Maracujá]; [Maçã]; vazio com mensagem",
     "Lista exata / mensagem", "test_produtos.py::test_p08_busca_combinada_com_estoque"),
    ("P09", "Apresentação", "Abrir catálogo", "Partição", "Página aberta", "-", "1. Abrir",
     "Em falta com selo (Maracujá, Abóbora); preço em R$ no formato pt-BR", "Conjunto com selo; 'R$ 1,00' e 'R$ 4,00'", "test_produtos.py::test_p09_em_falta_tem_selo_e_precos_em_reais"),
    ("P10", "Busca por nome (API)", "API", "Consistência tela x API", "API no ar", "q='  ervilha  '", "1. GET /api/products?q=...",
     "Mesmo resultado da tela: [Ervilha]", "Lista de nomes", "test_produtos.py::test_d01_api_busca_com_espacos_igual_a_tela (xfail = Defeito D1)"),
]


def resultados(pasta):
    """{nome_completo_do_teste: [outcome_r1, outcome_r2, outcome_r3]}"""
    saida = {}
    for r in (1, 2, 3):
        xml = pasta / f"execucao_r{r}.xml"
        if not xml.exists():
            continue
        for tc in ET.parse(xml).iter("testcase"):
            nome = tc.get("name")
            if tc.find("failure") is not None or tc.find("error") is not None:
                o = "falhou"
            elif tc.find("skipped") is not None:
                o = "xfail" if "xfail" in (tc.find("skipped").get("type", "") + tc.find("skipped").get("message", "")).lower() else "pulado"
            else:
                o = "passou"
            saida.setdefault(nome, []).append(o)
    return saida


def gerar(casos, pasta_res, destino):
    res = resultados(pasta_res)
    with open(destino, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CAMPOS)
        for (cid, regra, fluxo, tec, pre, dados, passos, esperado, assercao, func) in casos:
            func_nome = func.split("::")[-1].split(" ")[0]
            if "[" in func_nome:                      # um caso = uma variação específica
                chaves = [func_nome]
            else:                                      # um caso = todas as variações do teste
                chaves = [k for k in res if k == func_nome or k.startswith(func_nome + "[")]
            outs = [o for k in chaves for o in res.get(k, [])]
            if not outs and cid == "CT13" and "corrida" in func:
                obtido = "1 x 201 e 19 x 409 em 5 de 5 tentativas; ES3 = 39 (corrida_matricula.txt)"
                status = "aprovado (execução manual do script)"
            elif not outs:
                obtido, status = "não automatizado na UI (ver evidência)", "manual"
            elif all(o == "passou" for o in outs):
                obtido, status = f"conforme esperado em {len(outs)} execuções ({len(chaves)} variação(ões) x 3)", "aprovado"
            elif all(o == "xfail" for o in outs):
                obtido, status = "API devolve [] (defeito D1 reproduzido nas 3 execuções)", "falhou (defeito registrado)"
            else:
                obtido, status = f"resultados: {outs}", "falhou / oscilou"
            evid = (f"{pasta_res.relative_to(RAIZ)}/execucao_r1..r3.html" if outs
                    else "trabalho1-desempenho/resultados/pacote-A/corrida_matricula.txt")
            w.writerow([cid, regra, fluxo, tec, pre, dados, passos, esperado, assercao, obtido, status, evid, func])
    print(destino.relative_to(RAIZ))


gerar(A, RES / "pacote-A-desafio", RAIZ / "pacote-A" / "desafio" / "matriz_casos_matricula.csv")
gerar(B, RES / "pacote-B-desafio", RAIZ / "pacote-B" / "desafio" / "matriz_casos_inscricoes.csv")
gerar(P, RES / "projeto-anterior", RAIZ / "projeto-anterior" / "matriz_casos_produtos.csv")
