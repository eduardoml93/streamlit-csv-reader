import streamlit as st
import pandas as pd
import base64
import requests
from io import StringIO
import plotly.express as px

# Função para carregar a imagem e converter para base64
def get_base64_of_image(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Função para definir o background com escurecimento
def set_background(image_file="bg.jpeg", darkness=0.5):
    base64_str = get_base64_of_image(image_file)
    css = f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,{darkness}), rgba(0,0,0,{darkness})), 
                          url("data:image/jpeg;base64,{base64_str}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .title-box {{
        background: rgba(0, 0, 0, 0.3);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-size: 28px;
        font-weight: bold;
        width: 60%;
        margin: auto;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Inicializar Session State para armazenar o DataFrame e seleções
if 'df' not in st.session_state:
    st.session_state.df = None
if 'col_hist' not in st.session_state:
    st.session_state.col_hist = None
if 'col_x' not in st.session_state:
    st.session_state.col_x = None
if 'col_y' not in st.session_state:
    st.session_state.col_y = None
if 'col_cat' not in st.session_state:
    st.session_state.col_cat = None
if 'separator' not in st.session_state:
    st.session_state.separator = ","
if 'csv_url' not in st.session_state:
    st.session_state.csv_url = ""

# Aplicando o background
set_background("bg.jpeg", darkness=0.5)

def main():
    st.markdown('<div class="title-box">CSV Reader APP</div>', unsafe_allow_html=True)

    st.write("Você pode carregar um arquivo CSV do seu computador **ou** fornecer o link de um CSV online.")

    uploaded_file = st.file_uploader("Faça o upload do seu arquivo CSV", type=["csv"])
    
    # Criando duas colunas lado a lado
    col1, col2 = st.columns([4, 1])  # 4:1 para dar mais espaço para a URL e menos para o separador
    
    with col1:
        csv_url = st.text_input("Ou insira a URL do CSV", placeholder="https://example.com/arquivo.csv", value=st.session_state.csv_url)
        st.session_state.csv_url = csv_url
    
    with col2:
        separator = st.text_input("Separador", value=st.session_state.separator)
        st.session_state.separator = separator

    # Botão para carregar os dados
    if st.button("Carregar Dados"):
        try:
            if uploaded_file is not None:
                st.session_state.df = pd.read_csv(uploaded_file, sep=st.session_state.separator)
            elif st.session_state.csv_url:
                response = requests.get(st.session_state.csv_url)
                if response.status_code == 200:
                    csv_data = StringIO(response.text)
                    st.session_state.df = pd.read_csv(csv_data, sep=st.session_state.separator)
                else:
                    st.error("Não foi possível acessar o arquivo na URL fornecida.")
            else:
                st.warning("Por favor, envie um arquivo ou insira a URL do CSV.")
                return

            # Resetar seleções de colunas ao carregar novo arquivo
            st.session_state.col_hist = None
            st.session_state.col_x = None
            st.session_state.col_y = None
            st.session_state.col_cat = None

        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            st.session_state.df = None

    # Exibir os gráficos somente se houver um DataFrame carregado
    if st.session_state.df is not None:
        st.write("### Visualização dos Dados:")
        st.dataframe(st.session_state.df)

        # -------------------
        # Histograma (numérico)
        # -------------------
        st.write("### Histograma")
        num_cols = st.session_state.df.select_dtypes(include='number').columns
        if len(num_cols) > 0:
            st.session_state.col_hist = st.selectbox(
                "Selecione a coluna numérica para histograma",
                num_cols,
                index=num_cols.get_loc(st.session_state.col_hist) if st.session_state.col_hist in num_cols else 0
            )
            fig_hist = px.histogram(st.session_state.df, x=st.session_state.col_hist, nbins=20, title=f"Distribuição de {st.session_state.col_hist}")
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Não há colunas numéricas para histograma.")

        # -------------------
        # Gráfico de dispersão (numérico)
        # -------------------
        st.write("### Gráfico de Dispersão")
        if len(num_cols) >= 2:
            st.session_state.col_x = st.selectbox(
                "Eixo X",
                num_cols,
                index=num_cols.get_loc(st.session_state.col_x) if st.session_state.col_x in num_cols else 0
            )
            st.session_state.col_y = st.selectbox(
                "Eixo Y",
                num_cols,
                index=num_cols.get_loc(st.session_state.col_y) if st.session_state.col_y in num_cols else 1
            )
            fig_scatter = px.scatter(st.session_state.df, x=st.session_state.col_x, y=st.session_state.col_y, title=f"Dispersão: {st.session_state.col_x} vs {st.session_state.col_y}")
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("Não há colunas numéricas suficientes para dispersão.")

        # -------------------
        # Gráfico de barras para dados string
        # -------------------
        st.write("### Gráfico de Contagem (colunas categóricas)")
        cat_cols = st.session_state.df.select_dtypes(include='object').columns
        if len(cat_cols) > 0:
            st.session_state.col_cat = st.selectbox(
                "Selecione a coluna categórica para contar valores",
                cat_cols,
                index=cat_cols.get_loc(st.session_state.col_cat) if st.session_state.col_cat in cat_cols else 0
            )
            count_data = st.session_state.df[st.session_state.col_cat].value_counts().reset_index()
            count_data.columns = [st.session_state.col_cat, 'Quantidade']
            fig_bar = px.bar(count_data, x=st.session_state.col_cat, y='Quantidade', title=f"Contagem de {st.session_state.col_cat}")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Não há colunas categóricas (string) para gráfico de contagem.")

if __name__ == "__main__":
    main()
