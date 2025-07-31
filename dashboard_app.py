import pandas as pd
import dash
from dash import dcc, html
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- ==================================================================== ---
# --- PASO 1: CÁLCULO Y PREPARACIÓN DE DATOS (Lógica sin cambios)          ---
# --- ==================================================================== ---

REFERENCE_DATE = pd.to_datetime('2022-12-31')
df_purchases = pd.read_csv('Data/2025-07 purchases_challenge.csv', low_memory=False)
df_refunds = pd.read_csv('Data/2025-07 refunds_challenge.csv', low_memory=False)
df = pd.concat([df_purchases, df_refunds], ignore_index=True)

date_columns = ['Signup Date', 'Last Login Date', 'First Order Date', 'Last Order Date']
for col in date_columns:
    df[col] = pd.to_datetime(df[col], errors='coerce')

df.dropna(subset=['Signup Date', 'First Order Date'], inplace=True)
df['Activity Date'] = df['Last Order Date']
df = df[df['Activity Date'] <= REFERENCE_DATE]

customer_df = df.groupby('Member ID').agg(
    SignupDate=('Signup Date', 'first'),
    TotalSpend=('Total Amount', 'sum'),
    CreditAmountSum=('Credit Amount', 'sum')
).reset_index()
customer_df['UsedCredit'] = customer_df['CreditAmountSum'].notna() & (customer_df['CreditAmountSum'] != 0)
customer_df['SignupYear'] = customer_df['SignupDate'].dt.year

df_cohort = df.copy()
df_cohort['CohortYear'] = df_cohort['Signup Date'].dt.year.astype(int)
df_cohort['ActivityYear'] = df_cohort['Activity Date'].dt.year.astype(int)
df_cohort['CohortIndex'] = df_cohort['ActivityYear'] - df_cohort['CohortYear'] + 1
df_cohort = df_cohort[df_cohort['CohortIndex'] > 0]

cohort_data = df_cohort.groupby(['CohortYear', 'CohortIndex'])['Member ID'].nunique().reset_index()
cohort_retention_matrix = cohort_data.pivot_table(index='CohortYear', columns='CohortIndex', values='Member ID')
cohort_size = cohort_retention_matrix.iloc[:, 0]
cohort_retention_percentage = cohort_retention_matrix.divide(cohort_size, axis=0)
churn_rate_percentage = 1 - cohort_retention_percentage

df['OrderYear'] = df['Activity Date'].dt.year
yearly_sales = df[df['Total Amount'] > 0].groupby('OrderYear')['Total Amount'].sum()
yearly_refunds = abs(df[df['Total Amount'] < 0].groupby('OrderYear')['Total Amount'].sum())

credit_usage_counts = customer_df['UsedCredit'].value_counts()
credit_rate_by_cohort = customer_df.groupby('SignupYear')['UsedCredit'].mean() * 100

credit_users_ids = customer_df[customer_df['UsedCredit'] == True]['Member ID']
df_credit_users = df_cohort[df_cohort['Member ID'].isin(credit_users_ids)]
df_non_credit_users = df_cohort[~df_cohort['Member ID'].isin(credit_users_ids)]

credit_spend_matrix = df_credit_users.groupby(['CohortYear', 'CohortIndex'])['Total Amount'].sum().unstack()
credit_active_matrix = df_credit_users.groupby(['CohortYear', 'CohortIndex'])['Member ID'].nunique().unstack()
avg_spend_credit_users = credit_spend_matrix.divide(credit_active_matrix)

non_credit_spend_matrix = df_non_credit_users.groupby(['CohortYear', 'CohortIndex'])['Total Amount'].sum().unstack()
non_credit_active_matrix = df_non_credit_users.groupby(['CohortYear', 'CohortIndex'])['Member ID'].nunique().unstack()
avg_spend_non_credit_users = non_credit_spend_matrix.divide(non_credit_active_matrix)


# --- ==================================================================== ---
# --- PASO 2: CREACIÓN DE LOS GRÁFICOS INTERACTIVOS (ACTUALIZADO)          ---
# --- ==================================================================== ---

