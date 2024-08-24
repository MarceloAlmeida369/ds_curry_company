#1.0 - Visão empresa 
#========================================================================
#Import Bibliotecas
#========================================================================
import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

#========================================================================
# Funções de ETL
#========================================================================

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

# Função para exibir os gráficos e o layout
def display_dashboard(df_filtered):
    st.header('Marketplace - Visão Cliente')

    image_path = 'LOGO.png'
    image = Image.open(image_path)
    st.sidebar.image(image, width=120)

    st.sidebar.markdown('# Curry Company')
    st.sidebar.markdown('### Fastest Delivery in Town')
    st.sidebar.markdown("""___""")

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
    st.sidebar.markdown('### Powered by Marcelo')

    # Aplicar o filtro de data ao DataFrame original
    date_slider_datetime = pd.to_datetime(date_slider)
    df_filtered = df_filtered[df_filtered['Order_Date'] < date_slider_datetime]

    # Aplicar o filtro de condições de tráfego
    df_filtered = df_filtered[df_filtered['Road_traffic_density'].isin(traffic_options)]

    tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

    with tab1:
        with st.container():
            df_aux = df_filtered.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
            df_aux.columns = ['order_date', 'qtde_entregas']
            fig = px.bar(df_aux, x='order_date', y='qtde_entregas')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("""___""")

        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('# Traffic Order Share')
                columns = ['ID', 'Road_traffic_density']
                df_aux = df_filtered.loc[:, columns].groupby('Road_traffic_density').count().reset_index()
                df_aux['perc_ID'] = 100 * (df_aux['ID'] / df_aux['ID'].sum())
                fig = px.pie(df_aux, values='perc_ID', names='Road_traffic_density')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown('# Traffic Order City')
                columns = ['ID', 'City', 'Road_traffic_density']
                df_aux = df_filtered.loc[:, columns].groupby(['City', 'Road_traffic_density']).count().reset_index()
                df_aux['perc_ID'] = 100 * (df_aux['ID'] / df_aux['ID'].sum())
                fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='ID')
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        with st.container():
            st.markdown("# Order by Week")
            df_filtered['week_of_year'] = df_filtered['Order_Date'].dt.strftime('%U')
            df_aux = df_filtered.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
            fig = px.line(df_aux, x='week_of_year', y='ID')
            st.plotly_chart(fig, use_container_width=True)

        with st.container():
            st.markdown("# Order Share by Week")
            df_aux1 = df_filtered.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
            df_aux2 = df_filtered.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()
            df_aux = pd.merge(df_aux1, df_aux2, how='inner')
            df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
            fig = px.line(df_aux, x='week_of_year', y='order_by_delivery')
            st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.markdown("# Country Maps")
        colunas = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df_aux = df_filtered[colunas].groupby(['City', 'Road_traffic_density']).median().reset_index()
        df_aux = df_aux.dropna(subset=['City', 'Road_traffic_density'])
        mapa = folium.Map(zoom_start=11)
        for _, info in df_aux.iterrows():
            folium.Marker(
                location=[info['Delivery_location_latitude'], info['Delivery_location_longitude']],
                popup=f"Cidade: {info['City']}, Tráfego: {info['Road_traffic_density']}"
            ).add_to(mapa)
        folium_static(mapa, width=1024, height=600)

#========================================================================
# Função principal
#========================================================================
def main():
    st.set_page_config(page_title="Visão Empresa", page_icon="📈",
    layout='wide')

    # ETL
    df = load_data('dataset/train.csv')
    df_filtered = clean_data(df)

    # Exibir dashboard
    display_dashboard(df_filtered)

if __name__ == "__main__":
    main()
