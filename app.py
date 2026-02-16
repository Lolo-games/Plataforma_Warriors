import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="PLATAFORMA WARRIORS", layout="wide")

# =========================
# TEMA DARK
# =========================
st.markdown("""
<style>
.stApp { background-color: #0f1117; }
h1, h2, h3 { color: white; }
section[data-testid="stSidebar"] { background-color: #161a23; }
button[kind="primary"] {
    background-color: #ff4b4b !important;
    color: white !important;
    border-radius: 8px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

ARQ_USUARIOS = "usuarios.csv"
PASTA_DADOS = "banco_dados"

if not os.path.exists(PASTA_DADOS):
    os.makedirs(PASTA_DADOS)

# =========================
# USUÁRIOS
# =========================

def carregar_usuarios():
    if os.path.exists(ARQ_USUARIOS):
        return pd.read_csv(ARQ_USUARIOS)
    else:
        df = pd.DataFrame([{
            "usuario": "Admlolo",
            "senha": "lolo10",
            "ativo": True,
            "tipo": "admin"
        }])
        df.to_csv(ARQ_USUARIOS, index=False)
        return df

def salvar_usuarios(df):
    df.to_csv(ARQ_USUARIOS, index=False)

def autenticar(usuario, senha):
    usuarios = carregar_usuarios()
    usuarios["usuario"] = usuarios["usuario"].astype(str).str.strip()
    usuarios["senha"] = usuarios["senha"].astype(str).str.strip()
    usuarios["ativo"] = usuarios["ativo"].astype(str).str.lower().str.strip()

    user = usuarios[
        (usuarios["usuario"] == usuario.strip()) &
        (usuarios["senha"] == senha.strip()) &
        (usuarios["ativo"] == "true")
    ]

    if not user.empty:
        return user.iloc[0]["tipo"]

    return None

# =========================
# CAMINHOS
# =========================

def caminho(usuario, tipo):
    return os.path.join(PASTA_DADOS, f"{usuario}_{tipo}.csv")

# =========================
# DADOS
# =========================

def carregar_dados(usuario):
    if os.path.exists(caminho(usuario,"dados")):
        return pd.read_csv(caminho(usuario,"dados"))
    return pd.DataFrame(columns=["Equipe","Colocacao","Kill","TOTAL"])

def salvar_dados(usuario, df):
    df.to_csv(caminho(usuario,"dados"), index=False)

# =========================
# CONFIG
# =========================

def carregar_config(usuario):
    if os.path.exists(caminho(usuario,"config")):
        return pd.read_csv(caminho(usuario,"config")).iloc[0]
    return {"nome_ranking":"🏆 Ranking Oficial","cor_tabela":"#1f2937"}

def salvar_config(usuario, nome, cor):
    df = pd.DataFrame([{
        "nome_ranking": nome,
        "cor_tabela": cor
    }])
    df.to_csv(caminho(usuario,"config"), index=False)

# =========================
# HISTÓRICO
# =========================

def salvar_campeonato(usuario, nome_campeonato, df):
    if df.empty or nome_campeonato.strip()=="":
        return

    df_hist = df.copy()
    df_hist["Campeonato"] = nome_campeonato
    df_hist["Data"] = datetime.now().strftime("%d/%m/%Y %H:%M")

    if os.path.exists(caminho(usuario,"historico")):
        antigo = pd.read_csv(caminho(usuario,"historico"))
        df_hist = pd.concat([antigo, df_hist], ignore_index=True)

    df_hist.to_csv(caminho(usuario,"historico"), index=False)

def carregar_historico(usuario):
    if os.path.exists(caminho(usuario,"historico")):
        return pd.read_csv(caminho(usuario,"historico"))
    return pd.DataFrame()

# =========================
# CONTROLE LOGIN
# =========================

if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario = None
    st.session_state.tipo = None

# =========================
# LOGIN
# =========================

if not st.session_state.logado:

    st.markdown("<h1 style='text-align:center;'>⚔️ PLATAFORMA WARRIORS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Login</h3>", unsafe_allow_html=True)

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        tipo = autenticar(usuario, senha)
        if tipo:
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.session_state.tipo = tipo
            st.rerun()
        else:
            st.error("Login inválido ou usuário inativo.")

# =========================
# SISTEMA
# =========================

else:
    usuario = st.session_state.usuario

    st.sidebar.success(f"Logado como: {usuario}")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    # ================= ADMIN =================
    if st.session_state.tipo == "admin":

        st.title("👑 Painel Administrativo")

        usuarios = carregar_usuarios()

        usuarios["ativo"] = usuarios["ativo"].astype(str).str.lower().str.strip()

        st.subheader("🟢 Usuários Ativos")
        ativos = usuarios[usuarios["ativo"] == "true"]
        st.dataframe(ativos, use_container_width=True)

        st.subheader("🔴 Usuários Inativos")
        inativos = usuarios[usuarios["ativo"] == "false"]
        st.dataframe(inativos, use_container_width=True)

        st.markdown("---")

        # Criar usuário
        st.subheader("➕ Criar Novo Usuário")

        novo_user = st.text_input("Usuário")
        nova_senha = st.text_input("Senha")
        tipo_user = st.selectbox("Tipo", ["cliente", "admin"])

        if st.button("Criar Usuário"):
            if novo_user.strip() != "" and nova_senha.strip() != "":
                novo = pd.DataFrame([{
                    "usuario": novo_user.strip(),
                    "senha": nova_senha.strip(),
                    "ativo": True,
                    "tipo": tipo_user
                }])
                usuarios = pd.concat([usuarios, novo], ignore_index=True)
                salvar_usuarios(usuarios)
                st.success("Usuário criado!")
            else:
                st.warning("Preencha todos os campos.")

        st.markdown("---")

        # Ativar / Desativar
        st.subheader("🔄 Ativar / Desativar Usuário")

        usuario_select = st.selectbox(
            "Selecionar Usuário",
            usuarios["usuario"].tolist()
        )

        novo_status = st.selectbox("Status", ["true", "false"])

        if st.button("Atualizar Status"):
            usuarios.loc[usuarios["usuario"] == usuario_select, "ativo"] = novo_status
            salvar_usuarios(usuarios)
            st.success("Status atualizado!")

    # ================= CLIENTE =================
    else:
        col1, col2 = st.columns([6, 1])

        with col1:
            st.title("🎮 Painel do Usuário")

        with col2:
            if st.button("📜", help="Ver histórico"):
                st.session_state.ver_historico = True

        config = carregar_config(usuario)

        # CONFIG
        st.sidebar.subheader("⚙️ Configurações")

        nome_ranking = st.sidebar.text_input(
            "Nome do Ranking",
            config["nome_ranking"]
        )

        cor_tabela = st.sidebar.color_picker(
            "Cor da Tabela",
            config["cor_tabela"]
        )

        num_quedas = st.sidebar.slider("Quantidade de Quedas", 1, 15, 3)

        if st.sidebar.button("Salvar Configurações"):
            salvar_config(usuario, nome_ranking, cor_tabela)
            st.success("Configurações salvas!")

        # FORM
        st.subheader("➕ Adicionar Equipe")

        pontuacao = {
            1:12,2:9,3:8,4:7,5:6,6:5,
            7:4,8:3,9:2,10:1,11:0,12:0
        }

        df = carregar_dados(usuario)

        with st.form("form_equipe"):
            nome = st.text_input("Nome da Equipe")

            pontos_col_total = 0
            pontos_kill_total = 0

            for i in range(1, num_quedas+1):
                col1, col2 = st.columns(2)
                colocacao = col1.number_input(f"Colocação - Queda {i}",1,12,key=f"col_{i}")
                kill = col2.number_input(f"Kill - Queda {i}",0,key=f"kill_{i}")

                pontos_col_total += pontuacao[colocacao]
                pontos_kill_total += kill

            if st.form_submit_button("Adicionar") and nome.strip()!="":
                total = pontos_col_total + pontos_kill_total
                nova = pd.DataFrame([{
                    "Equipe":nome,
                    "Colocacao":pontos_col_total,
                    "Kill":pontos_kill_total,
                    "TOTAL":total
                }])
                df = pd.concat([df,nova],ignore_index=True)
                salvar_dados(usuario,df)
                st.success("Equipe adicionada!")

        # RANKING
        if not df.empty:

            df = df.sort_values("TOTAL",ascending=False).reset_index(drop=True)
            df.index += 1

            def medalha(pos):
                if pos==1: return "🥇"
                if pos==2: return "🥈"
                if pos==3: return "🥉"
                return ""

            df["🏅"] = df.index.map(medalha)
            df = df[["🏅","Equipe","Colocacao","Kill","TOTAL"]]

            st.markdown(
                f"<h2 style='text-align:center;'>{nome_ranking}</h2>",
                unsafe_allow_html=True
            )

            def estilo(row):
                if row.name==0:
                    return ['background-color: gold; color: black;']*len(row)
                return [f'background-color:{cor_tabela}; color:white;']*len(row)

            styled = df.style.apply(estilo,axis=1)
            st.dataframe(styled,use_container_width=True)
            st.markdown("#### 🗑 Excluir equipe")

            if not df.empty:
                equipe_excluir = st.selectbox(
                    "Selecione a equipe para excluir",
                    df["Equipe"].tolist(),
                    key="excluir_equipe"
                )

                if st.button("Excluir", key="btn_excluir"):
                    df = df[df["Equipe"] != equipe_excluir]

                    # recalcular ranking
                    df = df.sort_values("TOTAL", ascending=False).reset_index(drop=True)

                    salvar_dados(usuario, df[["Equipe", "Colocacao", "Kill", "TOTAL"]])

                    st.success("Equipe removida com sucesso!")
                    st.rerun()

            st.markdown("---")

            nome_campeonato = st.text_input("Nome do Campeonato")

            if st.button("Finalizar Campeonato"):
                salvar_campeonato(usuario,nome_campeonato,df)
                salvar_dados(usuario,pd.DataFrame(columns=["Equipe","Colocacao","Kill","TOTAL"]))
                st.success("Campeonato salvo no histórico!")

if st.session_state.get("ver_historico"):

    st.markdown("## 📜 Histórico de Campeonatos")

    historico = carregar_historico(usuario)

    if historico.empty:
        st.info("Nenhum campeonato salvo ainda.")
    else:
        campeonatos = historico["Campeonato"].unique()

        campeonato_sel = st.selectbox(
            "Selecione o campeonato",
            campeonatos
        )

        dados_campeonato = historico[historico["Campeonato"] == campeonato_sel]

        st.dataframe(dados_campeonato, use_container_width=True)

    if st.button("Fechar histórico"):
        st.session_state.ver_historico = False
        st.rerun()