# Gráfico B1: Churn por Cohorte (con título en la barra de color)
fig_b1 = go.Figure(data=go.Heatmap(
    z=churn_rate_percentage.values * 100,
    x=churn_rate_percentage.columns,
    y=churn_rate_percentage.index,
    colorscale='rdylgn_r',
    zmid=0,
    text=churn_rate_percentage.values * 100,
    texttemplate="%{text:.1f}%",
    textfont={"size":10},
    colorbar={
        'title': {
            'text': 'Tasa de Cancelación %',
            'side': 'right'  # Esta propiedad pone el título en vertical
        }
    }
))
fig_b1.update_layout(
    title_text='B1: Tasa de Cancelación (Churn Rate) por Cohorte (%)', 
    xaxis_title='Año de Vida del Cliente', 
    yaxis_title='Año de Registro'
)


fig_b4 = go.Figure()
fig_b4.add_trace(go.Scatter(x=yearly_sales.index, y=yearly_sales.values, mode='lines+markers', name='Compras ($)'))
fig_b4.add_trace(go.Scatter(x=yearly_refunds.index, y=yearly_refunds.values, mode='lines+markers', name='Reembolsos ($)'))
fig_b4.update_layout(title_text='B4: Compras y Reembolsos por Año', xaxis_title='Año', yaxis_title='Monto Total ($)')

fig_b5 = go.Figure(data=[go.Pie(labels=['No Usaron Crédito', 'Sí Usaron Crédito'], values=credit_usage_counts.values, hole=.3)])
fig_b5.update_layout(title_text='B5: Proporción de Clientes por Uso de Crédito')

fig_b6 = go.Figure()
fig_b6.add_trace(go.Box(y=customer_df[customer_df['UsedCredit'] == False]['TotalSpend'], name='No Usó Crédito'))
fig_b6.add_trace(go.Box(y=customer_df[customer_df['UsedCredit'] == True]['TotalSpend'], name='Sí Usó Crédito'))
fig_b6.update_layout(title_text='B6: Gasto Neto Total por Uso de Crédito')

fig_b7 = go.Figure(data=[go.Bar(x=credit_rate_by_cohort.index, y=credit_rate_by_cohort.values)])
fig_b7.update_layout(title_text='B7: Tasa de Uso de Crédito por Cohorte de Registro (%)', xaxis_title='Año de Registro', yaxis_title='Tasa de Uso (%)')

# --- CAMBIO AQUÍ ---
# Gráfico B8: Gasto Promedio (con etiquetas y títulos de ejes)
fig_b8 = make_subplots(
    rows=1, cols=2, 
    subplot_titles=('Clientes que USARON Crédito', 'Clientes que NO Usaron Crédito'), 
    shared_yaxes=True
)

# Heatmap para usuarios de crédito
fig_b8.add_trace(go.Heatmap(
    z=avg_spend_credit_users.values,
    x=avg_spend_credit_users.columns,
    y=avg_spend_credit_users.index,
    colorscale='viridis',
    text=avg_spend_credit_users.values,
    texttemplate="$%{text:,.0f}",
    textfont={"size":10},
    colorbar={'title': 'Gasto ($)', 'x': 0.45}
), 1, 1)

# Heatmap para NO usuarios de crédito
fig_b8.add_trace(go.Heatmap(
    z=avg_spend_non_credit_users.values,
    x=avg_spend_non_credit_users.columns,
    y=avg_spend_non_credit_users.index,
    colorscale='viridis',
    text=avg_spend_non_credit_users.values,
    texttemplate="$%{text:,.0f}",
    textfont={"size":10},
    colorbar={'title': 'Gasto ($)', 'x': 1.0}
), 1, 2)

# Actualizar el layout general con los títulos de los ejes
fig_b8.update_layout(
    title_text='B8: Gasto Promedio a lo Largo del Tiempo (Crédito vs. No Crédito)',
    yaxis_title='Año de Registro (Cohorte)'
)
# Se actualizan ambos ejes X para que tengan el mismo título
fig_b8.update_xaxes(title_text='Año de Vida del Cliente')


# --- ==================================================================== ---
# --- PASO 3: DISEÑO DEL DASHBOARD CON PESTAÑAS                          ---
# --- ==================================================================== ---
app = dash.Dash(__name__)
server = app.server

