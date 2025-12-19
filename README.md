# Cryptocurrency Market Data Analytics

> **Enterprise Data Engineering Project** | Solución Híbrida ETL & Cloud Data Warehousing | Proyecto Profesional

---

## 📋 Tabla de Contenidos

- [Descripción General](#descripción-general)
- [Arquitectura de Datos](#arquitectura-de-datos)
- [Pipeline ETL & Data Quality](#pipeline-etl--data-quality)
- [Análisis y KPIs de Negocio](#análisis-y-kpis-de-negocio)
- [Stack Tecnológico](#stack-tecnológico)
- [Validación de Datos (SQL)](#validación-de-datos-sql)
- [Guía de Instalación](#guía-de-instalación)
- [Infraestructura como Código](#infraestructura-como-código)

---

## 📊 Descripción General

Este proyecto constituye una solución de **Ingeniería de Datos de nivel empresarial**, desarrollada bajo requerimiento de una **empresa partner** de **Soy Henry**. El objetivo fue diseñar e implementar una arquitectura escalable y mantenible para el análisis histórico y predictivo del mercado de criptomonedas.

La solución implementa un ciclo de vida completo de datos (End-to-End), integrando fuentes externas (API), procesamiento robusto en Python y almacenamiento en la nube mediante **Supabase (PostgreSQL)**, gestionando la infraestructura mediante código (**Terraform**).

**Características Profesionales:**
- 🏢 **Entorno Corporativo Simulado**: Requerimientos reales de negocio para toma de decisiones de inversión.
- ☁️ **Arquitectura Híbrida**: Procesamiento local/Docker y almacenamiento Cloud en Supabase.
- 🛡️ **Data Quality**: Implementación de checks estrictos (Nulls, Frescura, Duplicados) antes y después de la carga.
- 🏗️ **Infrastructure as Code (IaC)**: Gestión de esquemas de base de datos reproducible mediante **Terraform**.
- 📊 **Business Intelligence Ready**: Datos normalizados y KPIs pre-calculados listos para consumo analítico.

---

## 📈 Métricas de Rendimiento (Pipeline KPIs)

| Métrica | Valor Actual |
|---------|--------------|
| **Volumen de Datos** | Datos históricos multianuales + Actualización diaria |
| **Tiempo de Ejecución ETL** | ~45s (Carga Incremental) |
| **Integridad de Datos** | 100% (Validado por `src/data_quality.py`) |
| **Costo Operativo** | **$0.00 / mes** (Supabase Free Tier + CoinGecko Free API) |
| **Cobertura de Monedas** | Top Market Cap (Bitcoin, Ethereum, etc.) |

---

## 🏗️ Arquitectura de Datos

El proyecto implementa un flujo de datos moderno y modular:

```mermaid
graph LR
    API[CoinGecko API] -->|JSON| ETL[Python ETL Processor]
    ETL -->|Pandas/Transform| QC{Data Quality Checks}
    QC -->|Pass| DB[(Supabase Postgres)]
    DB -->|SQL| BI[Analítica / Dashboard]
    
    subgraph "Infraestructura & Gestión"
        TF[Terraform IaC] -->|Deploy Schema| DB
        AF[Airflow DAG] -->|Orquestación| ETL
    end
```

Ver estrategia de datos detallada en [docs/data_model_strategy.md](./docs/data_model_strategy.md).

---

## 🔄 Pipeline ETL & Data Quality

### 1. **Extract (Extracción)**
- Ingesta de datos históricos y de mercado en tiempo real desde **CoinGecko API**.
- Manejo de Rate Limits y paginación automática.

### 2. **Transform (Transformación)**
- Limpieza y normalización con **Pandas**.
- Cálculo vectorizado de métricas financieras (Retorno Diario, Volatilidad Móvil).

### 3. **Load (Carga)**
- **Supabase (PostgreSQL)**: Carga optimizada mediante `SQLAlchemy`.
- Soporte dual: **Carga Histórica** (Full Refresh) y **Carga Incremental** (Append Only).

### 4. **Data Quality & Logging**
- **Logging Centralizado**: Trazabilidad completa de cada ejecución en `src/utils/logger.py`.
- **Quality Gates**: El pipeline falla automáticamente si no se cumplen reglas de negocio (ej. duplicados, frescura > 2 días).

---

## 🔍 Análisis y KPIs de Negocio

El modelo de datos está diseñado para responder a tres indicadores clave de desempeño (KPIs) solicitados por el negocio:

| KPI | Descripción | Objetivo |
|-----|-------------|----------|
| **1. Capitalización de Mercado** | Evolución del tamaño de mercado y volumen (2019-2023). | Comprender ciclos de mercado y dominancia. |
| **2. Rentabilidad Mensual** | Variación porcentual del precio mes a mes. | Objetivo: > 5% mensual (Simulación de estrategia). |
| **3. Volatilidad Mensual** | Desviación estándar de los retornos diarios. | Objetivo: Reducción del 1% mensual (Gestión de riesgo). |

---

## 🛠️ Stack Tecnológico

| Categoría | Tecnologías |
|-----------|-------------|
| **Lenguaje** | ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) 3.10+ |
| **Cloud Database** | ![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white) (PostgreSQL) |
| **IaC** | ![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white) |
| **Orquestación** | ![Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white) |
| **Librerías** | ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white) |
| **Entorno** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) |

---

## 📡 Validación de Datos (SQL)

Consultas listas para validar la integridad en el SQL Editor de Supabase:

```sql
-- Verificar frescura de datos
SELECT MAX(price_timestamp) FROM cryptocurrency_prices;

-- Detectar duplicados
SELECT coin, price_timestamp, COUNT(*) 
FROM cryptocurrency_prices 
GROUP BY coin, price_timestamp 
HAVING COUNT(*) > 1;
HAVING COUNT(*) > 1;
```

---

## � Solución de Problemas (Troubleshooting)

### 1. Error de Conexión a Base de Datos
- **Síntoma**: `OperationalError: connection to server failed`.
- **Solución**: Asegúrate de que el contenedor de Docker esté corriendo (`docker ps`) o que la URL de Supabase en `.env` sea correcta.

### 2. Rate Limit de CoinGecko
- **Síntoma**: Error HTTP 429.
- **Causa**: El plan gratuito de CoinGecko tiene límites de peticiones.
- **Solución**: El script incluye pausas automáticas, pero si persiste, espera 1-2 minutos antes de reintentar. No se requiere API Key para la funcionalidad básica.

---

## �📦 Guía de Instalación

### Requisitos
- Python 3.10+
- Terraform (opcional, para despliegue de infraestructura)
- Cuenta en Supabase

### Instalación Local

```bash
# 1. Clonar repositorio
# 1. Clonar repositorio
git clone https://github.com/franco18min/Cryptocurrency-Market-Data-Analytics.git
cd Cryptocurrency-Market-Data-Analytics
cd Cryptocurrency-Market-Data-Analytics

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
# Crear archivo .env con:
# DATABASE_URL=postgresql://user:password@host:5432/postgres

# 4. Levantar Base de Datos Local (Docker)
docker-compose up -d

# 5. Ejecutar Pipeline (Modo Histórico)
python -m src.main

# 6. Ejecutar Pipeline (Modo Incremental)
python -m src.main --incremental
```

---

## 🏗️ Infraestructura como Código

Para desplegar el esquema de base de datos de forma reproducible:

```powershell
# Desde carpeta /terraform
terraform init
terraform apply
# Ingresar host y password de Supabase cuando se solicite
```

---

## 👤 Autor

<div align="center">
<img src="https://github.com/franco18min.png" width="120px" style="border-radius: 50%;">
<h3>Franco Aguilera</h3>
<p><strong>Data Engineer</strong> | Data Science @ Soy Henry</p>
<a href="https://www.linkedin.com/in/franco-aguilera-data-engineer/">
<img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"/>
</a>
<a href="https://github.com/franco18min">
<img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"/>
</a>
</div>

---

## 📄 Licencia

Este proyecto es una solución académica-profesional desarrollada bajo estándares corporativos.