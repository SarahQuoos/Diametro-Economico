import streamlit as st
from st_aggrid import AgGrid
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


#Configuração de Página
st.set_page_config(
    page_title="Dimensionamento Diâmetro Econômico",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# Desenvolvido por Sarah Quoos e Edgar Silva. UTFPR, Curitiba, PR, 2025"}
    )

#Título
st.title("Dimensionamento de Diâmetro Econômico de Adutoras em Estações Elevatórias de Água")

#Dados de Entrada
with st.sidebar:
    st.title("Dados de entrada")
    Q = st.number_input('Vazão requerida em m³/h', value=0)
    L = st.number_input('Comprimento da adutora em metros:', value=0)
    Namin = st.number_input('Cota do nível de água mínimo no poço de sucção do bombeamento em metros:', value=0)
    Namax = st.number_input('Cota do nível de água máximo no reservatório elevado em metros:', value=0)  
    M = st.selectbox("Material da tubulação?",("select","Ferro Fundido", "PVC", "PRVF"),)

#Acesso ao banco de dados
def Banco():
    sheet = pd.read_excel('Banco de Dados.xlsx', sheet_name=M)
    #Diâmetro interno
    diaux = sheet['Diâmetro interno'].tolist()
    di = np.array(diaux)
    #Diâmetro nominal
    dnaux = sheet['Diâmetro nominal'].tolist()
    dn = np.array(dnaux)
    #Rugosidade
    e = sheet.loc[0, 'Rugosidade [mm]']
    return di, dn, e


#Cálculos
def Calculos():
    
    #Area
    pi = np.pi
    A = (pi * ((di/1000)**2))/4 
                    
    #Velocidade media
    q = Q/3600
    U = q/A
                    
    #Dados da agua
    p = 998 #massa específica [kg/m³]
    u = 0.001 #viscosidade dinamica [m²/s]
                                      
    #Número de Reynolds
    Re =  (p * (di/1000) * U)/u
                        
    #Fator de atrito
    f = (-1.8*np.log10(((e/di)/3.7)**1.11 + (6.9/Re)))**-2
                        
    #Perdas de carga distribuída
    g = 9.81 #gravidade [m²/s]
    hf = (f * L* U**2)/((di/1000) * 2 * g)
                    
    #Perdas de carga localizada
    hl = hf * 0.1
                    
    #Perda de carga total
    ht = hf + hl
                    
    #Altura manométrica
    hg = Namax - Namin
    hm = hg + ht
                    
    #Rendimento global
    ng = 0.70
                    
    #Potência requerida pela estação elevatória
    W = (9.8 * q * hm)/ng
                           
    #Volume de escavação 
    #Pf = Edgar
    #Ve = (di + 2 * L + m * (di + Pf)) * (di + Pf) 
                    
    #Volume para aterro da vala
    #Va = Ve - ((pi * di**2)/4)
                    
    #Bota-fora
    #Vbf = 1.3 * ((pi * d**2)/4)
                    
    #Área de reposição pavimento
    #m = Inclinação da vala, Edgar
    #Ar = 2 * m * (di + Pf) + 2 * L + d
                    
    #Custo de montagem
    #Md = (Ve * Pe) + (Va * Pa) + (Vbf * Pbf) + (Ar * Pr)
                    
    #Custo de Implementação
    #Pd = Considerar só o preço do tubo
    #Cd = (Pd + Md) * L
                    
    #Coeficiente de atualização de energia
    #i= 0.12
    #e = taxa de aumento de energia, Edgar
    #n = 30 
    #Fa = (((1 + e)**n - (1 + i)**n)/((1 + e) - (1 + i)))*(1/((1 + i)**n))
                    
    #Custo total
    #Nb = número de horas, Edgar
    #p = 
    #Ct = Cd * L * ((9.81 * Q * hm * nb * p * Fa)/ng)
    
    #Botão mostrar resultados em forma de tabela
    if st.checkbox("Tabela Cálculos"):
            data_tab = {'Diametro interno': di, 'Area': A, 'Velocidade': U, 'Reynolds': Re, 'Fator de atrito': f,
                            'Perda de carga distribuída': hf, 'Perda de carga localizada': hl, 
                            'Perda de carga total': ht, 'Altura manométrica': hm, 'Potência requerida': W}
            tab = pd.DataFrame(data_tab)
            st.table(tab)
            
    #return Md, Cd, Pd, Ct
    return di, hf, hl, ht, W
    
            
