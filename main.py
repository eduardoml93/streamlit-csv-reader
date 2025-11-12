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
    .section-title {{
        background: rgba(0, 0, 0, 0.5);
        padding: 10px;
        border-radius: 5px;
        color: white;
        font-size: 20px;
        font-weight: bold;
        margin: 20px 0 10px 0;
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
    st.markdown('<div class="title-box">Explorador CSV</div>', unsafe_allow_html=True)

    # Menu lateral para escolher página
    page = st.sidebar.radio("Escolha a Página:", ["📊 Gráficos", "📝 Análises e Estatísticas"])

    st.write("Você pode carregar um arquivo CSV do seu computador **ou** fornecer o link de um CSV online.")

    uploaded_file = st.file_uploader("Faça o upload do seu arquivo CSV", type=["csv"])
    
    # Colunas para URL e separador
    col1, col2 = st.columns([4, 1])
    with col1:
        csv_url = st.text_input("Ou insira a URL do CSV", placeholder="https://example.com/arquivo.csv", value=st.session_state.csv_url)
        st.session_state.csv_url = csv_url
    with col2:
        separator = st.text_input("Separador", value=st.session_state.separator)
        st.session_state.separator = separator

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

            # Resetar seleções
            st.session_state.col_hist = None
            st.session_state.col_x = None
            st.session_state.col_y = None
            st.session_state.col_cat = None

        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            st.session_state.df = None

    # -------------------
    # Se houver DataFrame carregado
    # -------------------
    if st.session_state.df is not None:
        if page == "📝 Análises e Estatísticas":
            st.write("### Informações sobre os Dados:")
            st.write("**Tipos de Dados:**")
            st.write(st.session_state.df.dtypes)
            
            st.write("**Valores Nulos por Coluna:**")
            st.write(st.session_state.df.isnull().sum())
            
            num_duplicados = st.session_state.df.duplicated().sum()
            st.metric(label="Número de Registros Duplicados", value=num_duplicados)

            st.write("**Número de Valores Únicos por Coluna:**")
            st.write(st.session_state.df.nunique())

            st.write("**Estatísticas Descritivas:**")
            st.write(st.session_state.df.describe())

            st.write("**Distribuição Percentual de Valores Nulos:**")
            st.write((st.session_state.df.isnull().sum() / len(st.session_state.df)) * 100)

        elif page == "📊 Gráficos":
            st.write("### Visualização dos Dados:")
            st.dataframe(st.session_state.df)

            num_cols = st.session_state.df.select_dtypes(include='number').columns
            cat_cols = st.session_state.df.select_dtypes(include='object').columns

            # Histograma
            if len(num_cols) > 0:
                st.markdown('<div class="section-title">📊 Distribuição - Histograma</div>', unsafe_allow_html=True)
                selected_hist = st.selectbox("Selecione a coluna numérica para histograma", num_cols, index=0, key="hist_select")
                fig_hist = px.histogram(st.session_state.df, x=selected_hist, nbins=20, title=f"Distribuição de {selected_hist}")
                st.plotly_chart(fig_hist, use_container_width=True)

            # Scatter Plot
            if len(num_cols) >= 2:
                st.markdown('<div class="section-title">🔍 Relação entre Variáveis - Scatter Plot</div>', unsafe_allow_html=True)
                selected_x = st.selectbox("Eixo X", num_cols, index=0, key="scatter_x")
                selected_y = st.selectbox("Eixo Y", num_cols, index=1, key="scatter_y")
                fig_scatter = px.scatter(st.session_state.df, x=selected_x, y=selected_y, title=f"{selected_x} vs {selected_y}")
                st.plotly_chart(fig_scatter, use_container_width=True)

            # Gráfico de Densidade 2D
            if len(num_cols) >= 2:
                st.markdown('<div class="section-title">🌡️ Densidade 2D - Heatmap de Concentração</div>', unsafe_allow_html=True)
                selected_density_x = st.selectbox("Eixo X para Densidade", num_cols, index=0, key="density_x")
                selected_density_y = st.selectbox("Eixo Y para Densidade", num_cols, index=1, key="density_y")
                
                fig_density = px.density_heatmap(st.session_state.df, x=selected_density_x, y=selected_density_y,
                                                title=f"Densidade 2D: {selected_density_x} vs {selected_density_y}")
                st.plotly_chart(fig_density, use_container_width=True)

            # Boxplot
            if len(num_cols) > 0:
                st.markdown('<div class="section-title">📦 Análise de Dispersão - Boxplot</div>', unsafe_allow_html=True)
                selected_box = st.selectbox("Coluna para Boxplot", num_cols, index=0, key="boxplot_select")
                fig_box = px.box(st.session_state.df, y=selected_box, title=f"Boxplot de {selected_box}")
                st.plotly_chart(fig_box, use_container_width=True)

            # Heatmap de correlação
            if len(num_cols) > 1:
                st.markdown('<div class="section-title">🔥 Correlação entre Variáveis - Heatmap</div>', unsafe_allow_html=True)
                corr = st.session_state.df[num_cols].corr()
                fig_heatmap = px.imshow(corr, text_auto=True, color_continuous_scale="RdBu_r", title="Mapa de Calor das Correlações")
                st.plotly_chart(fig_heatmap, use_container_width=True)

            # Gráfico de barras categórico
            if len(cat_cols) > 0:
                st.markdown('<div class="section-title">📊 Análise Categórica - Gráfico de Barras</div>', unsafe_allow_html=True)
                selected_cat = st.selectbox("Coluna categórica para contagem", cat_cols, index=0, key="bar_select")
                count_data = st.session_state.df[selected_cat].value_counts().reset_index()
                count_data.columns = [selected_cat, 'Quantidade']
                fig_bar = px.bar(count_data, x=selected_cat, y='Quantidade', title=f"Contagem de {selected_cat}")
                st.plotly_chart(fig_bar, use_container_width=True)

if __name__ == "__main__":
    main()
