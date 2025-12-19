terraform {
  required_providers {
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "1.21.0"
    }
  }
}

provider "postgresql" {
  host            = var.db_host
  port            = 5432
  database        = "postgres"
  username        = "postgres"
  password        = var.db_password
  sslmode         = "require"
  connect_timeout = 15
  superuser       = false
}

# --- Tablas (DDL) ---

# Tabla: cryptocurrency_prices
resource "postgresql_table" "cryptocurrency_prices" {
  name   = "cryptocurrency_prices"
  schema = "public"
  
  columns {
    name = "row_index"
    type = "bigint"
  }
  columns {
    name     = "coin"
    type     = "text"
    nullable = false
  }
  columns {
    name     = "price_timestamp"
    type     = "timestamp without time zone"
    nullable = false
  }
  columns {
    name = "price"
    type = "numeric"
  }
  columns {
    name = "volume"
    type = "numeric"
  }
  columns {
    name = "market_cap"
    type = "numeric"
  }

  // La definición de Clave Primaria Compuesta no está soportada directamente en el bloque 'columns' para algunas versiones,
  // usualmente se maneja con restricciones separadas o SQL crudo.
  // El provider 'cyrilgdn/postgresql' maneja bien las tablas, pero para gestión de esquemas complejos
  // es a menudo más fácil usar 'postgresql_execution' para SQL crudo si las claves son complejas.
  // Por robustez en esta demo, lo mantendremos simple o usaremos ejecución de SQL crudo
  // si se necesitan características específicas, pero nos quedaremos con la definición de recursos.
}

# Tabla: cryptocurrency_metrics
resource "postgresql_table" "cryptocurrency_metrics" {
  name   = "cryptocurrency_metrics"
  schema = "public"

  columns {
    name     = "coin"
    type     = "text"
    nullable = false
  }
  columns {
    name     = "price_timestamp"
    type     = "timestamp without time zone"
    nullable = false
  }
  columns {
    name = "price_change_24h"
    type = "numeric"
  }
  columns {
    name = "profitability_30d"
    type = "numeric"
  }
  columns {
    name = "volatility_30d"
    type = "numeric"
  }
  columns {
    name = "price_change_7d"
    type = "numeric"
  }
  columns {
    name = "price_change_30d"
    type = "numeric"
  }
  columns {
    name = "market_cap_change_24h"
    type = "numeric"
  }
  columns {
    name = "market_cap_change_7d"
    type = "numeric"
  }
   columns {
    name = "market_cap_change_30d"
    type = "numeric"
  }
  columns {
    name = "volume_change_24h"
    type = "numeric"
  }
  columns {
    name = "volume_change_7d"
    type = "numeric"
  }
  columns {
    name = "volume_change_30d"
    type = "numeric"
  }
}