#Encontrando Valores Econômicos       
def Economico():
    
    dnmin = min(dn) 
    tam = len(dn)
        
    i = 0
        
    while i <= tam:
        d1 = dn[i]
        if d1 == dnmin:
            de = dnmin
            We = W[i]
            hfe = hf[i]
            hle = hl[i]
            hte = ht[i] 
            break
        else:
            i = i + 1

    #Ctmin = min(Ct)
    #tam = len(Ct)
    
    #i = 0
        
    #while i <= tam:
        #Ct1 = Ct[i]
        #if Ct1 == Ctmin:
            #Cte = Ctmin
            #st.write(Cte)
            #Mde = Md[i]
            #st.write(Mde)
            #Cde = Cd[i]
            #st.write(Cde)
            #Pde = Pd[i] 
            #st.write(Pde)
            #de = d[i]
            #st.write(de)
        #else:
           #i = i + 1 

    #return Cte, Mde, Cde, Pde, de    
    return hfe, hle, hte, de, We

#Gráficos e Resultados
def Resultado():
    
    graf_1, graf_2 = st.columns(2)
    
    #Gráfico Linha
    with graf_1:
        st.markdown("### Potência Requerida x Diâmetro")
        chart_data = {'Potencia Requerida': W, 'Diâmetro nominal': dn}
        st.line_chart(chart_data, x="Diâmetro nominal", y="Potencia Requerida",height=500)
    
    #Gráfico Pizza
    with graf_2:
        st.markdown("### Perdas de Carga")
        labels = 'Perdas de carga distribuída', 'Perdas de carga localizada', 'Perda total'
        sizes = [hfe, hle, hte]
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, normalize=True,)
        st.pyplot(fig1)
    
    #Tabela Resultados
    st.markdown("### Resultados para o menor diâmetro")
    
    tab1, tab2, tab3, tab4, tab5 = st.columns(5)
    tab1.metric(label="Diâmetro Econômico", value=de,)
    tab2.metric(label="Potência Requerida", value=f" {round(We,4)} ",)
    tab3.metric(label="Perdas de carga distribuída", value=f" {round(hfe,4)} ",)
    tab4.metric(label="Perdas de carga localizada", value=f" {round(hle,4)} ",)
    tab5.metric(label="Perdas de carga total", value=f" {round(hte,4)} ",)
    