#----------------------------------------------------------------------------#

# --- Contenido de la Pestaña 0: Índice ---
def color_box(color):
    return html.Span(style={'backgroundColor': color, 'border': '1px solid grey', 'padding': '0px 10px', 'marginRight': '5px'})

tab0_layout = html.Div([
    html.H2('Cómo Interpretar los Gráficos', style={'textAlign': 'center', 'marginTop': '20px'}),
    
    html.Div([
        # --- Sección para el Gráfico B1 ---
        html.H3('Gráfico B1: Tasa de Cancelación (Churn Rate) por Cohorte'),
        html.Ul([
            html.Li([color_box('#d73027'), html.B("Colores Rojos (cálidos): "), "Indican un churn alto (malo)."]),
            html.Li([color_box('#1a9850'), html.B("Colores Verdes (fríos): "), "Indican un churn negativo (excelente)."]),
            html.Li([color_box('#ffffbf'), html.B("Colores Neutros (amarillos): "), "Indican un churn cercano a cero."]),
        ], style={'lineHeight': '2'}),
        html.H4("Explicación del Gráfico", style={'marginTop': '20px'}),
        html.P("El valor que medimos es la tasa de cancelación, que se calcula a partir del cambio en el número de clientes activos de un año a otro."),
        html.P("Este valor cambia debido a dos fuerzas opuestas:"),
        html.Ul([
            html.Li([html.B("Clientes que se van: "), "Son clientes que estaban activos el año pasado pero este año no realizan ninguna transacción."]),
            html.Li([html.B("Clientes que 'llegan' (se reactivan): "), "Son clientes que se registraron en el mismo año que la cohorte pero nunca habían comprado, y finalmente hacen su primera reserva."]),
        ]),
        html.P("El resultado de este balance hace que el total de clientes activos aumente o disminuya, cambiando así la tasa de cancelación."),

        html.Hr(style={'marginTop': '30px'}),

        # --- Sección para el Gráfico B4 ---
        html.H3('Gráfico B4: Compras y Reembolsos por Año'),
        html.P("Este gráfico muestra el avance de compras y reembolsos con respecto al paso del tiempo."),

        html.Hr(style={'marginTop': '30px'}),

        # --- Sección para el Gráfico B5 ---
        html.H3('Gráfico B5: Proporción de Clientes por Uso de Crédito'),
        html.P("Este gráfico muestra la proporción de clientes que han utilizado la función de crédito frente a los que no."),

        html.Hr(style={'marginTop': '30px'}),

        # --- Sección para el Gráfico B6 ---
        html.H3('Gráfico B6: Gasto Neto Total por Uso de Crédito'),
        html.P('Este gráfico de "cajas y bigotes" (box plot) compara el gasto neto total de los clientes que usaron crédito con los que no. La conclusión es inmediata y contundente: los clientes que usan crédito gastan significativamente más.'),
                
        html.Hr(style={'marginTop': '30px'}),

        # --- Sección para el Gráfico B7 ---
        html.H3('Gráfico B7: Tasa de Uso de Crédito por Cohorte de Registro'),
        html.P("Este gráfico muestra el porcentaje de clientes de cada cohorte (año de registro) que ha utilizado la función de crédito."),
        
        html.Hr(style={'marginTop': '30px'}),

        # --- Nueva Sección para el Gráfico B8 ---
        html.H3('Gráfico B8: Gasto Promedio a lo Largo del Tiempo (Crédito vs. No Crédito)'),
        html.P("Este gráfico compara el gasto promedio a lo largo del tiempo entre clientes que usan crédito y los que no."),

    ], style={'padding': '20px', 'maxWidth': '800px', 'margin': 'auto', 'fontSize': '16px'})
])

#----------------------------------------------------------------------------#

