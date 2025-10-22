# 📊 SEC Filing Extractor - Guía Completa

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**Herramienta profesional para descargar y extraer datos de documentos SEC EDGAR**

[English](#english-version) | [Español](#versión-en-español)

</div>

---

# 🇪🇸 Versión en Español

## 📑 Tabla de Contenidos

1. [¿Qué es SEC Filing Extractor?](#-qué-es-sec-filing-extractor)
2. [Instalación Paso a Paso](#-instalación-paso-a-paso)
3. [Tutorial para Principiantes](#-tutorial-para-principiantes)
4. [Modos de Uso](#-modos-de-uso)
5. [Guías Detalladas](#-guías-detalladas)
6. [Ejemplos Prácticos](#-ejemplos-prácticos)
7. [Casos de Uso Reales](#-casos-de-uso-reales)
8. [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
9. [Configuración Avanzada](#-configuración-avanzada)
10. [Solución de Problemas](#-solución-de-problemas)
11. [Preguntas Frecuentes](#-preguntas-frecuentes)
12. [API Reference](#-api-reference)

---

## 🎯 ¿Qué es SEC Filing Extractor?

**SEC Filing Extractor** es una herramienta Python que automatiza la descarga y extracción de datos de los documentos financieros que las empresas públicas presentan ante la SEC (Securities and Exchange Commission) de Estados Unidos.

### ¿Para qué sirve?

- 📈 **Análisis financiero**: Extraer estados financieros históricos automáticamente
- 📊 **Investigación de mercado**: Analizar métricas de múltiples empresas
- 📝 **Auditoría**: Extraer secciones específicas de informes anuales
- 🤖 **Automatización**: Procesar cientos de documentos sin intervención manual
- 📉 **Trading algorítmico**: Obtener datos financieros para modelos cuantitativos

### ¿Qué tipos de documentos puedo descargar?

- **10-K**: Informes anuales completos
- **10-Q**: Informes trimestrales
- **8-K**: Eventos importantes (fusiones, adquisiciones, cambios de CEO, etc.)
- **20-F**: Informes anuales de empresas extranjeras
- **6-K**: Informes de empresas extranjeras

### ¿Qué datos puedo extraer?

1. **Tablas financieras** → CSV/JSON
2. **Secciones de texto** (Items 1, 1A, 7, etc.) → Markdown
3. **Estados financieros** (Balance, P&L, Cash Flow) → CSV con datos históricos
4. **Datos XBRL** → JSON estructurado

---

## 🚀 Instalación Paso a Paso

### Opción 1: Instalación Básica (Recomendado para principiantes)

#### Paso 1: Verificar Python

Abre tu terminal o CMD y verifica que tienes Python instalado:

```bash
python --version
```

Deberías ver algo como `Python 3.8.0` o superior. Si no tienes Python, descárgalo de [python.org](https://www.python.org/).

#### Paso 2: Descargar el Proyecto

```bash
# Clona el repositorio
git clone https://github.com/hectoorperezz/financial_tools.git

# Entra al directorio
cd financial_tools
```

#### Paso 3: Instalar Dependencias

```bash
# Instala las librerías necesarias
pip install -r requirements.txt
```

¡Listo! Ya puedes usar la herramienta.

### Opción 2: Instalación con Entorno Virtual (Recomendado para desarrolladores)

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### Opción 3: Instalación como Paquete

```bash
# Instalar el paquete en tu sistema
python setup.py install

# Ahora puedes usarlo desde cualquier lugar
sec-filing-extractor --help
```

---

## 📚 Tutorial para Principiantes

### 🎬 Tu Primera Extracción (5 minutos)

Vamos a descargar el último informe anual (10-K) de Apple paso a paso.

#### Paso 1: Abrir Terminal

Navega hasta la carpeta del proyecto:

```bash
cd financial_tools
```

#### Paso 2: Ejecutar el Programa

```bash
python main.py
```

Verás algo como esto:

```
======================================================================
SEC Filing Extractor - Interactive CLI
======================================================================

Enter ticker symbol (e.g., AAPL):
```

#### Paso 3: Introducir el Ticker

Escribe `AAPL` y presiona Enter:

```
Enter ticker symbol (e.g., AAPL): AAPL
```

El programa buscará la información de Apple:

```
Looking up AAPL...

======================================================================
COMPANY INFORMATION
======================================================================
Ticker:        AAPL
Name:          Apple Inc.
CIK:           0000320193
SIC:           3571
Industry:      ELECTRONIC COMPUTERS
Fiscal Year:   0928
Entity Type:   operating
======================================================================
```

#### Paso 4: Seleccionar un Documento

El programa te mostrará los últimos documentos:

```
======================================================================
RECENT FILINGS
======================================================================
  1. 10-K     | 2024-10-28 | 0000320193-24-000123 | aapl-20240928.htm
  2. 10-Q     | 2024-08-02 | 0000320193-24-000081 | aapl-20240629.htm
  3. 10-Q     | 2024-05-03 | 0000320193-24-000055 | aapl-20240330.htm
  ...
======================================================================

Select filing [1-20] (Enter for 1):
```

Presiona Enter para seleccionar el primero (10-K más reciente):

```
Select filing [1-20] (Enter for 1): ↵
```

#### Paso 5: Descargar el Documento

El programa te preguntará si quieres descargarlo:

```
Download this filing? (Y/n):
```

Escribe `y` y presiona Enter:

```
Download this filing? (Y/n): y
Include exhibits? (y/N): n

Downloading filing... This may take a few minutes.

✓ Downloaded 73 files to: filings/0000320193-24-000123
✓ Recommended viewing file: aapl-20240928.htm
```

#### Paso 6: Extraer Datos

El programa te preguntará qué quieres extraer:

```
Open in browser? (y/N): n

Extract tables to CSV? (Y/n): y
Extracting tables...
✓ Extracted 63 tables
  JSON: aapl-20240928_tables.json

Extract text sections to Markdown? (Y/n): y
Extracting sections...
✓ Extracted 24 sections
  Index: sections_index.md

Extract financial statements (XBRL)? (Y/n): y
Extracting financial statements...
✓ Extracted 3 statements
  IS: IS.csv
  BS: BS.csv
  CF: CF.csv
```

#### ✅ ¡Completado!

Todos los archivos se guardaron en:

```
filings/0000320193-24-000123/
├── aapl-20240928.htm          # Documento principal
├── tables/                     # Tablas extraídas
│   ├── aapl-20240928_table_1.csv
│   ├── aapl-20240928_table_2.csv
│   └── ...
├── sections/                   # Secciones de texto
│   ├── Item_1.md
│   ├── Item_1A.md
│   ├── Item_7.md
│   └── ...
└── facts/                      # Estados financieros
    ├── IS.csv                  # Income Statement
    ├── BS.csv                  # Balance Sheet
    ├── CF.csv                  # Cash Flow
    └── company_facts.json      # Datos XBRL completos
```

### 📊 Explorando los Resultados

#### Ver Estados Financieros

Abre `filings/0000320193-24-000123/facts/IS.csv` en Excel o cualquier editor de hojas de cálculo:

```csv
Date,Revenues,SalesRevenueNet,CostOfRevenue,GrossProfit,...
2024-09-28,385603000000,,214137000000,171466000000,...
2023-09-30,383285000000,,214137000000,169148000000,...
2022-09-24,394328000000,,223546000000,170782000000,...
...
```

¡Ya tienes datos financieros de Apple listos para analizar!

---

## 🎮 Modos de Uso

### Modo 1: Interactivo (Recomendado para principiantes)

El modo más fácil. Te guía paso a paso:

```bash
python main.py
```

**Ventajas:**
- ✅ No necesitas saber programar
- ✅ Interfaz amigable con preguntas
- ✅ Perfecto para explorar

**Cuándo usarlo:**
- Primera vez usando la herramienta
- Descargas ocasionales
- Exploración de datos

---

### Modo 2: Línea de Comandos (Quick Mode)

Descarga automática sin preguntas. Ideal para automatización:

```bash
python main.py --ticker AAPL --form 10-K --quick
```

**Ventajas:**
- ⚡ Rápido y directo
- 🤖 Automatizable (scripts, cron jobs)
- 📝 Reproducible

**Ejemplos:**

```bash
# Descargar último 10-K de Microsoft
python main.py --ticker MSFT --form 10-K --quick

# Descargar último 10-Q de Tesla
python main.py --ticker TSLA --form 10-Q --quick

# Guardar en carpeta personalizada
python main.py --ticker GOOGL --form 10-K --quick --output-dir ./mis_datos

# Activar logs detallados
python main.py --ticker AMZN --form 10-K --quick --log-level DEBUG
```

**Cuándo usarlo:**
- Procesamiento por lotes
- Scripts automatizados
- Integración con otros sistemas

---

### Modo 3: Programático (Para desarrolladores)

Usa Python para control total:

```python
from sec_filing_extractor import FilingManager, Config

# Configuración
config = Config(
    user_agent="TuNombre (tu@email.com)",
    default_output_dir="./datos_sec"
)

# Inicializar manager
with FilingManager(config) as manager:
    # Buscar empresa
    filings = manager.get_filings("AAPL", form_types=("10-K",), limit=1)

    # Descargar y procesar
    result = manager.process_filing_complete(
        filings[0],
        extract_tables=True,
        extract_sections=True,
        extract_financials=True
    )

    print(f"Archivos en: {result['download']['filing_dir']}")
```

**Ventajas:**
- 🎯 Control total
- 🔧 Personalizable
- 🚀 Integrable en aplicaciones

**Cuándo usarlo:**
- Desarrollo de aplicaciones
- Pipelines de datos
- Análisis personalizado

---

## 📖 Guías Detalladas

### 🔍 Guía 1: Buscar Información de Empresas

#### Opción A: Modo Interactivo

```bash
python main.py
# Sigue las instrucciones en pantalla
```

#### Opción B: Modo Programático

```python
from sec_filing_extractor import CompanyLookup

lookup = CompanyLookup()

# Buscar por ticker
cik = lookup.get_cik_from_ticker("AAPL")
print(f"CIK de Apple: {cik}")

# Obtener información completa
info = lookup.get_company_info("TSLA")
print(f"Nombre: {info['name']}")
print(f"CIK: {info['cik']}")
print(f"Industria: {info['sic_description']}")
print(f"Estado: {info['state_of_incorporation']}")
```

**Salida esperada:**

```
CIK de Apple: 0000320193
Nombre: Tesla, Inc.
CIK: 0001318605
Industria: MOTOR VEHICLES & PASSENGER CAR BODIES
Estado: DE
```

---

### 📥 Guía 2: Descargar Documentos

#### Ejemplo: Descargar los últimos 5 documentos 10-K de una empresa

```python
from sec_filing_extractor import FilingManager

manager = FilingManager()

# Obtener últimos 5 documentos 10-K
filings = manager.get_filings("MSFT", form_types=("10-K",), limit=5)

# Mostrar información
for i, filing in enumerate(filings, 1):
    print(f"{i}. {filing.form} - {filing.filing_date}")
    print(f"   Accession: {filing.accession}")
    print()

# Descargar el más reciente
result = manager.download_filing(
    filing=filings[0],
    include_exhibits=False  # Sin anexos para ir más rápido
)

print(f"Descargado: {result['file_count']} archivos")
print(f"Ubicación: {result['filing_dir']}")
```

#### Control de Descarga

```python
from pathlib import Path

# Callback para ver progreso
def mostrar_progreso(actual, total):
    porcentaje = (actual / total) * 100
    print(f"Progreso: {porcentaje:.1f}% ({actual}/{total})")

# Descargar con progreso
result = manager.download_filing(
    filing=filings[0],
    include_exhibits=True,  # Incluir todos los anexos
    output_dir=Path("./mis_documentos")
)
```

---

### 📊 Guía 3: Extraer Tablas

Las tablas contienen datos financieros, métricas operativas y otra información estructurada.

#### Ejemplo Básico

```python
from pathlib import Path
from sec_filing_extractor.extractors import TableExtractor

# Inicializar extractor
extractor = TableExtractor()

# Extraer tablas
result = extractor.extract(
    source=Path("filings/0000320193-24-000123/aapl-20240928.htm"),
    output_dir=Path("filings/0000320193-24-000123/tables")
)

print(f"Tablas extraídas: {result['table_count']}")
print(f"Archivos CSV: {len(result['csv_files'])}")
print(f"Archivo JSON: {result['json_file']}")
```

#### Configuración Avanzada

```python
# Extraer solo tablas grandes (mínimo 5 columnas)
result = extractor.extract(
    source=html_file,
    output_dir=output_dir,
    min_columns=5,      # Mínimo 5 columnas
    max_tables=50       # Máximo 50 tablas
)

# Procesar las tablas extraídas
import pandas as pd

for csv_file in result['csv_files']:
    df = pd.read_csv(csv_file)
    print(f"\nTabla: {Path(csv_file).name}")
    print(f"Dimensiones: {df.shape}")
    print(f"Columnas: {list(df.columns)}")
```

#### Ejemplo: Encontrar tabla con ingresos

```python
import pandas as pd
from pathlib import Path

# Buscar en todas las tablas
tablas_dir = Path("filings/0000320193-24-000123/tables")

for csv_file in tablas_dir.glob("*.csv"):
    df = pd.read_csv(csv_file)

    # Buscar columnas con "revenue" o "revenues"
    revenue_cols = [col for col in df.columns
                    if 'revenue' in col.lower()]

    if revenue_cols:
        print(f"\n✓ Encontrado en: {csv_file.name}")
        print(df[revenue_cols].head())
```

---

### 📝 Guía 4: Extraer Secciones de Texto

Los documentos 10-K tienen secciones estandarizadas (Items) con información específica.

#### Secciones Importantes del 10-K

- **Item 1**: Descripción del negocio
- **Item 1A**: Factores de riesgo
- **Item 7**: Análisis de gestión (MD&A)
- **Item 7A**: Riesgos de mercado
- **Item 8**: Estados financieros
- **Item 9A**: Controles internos

#### Ejemplo de Extracción

```python
from pathlib import Path
from sec_filing_extractor.extractors import SectionExtractor

# Inicializar extractor
extractor = SectionExtractor()

# Extraer secciones
result = extractor.extract(
    source=Path("filings/0000320193-24-000123/aapl-20240928.htm"),
    output_dir=Path("filings/0000320193-24-000123/sections")
)

print(f"Secciones extraídas: {result['section_count']}")
print(f"\nArchivos generados:")
for item_id, path in result['sections'].items():
    print(f"  Item {item_id}: {Path(path).name}")
```

#### Leer una Sección Específica

```python
# Leer Item 1A (Risk Factors)
item_1a = Path("filings/0000320193-24-000123/sections/Item_1A.md")

with open(item_1a, 'r', encoding='utf-8') as f:
    contenido = f.read()

# Mostrar primeros 500 caracteres
print(contenido[:500])

# Analizar riesgos mencionados
riesgos = contenido.lower()
if 'competition' in riesgos:
    print("✓ Menciona riesgos de competencia")
if 'regulation' in riesgos:
    print("✓ Menciona riesgos regulatorios")
if 'cybersecurity' in riesgos:
    print("✓ Menciona riesgos de ciberseguridad")
```

---

### 💰 Guía 5: Extraer Estados Financieros

Los estados financieros están en formato XBRL y contienen datos históricos estructurados.

#### Ejemplo Completo

```python
from sec_filing_extractor.extractors import FinancialStatementExtractor
from pathlib import Path
import pandas as pd

# Inicializar extractor
extractor = FinancialStatementExtractor()

# Extraer estados financieros
result = extractor.extract(
    cik="0000320193",  # Apple
    output_dir=Path("datos_financieros")
)

print(f"Estados generados: {result['statement_count']}")

# Cargar Income Statement
is_df = pd.read_csv(result['IS'])
print("\n📊 Income Statement")
print(is_df.head())

# Cargar Balance Sheet
bs_df = pd.read_csv(result['BS'])
print("\n📊 Balance Sheet")
print(bs_df.head())

# Cargar Cash Flow
cf_df = pd.read_csv(result['CF'])
print("\n📊 Cash Flow")
print(cf_df.head())
```

#### Analizar Tendencias

```python
import pandas as pd
import matplotlib.pyplot as plt

# Cargar datos
df = pd.read_csv("datos_financieros/IS.csv")

# Convertir fecha a datetime
df['Date'] = pd.to_datetime(df['Date'])
df = df.sort_values('Date')

# Graficar ingresos
plt.figure(figsize=(12, 6))
plt.plot(df['Date'], df['Revenues'], marker='o', linewidth=2)
plt.title('Apple - Ingresos Históricos')
plt.xlabel('Fecha')
plt.ylabel('Ingresos (USD)')
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('ingresos_apple.png')
print("✓ Gráfico guardado: ingresos_apple.png")
```

#### Conceptos Personalizados

```python
# Extraer solo métricas específicas
conceptos_personalizados = [
    "Revenues",
    "GrossProfit",
    "OperatingIncomeLoss",
    "NetIncomeLoss",
    "EarningsPerShareBasic",
    "EarningsPerShareDiluted"
]

result = extractor.extract_custom_concepts(
    cik="0000320193",
    concepts=conceptos_personalizados,
    output_path=Path("metricas_clave.csv"),
    statement_name="Métricas Clave"
)

print(f"✓ Métricas guardadas: {result}")
```

---

## 🎯 Ejemplos Prácticos

### Ejemplo 1: Comparar ingresos de múltiples empresas

```python
from sec_filing_extractor import FilingManager
import pandas as pd

# Empresas a comparar
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
manager = FilingManager()

resultados = {}

for ticker in tickers:
    print(f"Procesando {ticker}...")

    # Obtener CIK
    company = manager.search_company(ticker)
    cik = company['cik']

    # Extraer financieros
    from sec_filing_extractor.extractors import FinancialStatementExtractor
    extractor = FinancialStatementExtractor()

    result = extractor.extract(cik, Path(f"temp_{ticker}"))

    # Cargar ingresos
    df = pd.read_csv(result['IS'])
    ultimo_ingreso = df.iloc[-1]['Revenues']

    resultados[ticker] = {
        'nombre': company['name'],
        'ingresos': ultimo_ingreso
    }

# Mostrar comparación
print("\n📊 Comparación de Ingresos")
print("="*60)
for ticker, data in sorted(resultados.items(),
                            key=lambda x: x[1]['ingresos'],
                            reverse=True):
    print(f"{ticker:6s} | {data['nombre']:30s} | ${data['ingresos']:,.0f}")
```

---

### Ejemplo 2: Buscar palabras clave en Risk Factors

```python
from sec_filing_extractor import FilingManager
from sec_filing_extractor.extractors import SectionExtractor
from pathlib import Path
import re

manager = FilingManager()

# Descargar 10-K
filings = manager.get_filings("TSLA", form_types=("10-K",), limit=1)
result = manager.download_filing(filings[0])

# Extraer secciones
extractor = SectionExtractor()
sections = extractor.extract(
    Path(result['preferred_view']),
    Path(result['filing_dir']) / "sections"
)

# Leer Item 1A (Risk Factors)
risk_file = Path(sections['sections']['1A'])
with open(risk_file, 'r', encoding='utf-8') as f:
    risk_text = f.read().lower()

# Palabras clave a buscar
keywords = [
    'competition',
    'supply chain',
    'regulation',
    'cybersecurity',
    'climate change',
    'recession',
    'inflation'
]

print("🔍 Análisis de Risk Factors - Tesla")
print("="*60)

for keyword in keywords:
    count = len(re.findall(r'\b' + keyword + r'\b', risk_text))
    if count > 0:
        print(f"✓ '{keyword}': mencionado {count} veces")
    else:
        print(f"  '{keyword}': no mencionado")
```

---

### Ejemplo 3: Descargar histórico completo de 10-K

```python
from sec_filing_extractor import FilingManager
from pathlib import Path

manager = FilingManager()
ticker = "AAPL"

# Obtener todos los 10-K disponibles
filings = manager.get_filings(ticker, form_types=("10-K",), limit=100)

print(f"Encontrados {len(filings)} documentos 10-K de {ticker}")

for i, filing in enumerate(filings, 1):
    print(f"\n[{i}/{len(filings)}] Descargando {filing.filing_date}...")

    try:
        # Descargar y procesar
        result = manager.process_filing_complete(
            filing,
            extract_tables=False,      # No extraer tablas (más rápido)
            extract_sections=False,    # No extraer secciones
            extract_financials=True    # Solo financials
        )

        print(f"  ✓ Guardado en: {result['download']['filing_dir']}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n✓ Proceso completado")
```

---

### Ejemplo 4: Crear dataset de métricas clave

```python
import pandas as pd
from pathlib import Path
from sec_filing_extractor import FilingManager

# Empresas del sector tech
tech_stocks = ["AAPL", "MSFT", "GOOGL", "META", "NVDA"]

# DataFrame para almacenar resultados
data = []

manager = FilingManager()

for ticker in tech_stocks:
    print(f"Procesando {ticker}...")

    company = manager.search_company(ticker)
    filings = manager.get_filings(ticker, form_types=("10-K",), limit=1)

    # Extraer financieros
    result = manager.process_filing_complete(
        filings[0],
        extract_tables=False,
        extract_sections=False,
        extract_financials=True
    )

    # Leer Income Statement
    is_path = Path(result['download']['filing_dir']) / "facts" / "IS.csv"
    df_is = pd.read_csv(is_path)

    # Último año
    ultimo = df_is.iloc[-1]

    data.append({
        'Ticker': ticker,
        'Empresa': company['name'],
        'Fecha': ultimo['Date'],
        'Ingresos': ultimo.get('Revenues', 0),
        'Beneficio_Neto': ultimo.get('NetIncomeLoss', 0),
        'Gastos_I+D': ultimo.get('ResearchAndDevelopmentExpense', 0)
    })

# Crear DataFrame
df_final = pd.DataFrame(data)

# Calcular ratios
df_final['Margen_Neto_%'] = (df_final['Beneficio_Neto'] / df_final['Ingresos']) * 100
df_final['I+D_sobre_Ingresos_%'] = (df_final['Gastos_I+D'] / df_final['Ingresos']) * 100

# Guardar
df_final.to_csv('comparacion_tech.csv', index=False)
print("\n✓ Dataset guardado: comparacion_tech.csv")
print(df_final)
```

---

## 💼 Casos de Uso Reales

### Caso 1: Analista Financiero

**Objetivo**: Comparar márgenes operativos de competidores

```python
from sec_filing_extractor import FilingManager
import pandas as pd

competidores = ["KO", "PEP"]  # Coca-Cola vs Pepsi
manager = FilingManager()

for ticker in competidores:
    filings = manager.get_filings(ticker, form_types=("10-K",), limit=1)
    result = manager.process_filing_complete(filings[0])

    # Analizar márgenes
    is_file = Path(result['download']['filing_dir']) / "facts" / "IS.csv"
    df = pd.read_csv(is_file)

    # Últimos 3 años
    df_reciente = df.tail(3)

    df_reciente['Margen_Operativo'] = (
        df_reciente['OperatingIncomeLoss'] / df_reciente['Revenues']
    ) * 100

    print(f"\n{ticker} - Márgenes Operativos:")
    print(df_reciente[['Date', 'Margen_Operativo']])
```

### Caso 2: Investigador Académico

**Objetivo**: Analizar divulgaciones de riesgos climáticos

```python
from sec_filing_extractor import FilingManager
from sec_filing_extractor.extractors import SectionExtractor
import re

# Empresas del S&P 500 (muestra)
empresas = ["XOM", "CVX", "BP"]  # Petroleras

resultados = []

for ticker in empresas:
    manager = FilingManager()
    filings = manager.get_filings(ticker, form_types=("10-K",), limit=1)
    result = manager.download_filing(filings[0])

    # Extraer Risk Factors
    extractor = SectionExtractor()
    sections = extractor.extract(
        Path(result['preferred_view']),
        Path(result['filing_dir']) / "sections"
    )

    # Leer Item 1A
    risk_file = sections['sections']['1A']
    with open(risk_file, 'r') as f:
        texto = f.read().lower()

    # Contar menciones
    menciones_clima = len(re.findall(r'climate change|carbon|emission|greenhouse', texto))

    resultados.append({
        'ticker': ticker,
        'menciones_clima': menciones_clima,
        'archivo': risk_file
    })

print("Menciones de cambio climático en Risk Factors:")
for r in resultados:
    print(f"{r['ticker']}: {r['menciones_clima']} menciones")
```

### Caso 3: Data Scientist

**Objetivo**: Crear dataset para modelo de ML

```python
from sec_filing_extractor import FilingManager
import pandas as pd
from pathlib import Path

# Lista de empresas
tickers = pd.read_csv('sp500_tickers.csv')['Ticker'].tolist()

# Dataset final
dataset = []

manager = FilingManager()

for ticker in tickers[:10]:  # Primeras 10 para prueba
    try:
        # Obtener últimos 5 años
        filings = manager.get_filings(ticker, form_types=("10-K",), limit=5)

        for filing in filings:
            result = manager.process_filing_complete(filing)

            # Cargar datos
            is_path = Path(result['download']['filing_dir']) / "facts" / "IS.csv"
            bs_path = Path(result['download']['filing_dir']) / "facts" / "BS.csv"

            df_is = pd.read_csv(is_path)
            df_bs = pd.read_csv(bs_path)

            # Combinar datos del último periodo
            ultimo_is = df_is.iloc[-1]
            ultimo_bs = df_bs.iloc[-1]

            dataset.append({
                'ticker': ticker,
                'fecha': ultimo_is['Date'],
                'ingresos': ultimo_is.get('Revenues', 0),
                'beneficio_neto': ultimo_is.get('NetIncomeLoss', 0),
                'activos': ultimo_bs.get('Assets', 0),
                'pasivos': ultimo_bs.get('Liabilities', 0),
                # ... más features
            })

    except Exception as e:
        print(f"Error con {ticker}: {e}")

# Guardar dataset
df_ml = pd.DataFrame(dataset)
df_ml.to_csv('ml_dataset.csv', index=False)
print(f"✓ Dataset creado: {len(df_ml)} registros")
```

---

## 🏗️ Arquitectura del Proyecto

### Estructura de Archivos

```
financial_tools/
│
├── 📁 sec_filing_extractor/          # Paquete principal
│   │
│   ├── 📄 __init__.py                # Exports del paquete
│   ├── 📄 config.py                  # Configuración
│   ├── 📄 exceptions.py              # Excepciones personalizadas
│   │
│   ├── 🌐 sec_client.py              # Cliente HTTP para SEC API
│   ├── 🔍 company_lookup.py          # Búsqueda de empresas
│   ├── 📥 filing_downloader.py       # Descarga de documentos
│   ├── 🎯 filing_manager.py          # Orquestador principal
│   ├── 💻 cli.py                     # Interfaz de línea de comandos
│   │
│   └── 📁 extractors/                # Extractores de datos
│       ├── 📄 __init__.py
│       ├── 📄 base.py                # Clase base
│       ├── 📊 table_extractor.py     # Extractor de tablas
│       ├── 📝 section_extractor.py   # Extractor de secciones
│       └── 💰 financial_extractor.py # Extractor de financials
│
├── 📄 main.py                        # Punto de entrada
├── 📄 requirements.txt               # Dependencias
├── 📄 setup.py                       # Instalación
├── 📄 README.md                      # Esta guía
└── 📄 .gitignore                     # Archivos a ignorar
```

### Flujo de Datos

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │
       ├─── Modo Interactivo ────────┐
       ├─── Modo Quick ──────────────┤
       └─── Modo Programático ───────┤
                                      │
                                      ▼
                            ┌──────────────────┐
                            │  FilingManager   │
                            └────────┬─────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
           ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
           │  Company    │  │   Filing     │  │  Extractors  │
           │  Lookup     │  │  Downloader  │  │              │
           └──────┬──────┘  └──────┬───────┘  └──────┬───────┘
                  │                │                  │
                  ▼                ▼                  ▼
           ┌─────────────────────────────────────────────┐
           │              SECClient                       │
           │        (Rate Limiting + Retry Logic)        │
           └──────────────────┬──────────────────────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │   SEC EDGAR API  │
                     └─────────────────┘
```

### Componentes Principales

#### 1. Config (config.py)

Gestiona toda la configuración del sistema:

```python
from sec_filing_extractor import Config

config = Config(
    user_agent="Mi App (mi@email.com)",  # Identificación ante SEC
    sec_api_base="https://data.sec.gov", # Base URL de API
    request_delay=0.2,                    # Delay entre requests
    max_retries=3,                        # Reintentos en caso de error
    log_level="INFO"                      # Nivel de logging
)
```

#### 2. SECClient (sec_client.py)

Cliente HTTP robusto con:
- ✅ Rate limiting automático
- ✅ Reintentos con backoff exponencial
- ✅ Manejo de errores
- ✅ Streaming para archivos grandes

```python
from sec_filing_extractor import SECClient

with SECClient(config) as client:
    # Obtener submissions
    data = client.get_company_submissions("0000320193")

    # Descargar archivo
    client.download_file(url, destino)
```

#### 3. CompanyLookup (company_lookup.py)

Resuelve tickers a CIKs:

```python
from sec_filing_extractor import CompanyLookup

lookup = CompanyLookup()
cik = lookup.get_cik_from_ticker("AAPL")
info = lookup.get_company_info("AAPL")
```

#### 4. FilingDownloader (filing_downloader.py)

Descarga documentos SEC:

```python
from sec_filing_extractor import FilingDownloader

downloader = FilingDownloader()
filings = downloader.get_recent_filings(cik, form_types=("10-K",))
files = downloader.download_filing(filings[0])
```

#### 5. Extractors (extractors/)

Extraen datos específicos:

- **TableExtractor**: HTML → CSV/JSON
- **SectionExtractor**: HTML → Markdown
- **FinancialStatementExtractor**: XBRL → CSV

#### 6. FilingManager (filing_manager.py)

Orquesta todo el proceso:

```python
from sec_filing_extractor import FilingManager

manager = FilingManager()
result = manager.process_filing_complete(filing)
```

---

## ⚙️ Configuración Avanzada

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Identificación (IMPORTANTE: usa tu email real)
SEC_USER_AGENT="Mi Aplicación - Juan Pérez (juan@example.com)"

# Carpeta de salida
SEC_OUTPUT_DIR="./mis_datos_sec"

# Logging
SEC_LOG_LEVEL="DEBUG"
SEC_LOG_FILE="sec_extractor.log"

# Rate Limiting
SEC_REQUEST_DELAY="0.3"
SEC_MAX_RETRIES="5"
```

Cargar configuración desde variables de entorno:

```python
import os
from dotenv import load_dotenv
from sec_filing_extractor import Config

# Cargar .env
load_dotenv()

# Config desde variables de entorno
config = Config.from_env()
```

### Configuración de Logging

#### Nivel Básico (Consola)

```python
config = Config(log_level="INFO")
```

#### Nivel Avanzado (Archivo + Consola)

```python
config = Config(
    log_level="DEBUG",
    log_file="logs/sec_extractor.log",
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

#### Logging Personalizado

```python
import logging

# Configurar manualmente
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

# Usar logger específico
logger = logging.getLogger('sec_filing_extractor')
logger.setLevel(logging.DEBUG)
```

### Personalizar User-Agent

⚠️ **MUY IMPORTANTE**: La SEC requiere que identifiques tu aplicación.

**Formato correcto:**

```python
config = Config(
    user_agent="NombreApp/1.0 (contacto@example.com)"
)
```

**Buenos ejemplos:**
- `"Investment Research Tool - Jane Doe (jane@research.com)"`
- `"Academic Study/1.0 (professor@university.edu)"`
- `"Financial Analysis Bot - FinTech Inc (api@fintech.com)"`

**Malos ejemplos (evitar):**
- `"Mozilla/5.0..."` (parece navegador)
- `"Python"` (demasiado genérico)
- `"Test"` (sin contacto)

### Configuración de Rate Limiting

```python
config = Config(
    request_delay=0.3,      # 300ms entre requests
    max_retries=5,          # 5 reintentos
    retry_delay=2.0         # 2s de delay base para reintentos
)
```

**Recomendaciones de la SEC:**
- Mínimo 200ms entre requests
- No más de 10 requests por segundo
- Identificación clara en User-Agent

---

## 🔧 Solución de Problemas

### Problema 1: "Ticker no encontrado"

**Error:**
```
TickerNotFoundError: Ticker 'XYZ' not found in SEC database
```

**Soluciones:**

1. Verifica que el ticker sea correcto:
   ```python
   # Buscar en Google Finance o Yahoo Finance primero
   ticker = "AAPL"  # Correcto
   ticker = "Apple" # ✗ Incorrecto
   ```

2. Algunos tickers tienen formato especial:
   ```python
   # Clase de acciones
   "BRK.A"  # Berkshire Hathaway Clase A
   "BRK.B"  # Berkshire Hathaway Clase B
   ```

3. Empresas extranjeras pueden no estar:
   ```python
   # Usar CIK directamente si conoces el número
   cik = "0000320193"
   ```

### Problema 2: "Rate limit exceeded"

**Error:**
```
RateLimitError: SEC API rate limit exceeded
```

**Soluciones:**

1. Aumentar delay entre requests:
   ```python
   config = Config(request_delay=0.5)  # 500ms
   ```

2. Reducir número de requests concurrentes

3. Esperar unos minutos antes de reintentar

### Problema 3: "Download failed"

**Error:**
```
DownloadError: Failed to download file: Connection timeout
```

**Soluciones:**

1. Verificar conexión a internet

2. Reintentar la descarga:
   ```python
   config = Config(
       max_retries=5,
       retry_delay=3.0
   )
   ```

3. Descargar sin exhibits si es muy grande:
   ```python
   result = manager.download_filing(
       filing,
       include_exhibits=False
   )
   ```

### Problema 4: "No tables extracted"

**Error:**
```
table_count: 0
```

**Soluciones:**

1. Verificar que el archivo HTML existe:
   ```python
   from pathlib import Path
   html_file = Path("filing.html")
   print(f"Existe: {html_file.exists()}")
   print(f"Tamaño: {html_file.stat().st_size} bytes")
   ```

2. Reducir min_columns:
   ```python
   result = extractor.extract(
       source=html_file,
       output_dir=output_dir,
       min_columns=1  # Menos restrictivo
   )
   ```

3. Algunos documentos no tienen tablas HTML (usan PDF o images)

### Problema 5: "No sections found"

**Error:**
```
section_count: 0
```

**Soluciones:**

1. Algunos 10-Q no tienen estructura de Items

2. Verificar que es un documento 10-K o 10-Q:
   ```python
   print(f"Form type: {filing.form}")
   ```

3. Probar con otro documento del mismo emisor

### Problema 6: ImportError

**Error:**
```
ModuleNotFoundError: No module named 'sec_filing_extractor'
```

**Soluciones:**

1. Verificar que estás en el directorio correcto:
   ```bash
   pwd  # Debe mostrar .../financial_tools
   ```

2. Reinstalar dependencias:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

3. Verificar Python path:
   ```python
   import sys
   print(sys.path)
   ```

### Problema 7: Encoding errors

**Error:**
```
UnicodeDecodeError: 'utf-8' codec can't decode
```

**Soluciones:**

Ya está manejado en el código con `errors="ignore"`, pero si persiste:

```python
# Leer archivo con encoding diferente
with open(file, 'r', encoding='latin-1') as f:
    content = f.read()
```

---

## ❓ Preguntas Frecuentes

### ¿Es gratis usar esta herramienta?

Sí, completamente gratis y open source. Los datos de la SEC también son públicos y gratuitos.

### ¿Necesito una API key?

No, la SEC no requiere API keys para acceso público.

### ¿Puedo descargar datos de cualquier empresa?

Solo empresas públicas que reportan a la SEC (empresas estadounidenses y algunas extranjeras listadas en USA).

### ¿Qué tan antiguos son los datos?

Depende de cada empresa, pero generalmente hay datos desde los años 90-2000 cuando comenzó EDGAR.

### ¿Con qué frecuencia se actualizan los datos?

- **10-K**: Anualmente (90 días después del fin de año fiscal)
- **10-Q**: Trimestralmente (45 días después del trimestre)
- **8-K**: Cuando ocurren eventos importantes

### ¿Puedo usar esto para trading?

Sí, pero considera:
- Los datos son históricos (no en tiempo real)
- Debes combinar con otras fuentes
- No es asesoramiento financiero

### ¿Cuánto espacio en disco necesito?

Depende:
- Un 10-K sin exhibits: ~5-20 MB
- Un 10-K con exhibits: ~50-200 MB
- Datos extraídos (CSV/MD): ~1-10 MB

### ¿Funciona en Windows/Mac/Linux?

Sí, es multiplataforma. Python funciona en todos los sistemas operativos.

### ¿Puedo modificar el código?

Sí, es open source (licencia MIT). Puedes modificar, distribuir y usar comercialmente.

### ¿Cómo reporto un bug?

Abre un issue en GitHub con:
- Descripción del problema
- Pasos para reproducirlo
- Mensaje de error completo
- Tu sistema operativo y versión de Python

---

## 📚 API Reference

### Config

```python
from sec_filing_extractor import Config

config = Config(
    user_agent: str = "SEC Filing Extractor (contact@example.com)",
    sec_api_base: str = "https://data.sec.gov",
    sec_files_base: str = "https://www.sec.gov",
    request_delay: float = 0.2,
    max_retries: int = 3,
    retry_delay: float = 1.0,
    default_output_dir: str = "filings",
    log_level: str = "INFO",
    log_file: str = None
)
```

**Métodos:**
- `setup_logging()`: Configura logging
- `from_env()`: Carga desde variables de entorno
- `update(**kwargs)`: Actualiza configuración

---

### FilingManager

```python
from sec_filing_extractor import FilingManager

manager = FilingManager(config: Config = None)
```

**Métodos principales:**

#### search_company()
```python
company_info = manager.search_company(ticker: str) -> Dict
```
Busca información de una empresa.

**Parámetros:**
- `ticker`: Símbolo bursátil (ej: "AAPL")

**Retorna:**
```python
{
    'ticker': 'AAPL',
    'cik': '0000320193',
    'name': 'Apple Inc.',
    'sic': '3571',
    'sic_description': 'ELECTRONIC COMPUTERS',
    'fiscal_year_end': '0928'
}
```

#### get_filings()
```python
filings = manager.get_filings(
    ticker: str,
    form_types: tuple = None,
    limit: int = 20
) -> List[Filing]
```

Obtiene documentos recientes.

**Parámetros:**
- `ticker`: Símbolo bursátil
- `form_types`: Tipos de formularios (ej: ("10-K", "10-Q"))
- `limit`: Número máximo de resultados

**Retorna:** Lista de objetos `Filing`

#### download_filing()
```python
result = manager.download_filing(
    filing: Filing,
    output_dir: Path = None,
    include_exhibits: bool = False
) -> Dict
```

Descarga un documento.

**Retorna:**
```python
{
    'filing_dir': Path,
    'files': List[str],
    'file_count': int,
    'preferred_view': str
}
```

#### process_filing_complete()
```python
result = manager.process_filing_complete(
    filing: Filing,
    output_dir: Path = None,
    include_exhibits: bool = False,
    extract_tables: bool = True,
    extract_sections: bool = True,
    extract_financials: bool = True
) -> Dict
```

Descarga y procesa completamente un documento.

---

### TableExtractor

```python
from sec_filing_extractor.extractors import TableExtractor

extractor = TableExtractor(config: Config = None)
```

#### extract()
```python
result = extractor.extract(
    source: Path,
    output_dir: Path,
    min_columns: int = 2,
    max_tables: int = 200
) -> Dict
```

**Retorna:**
```python
{
    'csv_files': List[str],
    'json_file': str,
    'table_count': int,
    'source': str
}
```

---

### SectionExtractor

```python
from sec_filing_extractor.extractors import SectionExtractor

extractor = SectionExtractor(config: Config = None)
```

#### extract()
```python
result = extractor.extract(
    source: Path,
    output_dir: Path
) -> Dict
```

**Retorna:**
```python
{
    'sections': Dict[str, str],  # item_id -> file_path
    'index_file': str,
    'section_count': int,
    'source': str
}
```

---

### FinancialStatementExtractor

```python
from sec_filing_extractor.extractors import FinancialStatementExtractor

extractor = FinancialStatementExtractor(config: Config = None)
```

#### extract()
```python
result = extractor.extract(
    cik: str,
    output_dir: Path,
    save_raw: bool = True
) -> Dict
```

**Retorna:**
```python
{
    'IS': str,              # Income Statement path
    'BS': str,              # Balance Sheet path
    'CF': str,              # Cash Flow path
    'raw_json': str,        # Raw XBRL data
    'statement_count': int,
    'cik': str
}
```

#### extract_custom_concepts()
```python
result = extractor.extract_custom_concepts(
    cik: str,
    concepts: List[str],
    output_path: Path,
    statement_name: str = "Custom"
) -> Path
```

---

## 🌟 Mejores Prácticas

### 1. Siempre usa User-Agent apropiado

```python
# ✓ Correcto
config = Config(user_agent="Mi App - John Doe (john@example.com)")

# ✗ Incorrecto
config = Config(user_agent="Python")
```

### 2. Maneja errores apropiadamente

```python
from sec_filing_extractor.exceptions import SECFilingException

try:
    result = manager.get_filings("AAPL")
except SECFilingException as e:
    logger.error(f"Error específico de SEC: {e}")
except Exception as e:
    logger.error(f"Error inesperado: {e}")
```

### 3. Usa context managers

```python
# ✓ Correcto - cierra recursos automáticamente
with FilingManager() as manager:
    result = manager.get_filings("AAPL")

# ✗ Incorrecto - puede dejar conexiones abiertas
manager = FilingManager()
result = manager.get_filings("AAPL")
```

### 4. Configura logging apropiadamente

```python
# Desarrollo
config = Config(log_level="DEBUG", log_file="debug.log")

# Producción
config = Config(log_level="WARNING", log_file="errors.log")
```

### 5. No hagas requests excesivos

```python
# ✓ Correcto - descarga una vez, procesa múltiples veces
result = manager.download_filing(filing)
# ... analizar datos descargados ...

# ✗ Incorrecto - descarga múltiples veces
for i in range(10):
    result = manager.download_filing(filing)  # No hacer esto!
```

### 6. Valida datos antes de usar

```python
import pandas as pd

df = pd.read_csv("IS.csv")

# Validar que hay datos
if df.empty:
    raise ValueError("No hay datos en el archivo")

# Validar columnas esperadas
required_cols = ['Date', 'Revenues']
if not all(col in df.columns for col in required_cols):
    raise ValueError("Faltan columnas requeridas")

# Validar valores
if df['Revenues'].isna().all():
    raise ValueError("No hay datos de ingresos")
```

---

## 📞 Soporte y Contacto

### Reportar Issues

Si encuentras un problema:

1. Verifica que no esté ya reportado en [Issues](https://github.com/hectoorperezz/financial_tools/issues)
2. Crea un nuevo issue con:
   - Título descriptivo
   - Pasos para reproducir
   - Error completo
   - Sistema operativo y versión de Python
   - Versión de la herramienta

### Contribuir

¡Las contribuciones son bienvenidas!

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'Agrega nueva funcionalidad'`
4. Push: `git push origin feature/nueva-funcionalidad`
5. Crea un Pull Request

### Recursos Adicionales

- 📖 [Documentación oficial de SEC EDGAR](https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm)
- 📊 [Guía de formularios SEC](https://www.sec.gov/forms)
- 💡 [XBRL Fundamentals](https://www.sec.gov/structureddata/osd-inline-xbrl.html)

---

## 📄 Licencia

MIT License - Ver archivo LICENSE para detalles.

---

## 🙏 Agradecimientos

- SEC por proporcionar datos públicos y gratuitos
- Comunidad open source de Python
- Todos los contribuidores del proyecto

---

<div align="center">

**¿Te resultó útil? Dale una ⭐ en GitHub!**

[Reportar Bug](https://github.com/hectoorperezz/financial_tools/issues) · [Solicitar Feature](https://github.com/hectoorperezz/financial_tools/issues) · [Documentación](https://github.com/hectoorperezz/financial_tools/wiki)

---

Hecho con ❤️ para la comunidad financiera y de análisis de datos

</div>