#Botões    
def Botões(): 
    
    bot_1, bot_2 = st.columns(2)

    with bot_1:
        if st.checkbox("Source Code"):
            code = '''
import streamlit as st
from st_aggrid import AgGrid
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


#Configuração de Página
st.set_page_config(
    page_title="Dimensionamento Diâmetro Econômico",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# Desenvolvido por Sarah Quoos e Edgar Silva. UTFPR, Curitiba, PR, 2025"}
    )

#Título
st.title("Dimensionamento de Diâmetro Econômico de Adutoras em Estações Elevatórias de Água")

#Dados de Entrada
with st.sidebar:
    st.title("Dados de entrada")
    Q = st.number_input('Vazão requerida em m³/h', value=0)
    L = st.number_input('Comprimento da adutora em metros:', value=0)
    Namin = st.number_input('Cota do nível de água mínimo no poço de sucção do bombeamento em metros:', value=0)
    Namax = st.number_input('Cota do nível de água máximo no reservatório elevado em metros:', value=0)  
    M = st.selectbox("Material da tubulação?",("select","Ferro Fundido", "PVC", "PRVF"),)

#Acesso ao banco de dados
def Banco():
    sheet = pd.read_excel('Banco de Dados.xlsx', sheet_name=M)
    #Diâmetro interno
    diaux = sheet['Diâmetro interno'].tolist()
    di = np.array(diaux)
    #Diâmetro nominal
    dnaux = sheet['Diâmetro nominal'].tolist()
    dn = np.array(dnaux)
    #Rugosidade
    e = sheet.loc[0, 'Rugosidade [mm]']
    return di, dn, e

#Cálculos
def Calculos():
    
    #Area
    pi = np.pi
    A = (pi * ((di/1000)**2))/4 
                    
    #Velocidade media
    q = Q/3600
    U = q/A
                    
    #Dados da agua
    p = 998 #massa específica [kg/m³]
    u = 0.001 #viscosidade dinamica [m²/s]
                                      
    #Número de Reynolds
    Re =  (p * (di/1000) * U)/u
                        
    #Fator de atrito
    f = (-1.8*np.log10(((e/di)/3.7)**1.11 + (6.9/Re)))**-2
                        
    #Perdas de carga distribuída
    g = 9.81 #gravidade [m²/s]
    hf = (f * L* U**2)/((di/1000) * 2 * g)
                    
    #Perdas de carga localizada
    hl = hf * 0.1
                    
    #Perda de carga total
    ht = hf + hl
                    
    #Altura manométrica
    hg = Namax - Namin
    hm = hg + ht
                    
    #Rendimento global
    ng = 0.70
                    
    #Potência requerida pela estação elevatória
    W = (9.8 * q * hm)/ng
                           
    #Botão mostrar resultados em forma de tabela
    if st.checkbox("Tabela Cálculos"):
            data_tab = {'Diametro interno': di, 'Area': A, 'Velocidade': U, 'Reynolds': Re, 'Fator de atrito': f,
                            'Perda de carga distribuída': hf, 'Perda de carga localizada': hl, 
                            'Perda de carga total': ht, 'Altura manométrica': hm, 'Potência requerida': W}
            tab = pd.DataFrame(data_tab)
            st.table(tab)
            
    #return Md, Cd, Pd, Ct
    return di, hf, hl, ht, W
    
            
#Encontrando Valores Econômicos       
def Economico():
    
    dnmin = min(dn) 
    tam = len(dn)
        
    i = 0
        
    while i <= tam:
        d1 = dn[i]
        if d1 == dnmin:
            de = dnmin
            We = W[i]
            hfe = hf[i]
            hle = hl[i]
            hte = ht[i] 
            break
        else:
            i = i + 1

#Gráficos e Resultados
def Resultado():
    
    graf_1, graf_2 = st.columns(2)
    
    #Gráfico Linha
    with graf_1:
        st.markdown("### Potência Requerida x Diâmetro")
        chart_data = {'Potencia Requerida': W, 'Diâmetro nominal': dn}
        st.line_chart(chart_data, x="Diâmetro nominal", y="Potencia Requerida",height=500)
    
    #Gráfico Pizza
    with graf_2:
        st.markdown("### Perdas de Carga")
        labels = 'Perdas de carga distribuída', 'Perdas de carga localizada', 'Perda total'
        sizes = [hfe, hle, hte]
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, normalize=True,)
        st.pyplot(fig1)
    
    #Tabela Resultados
    st.markdown("### Resultados para o menor diâmetro")
    
    tab1, tab2, tab3, tab4, tab5 = st.columns(5)
    tab1.metric(label="Diâmetro Econômico", value=de,)
    tab2.metric(label="Potência Requerida", value=f" {round(We,4)} ",)
    tab3.metric(label="Perdas de carga distribuída", value=f" {round(hfe,4)} ",)
    tab4.metric(label="Perdas de carga localizada", value=f" {round(hle,4)} ",)
    tab5.metric(label="Perdas de carga total", value=f" {round(hte,4)} ",)
    
#Botões    
def Botões(): 
    
    bot_1, bot_2 = st.columns(2)

    with bot_1:
        if st.checkbox("Source Code"):
            st.code(code, language="python")
    
    with bot_2:
        if st.checkbox("Banco de dados"):    
            file = pd.read_excel('Banco de Dados.xlsx', sheet_name='Dados')
            AgGrid(file)

#Rotina do Programa
if M == 'Ferro Fundido':
    di, dn, e = Banco()
    di, hf, hl, ht, W = Calculos()
    hfe, hle, hte, de, We = Economico()
    Resultado()
    Botões()
    
elif M == 'PVC':
    di, dn, e = Banco()
    di, hf, hl, ht, W = Calculos()
    hfe, hle, hte, de, We = Economico()
    Resultado()
    Botões()
        
elif M == 'PRVF':
    di, dn, e = Banco()
    di, hf, hl, ht, W = Calculos()
    hfe, hle, hte, de, We = Economico()
    Resultado()
    Botões()''' 
            st.code(code, language="python")
    
    with bot_2:
        if st.checkbox("Banco de dados"):    
            file = pd.read_excel('Banco de Dados.xlsx', sheet_name='Dados')
            AgGrid(file)

#Rotina do Programa
if M == 'Ferro Fundido':
    di, dn, e = Banco()
    di, hf, hl, ht, W = Calculos()
    hfe, hle, hte, de, We = Economico()
    Resultado()
    Botões()
    
elif M == 'PVC':
    di, dn, e = Banco()
    di, hf, hl, ht, W = Calculos()
    hfe, hle, hte, de, We = Economico()
    Resultado()
    Botões()
        
elif M == 'PRVF':
    di, dn, e = Banco()
    di, hf, hl, ht, W = Calculos()
    hfe, hle, hte, de, We = Economico()
    Resultado()
    Botões()
