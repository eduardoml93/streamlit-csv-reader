import streamlit as st
import pandas as pd
import base64
import requests
import plotly.express as px
from io import StringIO

# Função para carregar a imagem e convertê-la para base64
def get_base64_of_image(file):
    with open(file, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Definir o background com a imagem convertida em base64
def set_background(image_file="bg.jpeg", darkness=0.5):
    """
    darkness: valor de 0 a 1, sendo 0 sem escurecimento e 1 totalmente escuro
    """
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

# Definindo o background
set_background("bg.jpeg", darkness=0.5)

def main():
    st.markdown('<div class="title-box">CSV Reader APP</div>', unsafe_allow_html=True)

    st.write("Você pode carregar um arquivo CSV do seu computador **ou** fornecer o link de um CSV online.")

    uploaded_file = st.file_uploader("Faça o upload do seu arquivo CSV", type=["csv"])
    csv_url = st.text_input("Ou insira a URL do CSV", placeholder="https://example.com/arquivo.csv")

    separator = st.text_input("Informe o separador (padrão: ,)", value=",")

    df = None

    try:
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file, sep=separator)
        elif csv_url:
            response = requests.get(csv_url)
            if response.status_code == 200:
                csv_data = StringIO(response.text)
                df = pd.read_csv(csv_data, sep=separator)
            else:
                st.error("Não foi possível acessar o arquivo na URL fornecida.")

        if df is not None:
            st.write("### Visualização dos Dados:")
            st.dataframe(df)

            # -------------------
            # Histograma (numérico)
            # -------------------
            st.write("### Histograma")
            num_cols = df.select_dtypes(include='number').columns
            if len(num_cols) > 0:
                col_hist = st.selectbox("Selecione a coluna numérica para histograma", num_cols)
                fig_hist = px.histogram(df, x=col_hist, nbins=20, title=f"Distribuição de {col_hist}")
                st.plotly_chart(fig_hist, use_container_width=True)
            else:
                st.info("Não há colunas numéricas para histograma.")

            # -------------------
            # Gráfico de dispersão (numérico)
            # -------------------
            st.write("### Gráfico de Dispersão")
            if len(num_cols) >= 2:
                col_x = st.selectbox("Eixo X", num_cols, index=0)
                col_y = st.selectbox("Eixo Y", num_cols, index=1)
                fig_scatter = px.scatter(df, x=col_x, y=col_y, title=f"Dispersão: {col_x} vs {col_y}")
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("Não há colunas numéricas suficientes para dispersão.")

            # -------------------
            # Gráfico de barras para dados string
            # -------------------
            st.write("### Gráfico de Contagem (colunas categóricas)")
            cat_cols = df.select_dtypes(include='object').columns
            if len(cat_cols) > 0:
                col_cat = st.selectbox("Selecione a coluna categórica para contar valores", cat_cols)
                count_data = df[col_cat].value_counts().reset_index()
                count_data.columns = [col_cat, 'Quantidade']
                fig_bar = px.bar(count_data, x=col_cat, y='Quantidade', title=f"Contagem de {col_cat}")
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("Não há colunas categóricas (string) para gráfico de contagem.")

    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")

if __name__ == "__main__":
    main()