# --- Contenido de la Pestaña 1: Gráficos ---
tab1_layout = html.Div([
    html.Div(className='row', children=[
        html.Div(className='six columns', children=[dcc.Graph(id='churn-heatmap', figure=fig_b1)]),
        html.Div(className='six columns', children=[dcc.Graph(id='trends-line', figure=fig_b4)])
    ], style={'display': 'flex'}),
    html.Hr(),
    html.Div(className='row', children=[
        html.Div(className='six columns', children=[dcc.Graph(id='credit-pie', figure=fig_b5)]),
        html.Div(className='six columns', children=[dcc.Graph(id='spend-credit-box', figure=fig_b6)])
    ], style={'display': 'flex'}),
    html.Div(className='row', children=[dcc.Graph(id='credit-rate-bar', figure=fig_b7)]),
    html.Hr(),
    html.Div(className='row', children=[dcc.Graph(id='spend-time-heatmaps', figure=fig_b8)])
])

# --- Contenido de la Pestaña 2: Métricas Clave ---
metrics_data = {
    "Período MÍNIMO de pre-compra": "0 días",
    "Período MÁXIMO de pre-compra": "3059 días",
    "Antigüedad promedio de clientes ACTIVOS": "588.66 días",
    "Antigüedad promedio de clientes CANCELADOS": "222.36 días",
    "Número promedio de pedidos de clientes ACTIVOS": "6.02",
    "Número promedio de pedidos de clientes CANCELADOS": "3.02",
    "Gasto neto promedio de clientes ACTIVOS": "$1614.07",
    "Gasto neto promedio de clientes CANCELADOS": "$697.81",
    "Tasa de reembolso por NÚMERO de pedidos": "28.41%",
    "Tasa de reembolso por MONTO gastado": "18.13%",
}

