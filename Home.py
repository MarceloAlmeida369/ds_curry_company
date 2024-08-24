import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🎲"
)

image_path = 'LOGO.png'
image = Image.open(image_path)
st.sidebar.image(image, width=90)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown("""___""")


st.write("# Curry Company Growth DashBoard")

st.header("Sobre o Dataset")
st.write("""
        <p style="text-align: justify;">
        O dataset utilizado neste dashboard foi disponibilizado por Gaurav Malik no Kaggle. 
        Ele contém informações detalhadas sobre entregas de alimentos, incluindo condições de tráfego, 
        clima e avaliações dos entregadores. Este conjunto de dados é ideal para análises que visam 
        melhorar o processo de entrega e otimizar o tempo de serviço das empresas de delivery.
        </p>
    """, unsafe_allow_html=True)

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
      - Visão Gerencial: Métricas gerais de comportamento.
      - Visão Tática: Indicadores semanais de crescimento.
      - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
      - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurante:
      - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Desenvolvido duranto a capacitação Cientista de Dados by Marcelo
    """
)

st.header("Sobre a Empresa")
# Criando duas colunas, a primeira para a imagem e a segunda para o texto
col1, col2 = st.columns([1, 3])  # O argumento [1, 3] ajusta a largura das colunas

with col1:
    image_path = 'LOGO.png'
    image = Image.open(image_path)
    st.image(image, width=150)

with col2:
    st.write("""
            <p style="text-align: justify;">
            A empresa que disponibilizou o dataset no Kaggle tem foco em melhorar o tempo de entrega de alimentos 
            através da análise de dados. Eles coletam e fornecem dados de entregas para ajudar empresas de delivery 
            a otimizar suas operações, reduzindo o tempo de entrega e melhorando a satisfação do cliente.
        """, unsafe_allow_html=True)

st.header("Sobre Mim")

# Criando duas colunas, a primeira para a imagem e a segunda para o texto
col1, col2 = st.columns([1, 3])  # O argumento [1, 3] ajusta a largura das colunas

with col1:
    image_path = 'photo.jpeg'
    image = Image.open(image_path)
    st.image(image, width=150)

with col2:
    st.write("""
        <p style="text-align: justify;">
        Sou Marcelo L. Almeida, um cientista de dados com interesse em análises que possam impactar positivamente 
        o desempenho das empresas. Este projeto é uma demonstração das capacidades de análise de dados 
        aplicadas ao setor de entregas de alimentos. Estou sempre em busca de novos desafios e oportunidades 
        para aplicar minhas habilidades em ciência de dados.
        </p>
    """, unsafe_allow_html=True)


st.sidebar.write('### Powered by Marcelo') 