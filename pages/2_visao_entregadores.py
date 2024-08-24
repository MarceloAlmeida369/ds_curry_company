# 2.0 Visão: Entregadores

# ============================================================================
# Import Bibliotecas
# ============================================================================
import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
st.set_page_config(
    page_title="Visão Entregadores",
    page_icon="🛵",
    layout='wide'
)
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# ============================================================================
# Funções de ETL
# ============================================================================

# Função para extrair os dados
def load_data(file_path):
    df = pd.read_csv(file_path)
    return df

# Função para transformar os dados
def clean_data(df):
    df1 = df.copy()

    # Convertendo a coluna Age de texto para número
    df1 = df1[df1['Delivery_person_Age'] != 'NaN '].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    df1 = df1[df1['Road_traffic_density'] != 'NaN '].copy()
    df1 = df1[df1['City'] != 'NaN '].copy()
    df1 = df1[df1['Festival'] != 'NaN '].copy()

    # Convertendo a coluna Ratings de texto para número decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # Convertendo a coluna order_date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # Convertendo multiple_deliveries de texto para número inteiro (int)
    df1 = df1[df1['multiple_deliveries'] != 'NaN '].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # Removendo os espaços dentro de strings/texto/object
    df1['ID'] = df1['ID'].str.strip()
    df1['Road_traffic_density'] = df1['Road_traffic_density'].str.strip()
    df1['Type_of_order'] = df1['Type_of_order'].str.strip()
    df1['Type_of_vehicle'] = df1['Type_of_vehicle'].str.strip()
    df1['City'] = df1['City'].str.strip()
    df1['Festival'] = df1['Festival'].str.strip()

    # Limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(str).apply(lambda x: x.split('(min) ')[1] if '(min)' in x else x)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].replace('nan', pd.NA)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].fillna(0).astype(int)

    return df1

