import streamlit as st
#from st_aggrid import AgGrid
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#Streamlit page config
st.set_page_config(
    page_title="Dimensionamento Diâmetro Econômico",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# Desenvolvido por Sarah Quoos e Edgar Silva. UTFPR, Curitiba, PR, 2025"}
    )

#Page Title
st.title("Dimensionamento de Diâmetro Econômico de Adutoras em Estações Elevatórias de Água")

#Access database rotine
def Accessing_database():
    sheet_material = pd.read_excel('Banco de Dados.xlsx', sheet_name=material)

    inner_diameter_aux = sheet_material['Diâmetro interno'].tolist()
    inner_diameter = np.array(inner_diameter_aux)

    nominal_diameter_aux = sheet_material['Diâmetro nominal'].tolist()
    nominal_diameter = np.array(nominal_diameter_aux)
    
    roughness = sheet_material.loc[0, 'Rugosidade [mm]']
    return inner_diameter, nominal_diameter, roughness


#Main rotine
def Main():
    
    #Area
    pi = np.pi
    area = (pi * ((inner_diameter/1000)**2))/4 
                    
    #Velocidade media
    speed = (flow/3600)/area
                    
    #Dados da agua
    water_specific_mass = 998 #massa específica [kg/m³]
    water_dynamic_viscosity = 0.001 #viscosidade dinamica [m²/s]
                                      
    #Número de Reynolds
    reynolds = (water_specific_mass*(inner_diameter/1000)*speed)/water_dynamic_viscosity
                        
    #Fator de atrito
    f = (-1.8*np.log10(((roughness/inner_diameter)/3.7)**1.11 + (6.9/reynolds)))**-2
                        
    #Perdas de carga distribuída
    gravity = 9.81 #gravidade [m²/s]
    major_pressure_loss = (f*length*speed**2)/((inner_diameter/1000)*2*gravity)
                    
    #Perdas de carga localizada
    minor_pressure_loss = major_pressure_loss*0.1
                    
    #Perda de carga total
    total_pressure_losses = major_pressure_loss + minor_pressure_loss
                    
    #Cota do nível de água
    water_level = max_water_level - min_water_level
    
    #Altura manométrica
    manometric_height = total_pressure_losses + water_level
                    
    #Rendimento global
    global_efficiency = 0.70
                    
    #Potência requerida pela estação elevatória
    required_power = (9.8*(flow/3600)*manometric_height)/global_efficiency
                           
          
    #Encontrando Valores Econômicos       
    min_nominal_diameter = min(nominal_diameter) 
    tam = len(nominal_diameter)
        
    i = 0
        
    while i <= tam:
        d1 = nominal_diameter[i]
        if d1 == min_nominal_diameter:
            extenal_diameter = min_nominal_diameter
            We = required_power[i]
            hfe = major_pressure_loss[i]
            hle = minor_pressure_loss[i]
            hte = total_pressure_losses[i] 
            break
        else:
            i = i + 1

    #Gráficos e Resultados
    line_chart, pizza_chart = st.columns(2)
    
    #Gráfico Linha
    with line_chart:
        st.markdown("### Potência Requerida[W] x Diâmetro Nominal[mm]")
        chart_data = {'Potencia Requerida': required_power, 'Diâmetro nominal': nominal_diameter}
        st.line_chart(chart_data, x="Diâmetro nominal", y="Potencia Requerida",height=500)
    
    #Gráfico Pizza
    with pizza_chart:
        st.markdown("### Relação entre Perdas de Carga")
        labels = 'Perdas de carga distribuída', 'Perdas de carga localizada', 'Perda total'
        sizes = [hfe, hle, hte]
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, normalize=True,)
        st.pyplot(fig1)
    
    #Results table
    st.markdown("### Resultados para o menor diâmetro")
    
    tab1, tab2, tab3, tab4, tab5 = st.columns(5)
    tab1.metric(label="Diâmetro Econômico", value=extenal_diameter,)
    tab2.metric(label="Potência Requerida", value=f"{round(We,2)} ",)
    tab3.metric(label="Perdas de carga distribuída", value=f" {round(hfe,2)} ",)
    tab4.metric(label="Perdas de carga localizada", value=f" {round(hle,2)} ",)
    tab5.metric(label="Perdas de carga total", value=f" {round(hte,2)} ",)
    
    #Botões/Opções de visualização           
    if st.checkbox("Mostrar tabela de cálculos"):
        st.write(st.session_state.test)
        data_table = {'Diametro interno': inner_diameter, 'Area': area, 'Velocidade': speed, 'Reynolds': reynolds, 'Fator de atrito': f,
                      'Perda de carga distribuída': major_pressure_loss, 'Perda de carga localizada': minor_pressure_loss, 
                      'Perda de carga total': total_pressure_losses, 'Altura manométrica': manometric_height, 'Potência requerida': required_power}
        calculations_table = pd.DataFrame(data_table)
        st.table(calculations_table)
                          
#Loop principal
submit_button_check = 0
with st.sidebar:
    st.title("Dados de entrada")
    with st.form(key='Dados de entrada'):
        flow = st.number_input('Vazão requerida em m³/h')
        length = st.number_input('Comprimento da adutora em metros:')
        min_water_level = st.number_input('Cota do nível de água mínimo no poço de sucção do bombeamento em metros:')
        max_water_level = st.number_input('Cota do nível de água máximo no reservatório elevado em metros:')  
        material = st.selectbox("Material da tubulação?",("Select","Ferro Fundido", "PVC", "PRVF"),)
            
        button_submit, button_reset = st.columns(2)
        
        with button_submit:
            if st.form_submit_button("Submit"):
                if (flow == 0) or (length == 0) or (min_water_level == 0) or (max_water_level == 0) or (material == "Select"): 
                    st.write("Preencha todas as informações necessárias!")
                else:
                    submit_button_check = 1
        with button_reset:
            if st.form_submit_button("Reset"):
                submit_button_check = 0
                st.rerun()

if submit_button_check == 1:
    inner_diameter, nominal_diameter, roughness = Accessing_database()
    Main()
