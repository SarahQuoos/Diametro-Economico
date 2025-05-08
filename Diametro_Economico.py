import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import openpyxl
import xlsxwriter
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb

#Streamlit page config
st.set_page_config(
    page_title="Dimensionamento Diâmetro Econômico",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# Desenvolvido por Sarah Quoos e Edgar Silva. UTFPR, Curitiba, PR, 2025"}
    )

st.title("Dimensionamento de Diâmetro Econômico")

def Main():
    #Access database
    sheet_material = pd.read_excel('Banco de Dados.xlsx', sheet_name=material)

    inner_diameter_aux = sheet_material['Diâmetro interno'].tolist()
    inner_diameter = np.array(inner_diameter_aux)

    external_diameter_aux = sheet_material['Diâmetro externo'].tolist()
    external_diameter = np.array(external_diameter_aux)

    nominal_diameter_aux = sheet_material['Diâmetro nominal'].tolist()
    nominal_diameter = np.array(nominal_diameter_aux)

    pipe_cost_aux = sheet_material['Valor metro'].tolist()
    pipe_cost = np.array(pipe_cost_aux)

    trench_base_aux = sheet_material['Base vala'].tolist()
    trench_base = np.array(trench_base_aux)

    trench_length_aux = sheet_material['Profundidade vala'].tolist()
    trench_length = np.array(trench_length_aux)
  
    trench_ratio_aux = sheet_material['Proporção vala'].tolist()
    trench_ratio = np.array(trench_ratio_aux)
    
    excavation_price_aux = sheet_material['Preço escavação [R$/m3]'].tolist()
    excavation_price = np.array(excavation_price_aux)
    
    dig_price_aux = sheet_material['Preço do aterro [R$/m3]'].tolist()
    dig_price = np.array(dig_price_aux)

    bt_distance_aux = sheet_material['Distância do bota-fora [km]'].tolist()
    bt_distance = np.array(bt_distance_aux)
    
    transport_price_aux = sheet_material['Preço do transporte [R$/(m3*km)]'].tolist()
    transport_price = np.array(transport_price_aux)
    
    roughness = sheet_material.loc[0, 'Rugosidade [mm]']

    #Calculations
    pi = np.pi
    area = (pi * ((inner_diameter/1000)**2))/4          
    speed = (flow/3600)/area
    
    water_specific_mass = 998 #[kg/m³]
    water_dynamic_viscosity = 0.001 #[Nm²/s]
                                      
    reynolds = (water_specific_mass*(inner_diameter/1000)*speed)/water_dynamic_viscosity
                        
    f = (-1.8*np.log10(((roughness/inner_diameter)/3.7)**1.11 + (6.9/reynolds)))**-2
                        
    major_pressure_loss = f*((length*speed**2)/((inner_diameter/1000)*2*9.81))        
    minor_pressure_loss = major_pressure_loss*0.1
    total_pressure_losses = major_pressure_loss + minor_pressure_loss
                    
    water_level = max_water_level - min_water_level
    manometric_height = total_pressure_losses + water_level
    global_efficiency = 0.75
    required_power = (9.81*(flow/3600)*manometric_height)/global_efficiency
    
    diameter_meters = external_diameter/1000
    excavation_volume = (diameter_meters+(trench_base - diameter_meters)+trench_ratio*(diameter_meters + trench_length))*(diameter_meters + trench_length) 
    excavation_price_meter = excavation_volume*excavation_price
    
    dig_volume = excavation_volume - ((pi * diameter_meters**2)/4)
    dig_price_meter = dig_volume*dig_price
         
    bt_volume = 1.3 * ((pi * diameter_meters**2)/4)
    bt_price_meter = bt_volume*transport_price*bt_distance
            
    assembly_cost = excavation_price_meter + dig_price_meter + bt_price_meter
    implementation_cost = (pipe_cost + assembly_cost)
    
    pump_work_hours = 7665.0
    annual_interest_rate = 0.12
    energy_increase_rate = 0.06
    energy_coefficient = (((1 + energy_increase_rate)**project_lifespan - (1 + annual_interest_rate)**project_lifespan)/((1 + energy_increase_rate) - (1 + annual_interest_rate)))*(1/((1 + annual_interest_rate)**project_lifespan))
    
    operation_cost = (9.81*(flow/3600)*manometric_height*pump_work_hours*energy_coefficient*electricity_cost)/global_efficiency
   
    total_cost = (implementation_cost*length)+operation_cost
    total_cost_meter = total_cost/length
    
    #Get economic diameter       
    min_total_cost_meter = min(total_cost_meter) 
    list_size = len(total_cost_meter) 
    aux = 0
    
    while aux <= list_size:
        if total_cost_meter[aux] == min_total_cost_meter:
            economic_diameter = nominal_diameter[aux]
            economic_assembly_cost = assembly_cost[aux]
            economic_implementation_cost = implementation_cost[aux]
            economic_total_cost_meter = total_cost_meter[aux]
            break
        else:
            aux = aux + 1

    #Line Chart
    st.markdown("### Custo Total x Diâmetro Nominal ###")
    chart_data = {'Custo Total [R$/m]': total_cost_meter, 'Diâmetro Nominal [mm]': nominal_diameter}
    chart = px.line(chart_data, x="Diâmetro Nominal [mm]", y="Custo Total [R$/m]")
    chart.update_layout(width = 1500, height = 500)
    chart.update_yaxes(autorangeoptions=dict(minallowed=0))
    chart.update_xaxes(autorangeoptions=dict(minallowed=0),fixedrange=True)
    chart
    
    #Results table
    st.markdown("### Resultado")
    
    tab1, tab2 = st.columns(2)
    tab1.metric(label="Diâmetro Econômico ", value=f"{'{:,} mm'.format(economic_diameter)} ",)
    tab2.metric(label="Custo Total Estimado por Metro", value=f"{'R$ {:,.2f}'.format(economic_total_cost_meter)} ",)
    
    st.markdown("###") 
    
    data_table = {'Diâmetro Nominal [mm]': nominal_diameter,'Perda de Carga Total [m]': total_pressure_losses,
                  'Potência Requerida [W]': required_power,'Custo de Implantação [R$/m]': implementation_cost,
                  'Custo de Operação [R$]': operation_cost,'Custo Total [R$]': total_cost, 'Custo Total [R$/m]': total_cost_meter}

    calculations_table = pd.DataFrame(data_table)
    
    with st.expander("Visualizar Tabela Simplificada de Resultados"):
        st.dataframe(calculations_table.style.format(precision=2,decimal=",",thousands=".").applymap(lambda _: "background-color: LightSkyBlue;", subset=([aux], slice(None))))
        
#Main loop
submit_button_check = 0
with st.sidebar:
    st.title("Dados de entrada")
    with st.form(key='Dados de entrada'):
        flow = st.number_input('Vazão requerida em m³/h')
        length = st.number_input('Comprimento da adutora em metros:')
        min_water_level = st.number_input('Cota do nível de água mínimo no poço de sucção do bombeamento em metros:')
        max_water_level = st.number_input('Cota do nível de água máximo no reservatório elevado em metros:')  
        material = st.selectbox("Informe o material da tubulação?",("Select","Ferro Fundido", "PVC", "PRVF"),)
        
        electricity_cost = 0.75
        project_lifespan = 20
        
        with st.expander("Deseja informar o preço atual da energia elétrica em kWh?"):
            electricity_cost = st.number_input('', value=0.75)
        with st.expander("Deseja informar a vida útil do projeto em anos?"):    
            project_lifespan = st.number_input('', value=20)
            
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



def a_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data

vtncu = {1,2,3}
df_xlsx = a_excel(vtncu)
st.download_button(label='📥 Download Current Result',
                                data=df_xlsx ,
                                file_name= 'df_test.xlsx')
