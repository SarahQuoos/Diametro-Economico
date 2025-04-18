import streamlit as st
#from st_aggrid import AgGrid
import openpyxl
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
st.markdown("###")

def Main():
    ########Access database########
    sheet_material = pd.read_excel('Banco de Dados.xlsx', sheet_name=material)

    #Dados diâmetro interno
    inner_diameter_aux = sheet_material['Diâmetro interno'].tolist()
    inner_diameter = np.array(inner_diameter_aux)

    #Dados diâmetro externo
    external_diameter_aux = sheet_material['Diâmetro externo'].tolist()
    external_diameter = np.array(external_diameter_aux)
    
    #Dados diâmetro nominal
    nominal_diameter_aux = sheet_material['Diâmetro externo'].tolist()
    nominal_diameter = np.array(nominal_diameter_aux)
    
    #Dados preço da tubulação
    pipe_cost_aux = sheet_material['Valor metro'].tolist()
    pipe_cost = np.array(pipe_cost_aux)
    
    #Dados b
    trench_base_aux = sheet_material['Base vala'].tolist()
    trench_base = np.array(trench_base_aux)
    
    #Dados Pf
    trench_length_aux = sheet_material['Profundidade vala'].tolist()
    trench_length = np.array(trench_length_aux)
    
    #Dados h
    #trench_height_aux = sheet_material['Altura vala'].tolist()
    #trench_height = np.array(trench_height_aux)
    
    #Dados m
    trench_ratio_aux = sheet_material['Proporção vala'].tolist()
    trench_ratio = np.array(trench_ratio_aux)
    
    #Dados preço excavação
    excavation_price_aux = sheet_material['Preço escavação [R$/m3]'].tolist()
    excavation_price = np.array(excavation_price_aux)
    
    #Dados preço aterro
    dig_price_aux = sheet_material['Preço do aterro [R$/m3]'].tolist()
    dig_price = np.array(dig_price_aux)
    
    #Dados distância bota-fora
    bt_distance_aux = sheet_material['Distância do bota-fora [km]'].tolist()
    bt_distance = np.array(bt_distance_aux)
    
    #Dados preço transporte
    transporte_price_aux = sheet_material['Preço do transporte [R$/(m3*km)]'].tolist()
    transporte_price = np.array(transporte_price_aux)
    
    #Dados rugosidade
    roughness = sheet_material.loc[0, 'Rugosidade [mm]']
    
    ########Cálculos########
    pi = np.pi
    area = (pi * ((inner_diameter/1000)**2))/4 
                    
    speed = (flow/3600)/area
                    
    #Dados da agua
    water_specific_mass = 998 #massa específica [kg/m³]
    water_dynamic_viscosity = 0.001 #viscosidade dinamica [Nm²/s]
                                      
    reynolds = (water_specific_mass*(inner_diameter/1000)*speed)/water_dynamic_viscosity
                        
    #Fator de atrito
    f = (-1.8*np.log10(((roughness/inner_diameter)/3.7)**1.11 + (6.9/reynolds)))**-2
                        
    #Perdas de carga distribuída
    gravity = 9.81 #gravidade [m²/s]
    major_pressure_loss = f*((length*speed**2)/((inner_diameter/1000)*2*gravity))
                    
    #Perdas de carga localizada
    minor_pressure_loss = major_pressure_loss*0.1
                    
    #Perda de carga total
    total_pressure_losses = major_pressure_loss + minor_pressure_loss
                    
    #Cota do nível de água
    water_level = max_water_level - min_water_level
    
    #Altura manométrica*************
    manometric_height = total_pressure_losses + water_level
                    
    #Rendimento global da estação
    global_efficiency = 0.70
                    
    #Potência requerida pela estação elevatória*********
    required_power = (gravity*(flow/3600)*manometric_height)/global_efficiency
    
    #Volume de escavação
    diameter_meters = external_diameter/1000
    excavation_volume = (diameter_meters+(trench_base - diameter_meters)+trench_ratio*(diameter_meters + trench_length))*(diameter_meters + trench_length) 
                    
    #Volume do aterro
    dig_volume = excavation_volume - ((pi * diameter_meters**2)/4)
    
    #Preço do aterro
    dig_price_meter = dig_volume*dig_price
    
    #Preço da escavação
    excavation_price_meter = excavation_volume*excavation_price
              
    #Bota-fora
    bt_volume = 1.3 * ((pi * diameter_meters**2)/4)
                    
    #Preço bota-fora
    bt_price_meter = bt_volume*transporte_price*bt_distance
            
    #Custo de montagem
    assembly_cost = excavation_price_meter + dig_price_meter + bt_price_meter
    
    #Custo de implantação
    implementation_cost = (pipe_cost + assembly_cost)
    
    #Número de horas de bombeamento
    pump_work_hours = 21.0
    
    #Coeficiente de atualização da energia
    Fa=0.16
    
    #Custo da energia elétrica
    p=0.63
    
    #Custo total
    total_cost_meter = implementation_cost*((9.81*flow*(water_level+total_pressure_losses)*pump_work_hours*Fa*p)/global_efficiency)
    total_cost = total_cost_meter*length
    
    ########Encontrando Diâmetro Econômico########       
    min_total_cost = min(total_cost) 
    list_size = len(total_cost)
    
    i = 0
        
    while i <= list_size:
        if total_cost[i] == min_total_cost:
            economic_diameter = nominal_diameter[i]
            economic_implementation_cost = implementation_cost[i] 
            #economic_dig_price = dig_price_meter[i]
            #economic_excavation_price = excavation_price_meter[i]
            #economic_bt_price = bt_price_meter[i]
            break
        else:
            i = i + 1

    ########Gráficos e Resultados########
    #line_chart, pizza_chart = st.columns(2)
    
    #Gráfico Linha
    #with line_chart:
    st.markdown("### Custo Total[R$/m] x Diâmetro Nominal[mm]")
    chart_data = {'Custo Total': total_cost_meter, 'Diâmetro nominal': nominal_diameter}
    st.line_chart(chart_data, x="Diâmetro nominal", y="Custo Total",height=500)
    
    #Gráfico Pizza
    #with pizza_chart:
     #   st.markdown("### Relação entre custos")
     #   labels = 'Preço do aterro', 'Preço de excavação', 'Preço bota-fora'
     #   sizes = [economic_dig_price, economic_excavation_price, economic_bt_price]
     #   fig1, ax1 = plt.subplots()
     #   ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=70, normalize=True,)
     #   st.pyplot(fig1)
        
    #Results table
    st.markdown("### Resultados")
    
    tab1, tab2, tab3 = st.columns(3)
    tab1.metric(label="Diâmetro Nominal Econômico [mm]", value=economic_diameter,)
    tab2.metric(label="Custo de Implementação[R$/m]", value=f"{round(economic_implementation_cost,2)} ",)
    tab3.metric(label="Custo Total [R$]", value=f"{round(min_total_cost,2)} ",)
    st.markdown("###") 
    
    #Visualização da tabela           
    #if st.checkbox("Mostrar tabela de cálculos"):
    #st.write(st.session_state.test)
    st.markdown("### Tabela")
    
    #data_table = {'Diametro interno': inner_diameter, 'Diametro nominal': nominal_diameter,'Area': area, 'Velocidade': speed, 'Reynolds': reynolds, 
    #              'Fator de atrito': f,'Perda de carga distribuída': major_pressure_loss, 'Perda de carga localizada': minor_pressure_loss,
    #              'Perda de carga total': total_pressure_losses, 'Altura manométrica': manometric_height, 'Potência requerida': required_power,
    #              'Volume de escavação': excavation_volume, 'Preço da escavação [R$/m]': excavation_price_meter,
    #              'Volume de aterro': dig_volume,'Preço do aterro [R$/m]':dig_price_meter,'Volume bota-fora': bt_volume,'Preço bota-fora': bt_price_meter}
    data_table = {'Diametro interno': inner_diameter, 'Diametro nominal': nominal_diameter,'Area': area, 'Velocidade': speed, 'Reynolds': reynolds, 
                  'Fator de atrito': f, 'Diametro nominal': nominal_diameter,'Perda de carga distribuída': major_pressure_loss, 
                  'Perda de carga localizada': minor_pressure_loss,
                  'Perda de carga total': total_pressure_losses, 'Nivel agua': water_level, 'Custo de montagem': assembly_cost,
                  'Custo tubo': pipe_cost, 'Custo de implementação': implementation_cost, 'Custo total': total_cost} 
                
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
    Main()