table_header = [html.Thead(html.Tr([html.Th("Métrica", style={'textAlign': 'left', 'padding': '8px'}), html.Th("Valor", style={'textAlign': 'left', 'padding': '8px'})]))]
table_body = [html.Tbody([html.Tr([html.Td(metric, style={'padding': '8px'}), html.Td(value, style={'padding': '8px'})]) for metric, value in metrics_data.items()])]
table = html.Table(table_header + table_body, style={'width': '60%', 'margin': 'auto', 'marginTop': '20px', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'})

tab2_layout = html.Div([
    html.H2('Métricas Clave al 2022-12-31', style={'textAlign': 'center', 'marginTop': '20px'}),
    table
])

# --- Contenido de la Pestaña 3: Resumen de Hallazgos (versión definitiva y completa) ---
tab3_layout = html.Div([
    html.H2('Resumen de Hallazgos y Recomendaciones Estratégicas', style={'textAlign': 'center', 'marginTop': '20px'}),
    
    html.Div([
        # --- Hallazgos de Retención y Churn ---
        html.H3('Hallazgos de Retención y Churn (B1, B2, B3)'),
        html.Ul([
            html.Li([html.B("Comportamiento de Churn: "), "La mayoría de las cohortes pierden clientes después del primer año, pero las cohortes 2016 y 2018 muestran un valioso 'churn negativo' por activación de clientes dormidos."]),
            html.Li([html.B("Mejor y Peor Cohorte: "), "La cohorte de 2016 es la de mejor rendimiento, demostrando una excelente capacidad de retención, mientras que la de 2017 tuvo el peor desempeño en su segundo año."]),
        ], style={'lineHeight': '2'}),

        html.Hr(style={'margin': '30px 0'}),

        # --- Hallazgos de Crecimiento y Mercado ---
        html.H3('Hallazgos de Crecimiento del Negocio (B4)'),
        html.P("El gráfico de tendencias de compras y reembolsos muestra una empresa en una fase de crecimiento exponencial y saludable. Los puntos clave son:"),
        html.Ul([
            html.Li([html.B("Crecimiento Acelerado: "), "El volumen de compras se disparó desde 2020, mostrando una fuerte demanda y una excelente adaptación al mercado."]),
            html.Li([html.B("Resiliencia Post-2020: "), "El negocio superó con éxito la pequeña caída de 2020 (probablemente por la pandemia), demostrando la fortaleza de su modelo."]),
            html.Li([html.B("Tasa de Reembolso Saludable: "), "Los reembolsos crecen a un ritmo mucho más lento que las compras. Esta brecha creciente significa que el negocio escala de manera eficiente y con clientes satisfechos."]),
        ], style={'lineHeight': '2'}),

        html.Hr(style={'margin': '30px 0'}),

        # --- Conclusión Estratégica sobre el Crédito ---
        html.H3('El Crédito como Principal Oportunidad (B5, B6, B7, B8)'),
        html.P("La historia del crédito, contada a través de varios gráficos, revela la mayor palanca de crecimiento para la empresa:"),
        html.Ul([
            html.Li([html.B("La Oportunidad (B5): "), "Más del 70% de los clientes no usa crédito, representando un vasto mercado potencial por capturar."]),
            html.Li([html.B("El Impacto en el Gasto (B6): "), "El gráfico de cajas muestra de forma contundente que los clientes que usan crédito tienen un gasto neto total significativamente más alto y con mayor variabilidad."]),
            html.Li([html.B("El Valor a Largo Plazo (B8): "), "Los mapas de calor confirman que los usuarios de crédito no solo gastan más en total, sino que lo hacen de manera consistente año tras año, haciéndolos mucho más valiosos."]),
            html.Li([
                html.B("La Tendencia Positiva (B7): "), 
                "La adopción del crédito muestra dos fases claras: una inicial (2015-2017) donde era una función de nicho, y una de crecimiento acelerado (2018-2022) donde cada nueva cohorte lo adopta mucho más."
            ]),
        ], style={'lineHeight': '2'}),

        # --- Recomendación Final ---
        html.Div([
            html.H4("Recomendación Estratégica Principal", style={'color': '#1a9850'}),
            html.P(
                "Lanzar campañas de marketing para aumentar la adopción de la función de crédito. Enfocarse en comunicar sus beneficios tiene el potencial de convertir a clientes promedio en clientes de alto valor, siendo esta la palanca de crecimiento más clara identificada en el análisis.",
                style={'fontSize': '18px', 'fontStyle': 'italic'}
            )
        ], style={'marginTop': '25px', 'padding': '20px', 'backgroundColor': '#f9f9f9', 'borderRadius': '5px', 'borderLeft': '5px solid #1a9850'})

    ], style={'padding': '20px', 'maxWidth': '900px', 'margin': 'auto', 'fontSize': '16px'})
])

#----------------------------------------------------------------#

# --- Layout principal de la aplicación con el orden de pestañas corregido ---
app.layout = html.Div([
    html.H1(children='Análisis de Clientes y Cancelación (Churn) para ID90', style={'textAlign': 'center'}),
    dcc.Tabs(id="tabs", value='tab-0', children=[
        dcc.Tab(label='Índice', value='tab-0', children=tab0_layout),
        dcc.Tab(label='Dashboard Interactivo', value='tab-1', children=tab1_layout),
        dcc.Tab(label='Métricas Clave', value='tab-2', children=tab2_layout),
        dcc.Tab(label='Resumen de Hallazgos', value='tab-3', children=tab3_layout),
    ])
])

# --- Layout principal de la aplicación con FONDO DE PANTALLA ---
app.layout = html.Div(
    style={
        'backgroundImage': 'url("/assets/background.png")', # Ruta a tu imagen
        'backgroundSize': 'cover',          # Cubre todo el espacio
        'backgroundPosition': 'center',     # Centra la imagen
        'backgroundRepeat': 'no-repeat',    # No repitas la imagen
        'backgroundAttachment': 'fixed',    # El fondo no se mueve al hacer scroll
        'minHeight': '100vh'                # Asegura que el fondo cubra toda la altura
    }, 
    children=[
        html.H1(children='Análisis de Clientes y Cancelación (Churn) para ID90', style={'textAlign': 'center', 'color': 'black'}), # Color de texto cambiado a blanco para legibilidad
        dcc.Tabs(id="tabs", value='tab-0', children=[
            dcc.Tab(label='Índice', value='tab-0', children=tab0_layout),
            dcc.Tab(label='Dashboard Interactivo', value='tab-1', children=tab1_layout),
            dcc.Tab(label='Métricas Clave', value='tab-2', children=tab2_layout),
            dcc.Tab(label='Resumen de Hallazgos', value='tab-3', children=tab3_layout),
        ])
    ]
)

if __name__ == '__main__':
    app.run(debug=True)