# Função para exibir o layout e os gráficos
def display_dashboard(df_filtered):
    st.header('Marketplace - Visão Entregadores')

    image_path = 'LOGO.png'
    image = Image.open(image_path)
    st.sidebar.image(image, width=120)

    st.sidebar.markdown('# Curry Company')
    st.sidebar.markdown('### Fastest Delivery in Town')
    st.sidebar.markdown("""___""")

    # Definindo o date_slider
    date_slider = st.sidebar.slider(
        'Até qual valor?',
        value=pd.to_datetime('2022-04-13').date(),
        min_value=pd.to_datetime('2022-02-11').date(),
        max_value=pd.to_datetime('2022-04-06').date(),
        format='DD-MM-YYYY'
    )

    st.sidebar.markdown("""___""")

    traffic_options = st.sidebar.multiselect(
        'Quais as condições do trânsito?',
        ['Low', 'Medium', 'High', 'Jam'],
        default=['Low', 'Medium', 'High', 'Jam']
    )

    st.sidebar.markdown("""___""")

    weather_options = st.sidebar.multiselect(
        'Quais as condições climáticas?',
        ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms', 'conditions Fog'],
        default=['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms', 'conditions Fog']
    )

    st.sidebar.markdown("""___""")
    st.sidebar.markdown('### Powered by Marcelo')

    # Aplicar o filtro de data ao DataFrame original
    date_slider_datetime = pd.to_datetime(date_slider)
    df_filtered = df_filtered[df_filtered['Order_Date'] < date_slider_datetime]

    # Aplicar o filtro de condições de tráfego
    df_filtered = df_filtered[df_filtered['Road_traffic_density'].isin(traffic_options)]

    # Aplicar o filtro de condições de clima
    df_filtered = df_filtered[df_filtered['Weatherconditions'].isin(weather_options)]

    # Layout Streamlit
    tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

    with tab1:
        with st.container():
            st.title('Overall Metrics')
            col1, col2, col3, col4 = st.columns(4, gap='large')

            with col1:
                # A maior idade dos entregadores
                maior_idade = df_filtered['Delivery_person_Age'].max()
                col1.metric('Maior idade', maior_idade)

            with col2:
                # A menor idade dos entregadores
                menor_idade = df_filtered['Delivery_person_Age'].min()
                col2.metric('Menor idade', menor_idade)

            with col3:
                # A melhor condição do veículo
                melhor_veiculo = df_filtered['Vehicle_condition'].max()
                col3.metric('Melhor condição', melhor_veiculo)

            with col4:
                # A pior condição do veículo
                pior_veiculo = df_filtered['Vehicle_condition'].min()
                col4.metric('Pior condição', pior_veiculo)

        with st.container():
            st.markdown("""___""")
            st.title('Avaliações')

            col1, col2 = st.columns(2, gap='large')

            with col1:
                st.markdown('###### Avaliação média por Entregador')
                df_avg_rating_per_deliver = (df_filtered.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                             .groupby('Delivery_person_ID')
                                             .mean()
                                             .reset_index())
                st.dataframe(df_avg_rating_per_deliver)

            with col2:
                st.markdown('###### Avaliação média por Trânsito')

                df_avg_std_rating_by_traffic = (df_filtered.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                                .groupby('Road_traffic_density')
                                                .agg({'Delivery_person_Ratings': ['mean', 'std']}))
                
                df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
                
                # Aplicando np.round para mostrar apenas 2 casas decimais
                df_avg_std_rating_by_traffic['delivery_mean'] = np.round(df_avg_std_rating_by_traffic['delivery_mean'], 2)
                df_avg_std_rating_by_traffic['delivery_std'] = np.round(df_avg_std_rating_by_traffic['delivery_std'], 2)
                
                st.dataframe(df_avg_std_rating_by_traffic.reset_index())


                st.markdown('###### Avaliação média por Clima')

                df_avg_std_rating_by_weather = (df_filtered.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                                .groupby('Weatherconditions')
                                                .agg({'Delivery_person_Ratings': ['mean', 'std']}))
                
                df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']
                
                # Aplicando np.round para mostrar apenas 2 casas decimais
                df_avg_std_rating_by_weather['delivery_mean'] = np.round(df_avg_std_rating_by_weather['delivery_mean'], 2)
                df_avg_std_rating_by_weather['delivery_std'] = np.round(df_avg_std_rating_by_weather['delivery_std'], 2)
                
                st.dataframe(df_avg_std_rating_by_weather.reset_index())


        with st.container():
            st.markdown("""___""")
            st.title('Velocidade de Entrega')

            col1, col2 = st.columns(2, gap='large')

            with col1:
                st.markdown('###### Top Entregadores mais rápidos')
                df2 = (df_filtered.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                       .groupby(['City', 'Delivery_person_ID'])
                       .min()
                       .sort_values(['City', 'Time_taken(min)'], ascending=True)
                       .reset_index())

                df_aux1 = df2[df2['City'] == 'Metropolitian'].head(10)
                df_aux2 = df2[df2['City'] == 'Urban'].head(10)
                df_aux3 = df2[df2['City'] == 'Semi-Urban'].head(10)

                df3 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)
                st.dataframe(df3)

            with col2:
                st.markdown('###### Top Entregadores mais lentos')
                df2 = (df_filtered.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                       .groupby(['City', 'Delivery_person_ID'])
                       .max()
                       .sort_values(['City', 'Time_taken(min)'], ascending=False)
                       .reset_index())

                df_aux1 = df2[df2['City'] == 'Metropolitian'].head(10)
                df_aux2 = df2[df2['City'] == 'Urban'].head(10)
                df_aux3 = df2[df2['City'] == 'Semi-Urban'].head(10)

                df3 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index(drop=True)
                st.dataframe(df3)

        # Novo container para exibir dados de clima
        with st.container():
            st.markdown("""___""")
            st.title('Condições Climáticas')

            col1, col2 = st.columns(2, gap='large')

            with col1:
                st.markdown('###### Entregadores em Climas Específicos')
                df_weather = df_filtered.groupby('Weatherconditions')['Delivery_person_ID'].nunique().reset_index()
                df_weather.columns = ['Condições Climáticas', 'Número de Entregadores']
                st.dataframe(df_weather)

            with col2:
                st.markdown('###### Avaliação Média por Clima')

                df_avg_rating_weather = df_filtered.groupby('Weatherconditions')['Delivery_person_Ratings'].mean().reset_index()
                df_avg_rating_weather.columns = ['Condições Climáticas', 'Avaliação Média']
                
                # Aplicando np.round para mostrar apenas 2 casas decimais
                df_avg_rating_weather['Avaliação Média'] = np.round(df_avg_rating_weather['Avaliação Média'], 2)
                
                st.dataframe(df_avg_rating_weather)


# ============================================================================
# Função principal
# ============================================================================
def main():
    # Extração dos dados
    df = load_data('dataset/train.csv')

    # Transformação dos dados
    df_filtered = clean_data(df)

    # Exibir dashboard
    display_dashboard(df_filtered)

if __name__ == "__main__":
    main()
