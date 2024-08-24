# Visão 3.0 - visão dos Restaurantes

# ============================================================================
# Import Bibliotecas
# ============================================================================
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
from PIL import Image
import folium
from streamlit_folium import folium_static

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

st.set_page_config(
    page_title="Visão Restaurantes",
    page_icon="🍽️",
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

    # Convertendo a coluna Order_Date de texto para data
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
    st.header('Marketplace - Visão Restaurantes')

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

    # Aplicar os filtros
    date_slider_datetime = pd.to_datetime(date_slider)
    df_filtered = df_filtered[df_filtered['Order_Date'] < date_slider_datetime]
    df_filtered = df_filtered[df_filtered['Road_traffic_density'].isin(traffic_options)]
    df_filtered = df_filtered[df_filtered['Weatherconditions'].isin(weather_options)]

    # Layout Streamlit
    tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

    with tab1:
        with st.container():
            st.title('Overall Metrics')
            col1, col2, col3, col4, col5, col6 = st.columns(6)

            with col1:
                delivery_unique = len(df_filtered['Delivery_person_ID'].unique())
                col1.metric('Entregadores únicos', delivery_unique)

            with col2:
                cols = ['Delivery_location_latitude', 
                        'Delivery_location_longitude', 
                        'Restaurant_latitude', 
                        'Restaurant_longitude']

                df_filtered['distance'] = df_filtered.loc[:, cols].apply(lambda x: 
                    haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), 
                              (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
                
                avg_distance = np.round(df_filtered['distance'].mean(), 2)
                col2.metric('Distância média', avg_distance)

            with col3:
                df_aux = (df_filtered.loc[:, ['Time_taken(min)', 'Festival']]
                          .groupby('Festival')
                          .agg({'Time_taken(min)': ['mean','std']}))
                df_aux.columns = ['avg_time', 'std_time']
                df_aux = df_aux.reset_index()
                avg_time_yes = df_aux.loc[df_aux['Festival'] == 'Yes', 'avg_time']
                
                if not avg_time_yes.empty:
                    col3.metric('Tempo médio (Festival)', np.round(avg_time_yes.iloc[0], 2))
                else:
                    col3.metric('Tempo médio (Festival)', "N/A")

            with col4:
                std_time_yes = df_aux.loc[df_aux['Festival'] == 'Yes', 'std_time']
                
                if not std_time_yes.empty:
                    col4.metric('STD Entrega (Festival)', np.round(std_time_yes.iloc[0], 2))
                else:
                    col4.metric('STD Entrega (Festival)', "N/A")

            with col5:
                avg_time_no = df_aux.loc[df_aux['Festival'] == 'No', 'avg_time']
                
                if not avg_time_no.empty:
                    col5.metric('Tempo médio (Sem Festival)', np.round(avg_time_no.iloc[0], 2))
                else:
                    col5.metric('Tempo médio (Sem Festival)', "N/A")

            with col6:
                std_time_no = df_aux.loc[df_aux['Festival'] == 'No', 'std_time']
                
                if not std_time_no.empty:
                    col6.metric('STD Entrega (Sem Festival)', np.round(std_time_no.iloc[0], 2))
                else:
                    col6.metric('STD Entrega (Sem Festival)', "N/A")

        with st.container():
            st.markdown("""___""")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown('##### Tempo médio de entrega por cidade')
                df_aux = (df_filtered.loc[:, ['City', 'Time_taken(min)']]
                          .groupby('City')
                          .agg({'Time_taken(min)': ['mean', 'std']}))
                
                df_aux.columns = ['avg_time', 'std_time']
                df_aux = df_aux.reset_index()

                fig = go.Figure()
                fig.add_trace(go.Bar(name='Control',
                                     x=df_aux['City'],
                                     y=np.round(df_aux['avg_time'], 2),
                                     error_y=dict(type='data', array=np.round(df_aux['std_time'], 2))))
                    
                fig.update_layout(barmode='group')
                st.plotly_chart(fig)

            with col2:
                st.markdown('##### Distribuição da Distância')

                df_aux = (df_filtered.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                          .groupby(['City', 'Road_traffic_density'])
                          .agg({'Time_taken(min)': ['mean', 'std']}))
                
                df_aux.columns = ['avg_time', 'std_time']
                df_aux = df_aux.reset_index()
                
                # Aplicando np.round para mostrar apenas 2 casas decimais
                df_aux['avg_time'] = np.round(df_aux['avg_time'], 2)
                df_aux['std_time'] = np.round(df_aux['std_time'], 2)
                
                st.dataframe(df_aux)


        with st.container():
            st.markdown("""___""")
            st.title('Distribuição do Tempo')
            col1, col2 = st.columns(2)

            with col1:
                cols = ['Delivery_location_latitude', 
                        'Delivery_location_longitude', 
                        'Restaurant_latitude', 
                        'Restaurant_longitude']
                
                df_filtered['distance'] = df_filtered.loc[:, cols].apply(lambda x:
                    haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                              (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
                
                avg_distance = df_filtered.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()

                fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], 
                                             values=np.round(avg_distance['distance'], 2), 
                                             pull=[0, 0.1, 0])])
                
                st.plotly_chart(fig)

            with col2:
                cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
                df_aux = (df_filtered.loc[:, cols]
                          .groupby(['City', 'Road_traffic_density'])
                          .agg({'Time_taken(min)': ['mean', 'std']}))
                
                df_aux.columns = ['avg_time', 'std_time']
                df_aux = df_aux.reset_index()
                
                fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values=np.round(df_aux['avg_time'], 2),
                                  color=np.round(df_aux['std_time'], 2), color_continuous_scale='RdBu',
                                  color_continuous_midpoint=np.average(np.round(df_aux['std_time'], 2)))
                st.plotly_chart(fig)

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
