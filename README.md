# <ins>__Análisis de Clientes para ID90__</ins>

## <ins>__1. Resumen del Proyecto__</ins>

Este proyecto presenta un análisis de datos para __ID90__, enfocado en entender el comportamiento de los clientes y la tasa de cancelación (churn). El objetivo es identificar patrones clave en la retención de clientes, el uso de crédito y el valor a lo largo del tiempo para generar recomendaciones estratégicas que impulsen el crecimiento del negocio.

El análisis se divide en dos partes principales:

* Un Análisis Exploratorio de Datos (EDA) para entender las características básicas de los datos.

* Un Dashboard Interactivo en Plotly Dash que visualiza las métricas clave y los hallazgos del análisis.


## <ins>__2. Estructura del Proyecto__</ins>

La carpeta del proyecto está organizada de la siguiente manera para facilitar la comprensión y reproducibilidad:

```
ID90_Project/
├── Data/
│   ├── 2025-07 purchases_challenge.csv   # Datos crudos de compras
│   └── 2025-07 refunds_challenge.csv     # Datos crudos de devoluciones
├── Processed_data/
│   ├── transacciones.csv                 # Resumen por cliente (compras y devoluciones) agrupado por ID Member
│   ├── concatenado.csv                   # Dataframes concatenados, para trabajar con un solo dataframe todas las compras y devoluciones
│   └── customer_df.csv                   # Perfil final por cliente con métricas de churn. Dataframe con columnas adicionales.
├── Notebooks/
│   ├── EDA.ipynb                         # Notebook con el Análisis Exploratorio de Datos
│   └── Resumen de los Hallazgos.ipynb   # Notebook con gráficos y resumen de insights
├── assets/
│   ├── Background.png                     # Imágenes para el dashboard
│   ├── background2.png
│   ├── background3.png
│   └── background4.png
├── dashboard_app.py                       # Script para ejecutar el dashboard interactivo
├── requirements.txt                       # Lista de librerías necesarias para el proyecto
└── README.md                             # Este archivo
```

## <ins>3. Instrucciones de uso</ins>

Para ejecutar este proyecto y visualizar el dashboard interactivo, por favor sigue estos pasos:

### a) Prerrequisitos

Tener instalado Python 3.9 o superior.

Se recomienda usar un entorno virtual para evitar conflictos de dependencias.

### b) Instalación

1. Clona o descarga este repositorio en tu máquina local.

2. Abre una terminal y navega a la carpeta raíz del proyecto.

3. Crea y activa un entorno virtual (opcional pero recomendado):

python -m venv mi_entorno
source mi_entorno/bin/activate  # En macOS/Linux
mi_entorno\Scripts\activate      # En Windows

4. Instala todas las librerías necesarias desde el archivo ~requirements.txt~:

pip install -r requirements.txt

### c) Ejecutar Dashboard

1. Con tu entorno activado y ubicado en la carpeta del proyecto, ejecuta el siguiente comando en la terminal:

   python dashboard_app.py

2. Abre tu navegador web y ve a la dirección que aparece en la terminal (usualmente http://127.0.0.1:8050/).

## <ins>4. Metodología de Análisis</ins>

Se definieron las siguientes métricas clave para el análisis:

* <ins>Cliente Cancelado (Churned):</ins> Se considera que un cliente ha cancelado si su Last Login Date tiene más de 100 días de antigüedad con respecto a la fecha de referencia del 31 de diciembre de 2022.

* <ins>Antigüedad del Cliente (Tenure):</ins> Tiempo transcurrido entre la primera y la última compra de un cliente.

* <ins>Período de Pre-Compra:</ins> Tiempo transcurrido entre la fecha de registro y la primera compra.

* <ins>Uso de Crédito:</ins> Indicador que determina si un cliente ha utilizado crédito (Credit Amount != 0).

## 5. Diccionario de Datos

### a) Archivos de Datos Crudos (/data)

El archivo __"2025-07 purchases_challenge"__ contiene:

<ins>Member ID:</ins> Identificador único del cliente.

<ins>Signup Date:</ins> Fecha de registro del cliente.

<ins>Last Login Date:</ins> Última fecha de inicio de sesión del cliente.

<ins>Purchases:</ins> Número total de pedidos/compras.

<ins>Total Amount:</ins> Monto total gastado.

<ins>First Order Date:</ins> Fecha de la primera compra.

<ins>Last Order Date:</ins> Fecha de la última compra.

Credit Amount: Esto es monto que el cliente pagó con crédito (en el archivo __"2025-07 purchases_challenge"__) y en el archivo de __"2025-07 refunds_challenge"__ es el monto que se le devolvió al usuario a través de tarjeta de crédito

__"2025-07 refunds_challenge"__:

<ins>Member ID:</ins> Identificador único del cliente (para unir con purchases_df).

<ins>Signup Date:</ins> Fecha de registro del cliente.

<ins>Last Login Date:</ins> Última fecha de inicio de sesión del cliente.

<ins>Refunds:</ins> Monto del dinero reembolsado al cliente.

<ins>Credit Amount:</ins> Monto monetario del reembolso. Si esta es la columna que indica el valor de la devolución.

<ins>Total Amount:</ins> Monto total gastado.

<ins>First Order Date:</ins> Fecha de la primera compra.

<ins>Last Order Date:</ins> Fecha de la última compra.

### b) Archivos de Datos Procesados (/processed_data)

<ins>1_transacciones.csv:</ins> Resultado de un merge de los datos de compras y devoluciones, creando un resumen estático para cada cliente. Útil para análisis de totales por cliente.

<ins>2_concatenado.csv:</ins> Resultado de un concat de los datos de compras y devoluciones, creando un historial completo de todas las transacciones. Esencial para el análisis de cohortes y tendencias temporales.

<ins>3_customer_df.csv:</ins> El DataFrame final y enriquecido que sirve como base para el dashboard. Cada fila representa un único cliente con todas sus métricas calculadas:
* __IsChurned:__ Un indicador (Sí/No) basado en los 100 días de inactividad.
* __CustomerTenure:__ Antigüedad del cliente.
* __PrePurchasePeriod:__ Tiempo que tardó en hacer la primera compra.
* __UsedCredit:__ Un indicador (Sí/No) si usó crédito.


## 🚀 Deploy en Render

El dashboard está disponible en una URL pública como: `https://id90-challenge.onrender.com`

---