import streamlit as st
import pandas as pd

def main():
    st.title("CSV Reader App")
    
    uploaded_file = st.file_uploader("Faça o upload do seu arquivo CSV", type=["csv"])
    
    if uploaded_file is not None:
        separator = st.text_input("Informe o separador (padrão: ,)", value=",")
        
        try:
            df = pd.read_csv(uploaded_file, sep=separator)
            st.write("### Visualização dos Dados:")
            st.dataframe(df)
            
            st.write("### Informações sobre os Dados:")
            st.write("**Tipos de Dados:**")
            st.write(df.dtypes)
            
            st.write("**Valores Nulos por Coluna:**")
            st.write(df.isnull().sum())
            
            st.write("**Número de Registros Duplicados:**")
            st.write(df.duplicated().sum())

            st.write("**Número de Valores Únicos por Coluna:**")
            st.write(df.nunique())

            st.write("**Estatísticas Descritivas:**")
            st.write(df.describe())

            st.write("**Distribuição Percentual de Valores Nulos:**")
            st.write((df.isnull().sum() / len(df)) * 100)

            
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")

if __name__ == "__main__":
    main()
