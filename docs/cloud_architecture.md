# Arquitectura de Nube Híbrida (On-Prem to Cloud)

Esta arquitectura implementa un modelo **ELT (Extract, Load, Transform)** híbrido donde la extracción y transformación inicial ocurren en un entorno local (o contenedorizado), y los datos procesados se cargan a un Data Warehouse en la nube para análisis y visualización.

## Diagrama de Flujo

```mermaid
graph LR
    A["CoinGecko API"] -->|"Extracción (JSON)"| B("Script Local Python")
    B -->|"Transformación (Pandas)"| B
    B -->|"Carga (SSL/TCP)"| C{"Base de Datos Cloud"}
    C -->|"Consultas SQL"| D["Analítica / Dashboard"]
    
    subgraph "Entorno Local / Docker"
    B
    end
    
    subgraph "Proveedor Cloud (Supabase/Render)"
    C
    end
```

## Componentes

### 1. Fuente de Datos (Source)
- **Proveedor**: CoinGecko API (Public).
- **Datos**: Precios históricos, volumen, capitalización de mercado.
- **Frecuencia**: Ejecución bajo demanda (o programada con cron/Task Scheduler).

### 2. Procesamiento Local (ETL Worker)
- **Tecnología**: Python 3.11 + Pandas + SQLAlchemy.
- **Responsabilidad**:
  - Obtener datos de la API.
  - Limpieza básica (fechas, nulos).
  - Cálculo de KPIs pre-agregados (Rentabilidad, Volatilidad).
  - Generación de DataFrame final.

### 3. Almacenamiento en Nube (Cloud Warehouse)
- **Tecnología**: PostgreSQL (Supabase / Render / Railway).
- **Ventajas**:
  - **Supabase**: Capa gratuita generosa (500MB), interfaz UI excelente, API automática.
  - **Render**: Despliegue fácil desde GitHub, capa gratuita (borra datos tras inactividad en free tier, recomendado plan starter para persistencia crítica).
  - **Railway**: Fácil configuración, créditos iniciales.
- **Seguridad**: Conexión cifrada (SSL Mode = Require).

## Guía de Configuración (Supabase Ejemplo)

1. **Crear Proyecto**:
   - Registrarse en [supabase.com](https://supabase.com).
   - Crear nuevo proyecto "CryptoAnalytics".
   
2. **Obtener Credenciales**:
   - Ir a Project Settings -> Database -> Connection String -> URI.
   - Copiar el string (e.g., `postgresql://postgres:[PASSWORD]@db.project.supabase.co:5432/postgres`).

3. **Configurar Entorno Local**:
   - Crear archivo `.env` en la raíz del proyecto.
   - Añadir la variable `DATABASE_URL`:
     ```bash
     DATABASE_URL="postgresql://postgres:tu_password@db.xyz.supabase.co:5432/postgres"
     ```

4. **Ejecutar Pipeline**:
   - El script `src/main.py` detectará automáticamente la variable de entorno y cargará los datos a la nube en lugar de la base de datos local.

## Consultas Analíticas
Las consultas SQL avanzadas para explotar estos datos se encuentran en `src/analytics/queries.sql`. Incluyen:
- Promedios móviles (7d, 30d).
- Rankings de riesgo (volatilidad).
- Análisis de crecimiento anómalo (Z-Score).
