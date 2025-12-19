variable "db_host" {
  description = "Host de la base de datos Supabase (ej. db.xyz.supabase.co)"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Contraseña del usuario postgres de Supabase"
  type        = string
  sensitive   = true
}
