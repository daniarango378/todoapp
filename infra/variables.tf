# infra/variables.tf

variable "environment_name" {
  description = "Nombre del entorno (ej: staging, production). Usado para nombrar recursos."
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment_name)
    error_message = "El entorno debe ser 'staging' o 'production'."
  }
}

# --- Imágenes Docker (Docker Hub) ---
variable "backend_docker_image_uri" {
  description = "URI completo de la imagen Docker del backend en Docker Hub (ej: usuario/todoapp-backend:tag)."
  type        = string
}

variable "frontend_docker_image_uri" {
  description = "URI completo de la imagen Docker del frontend en Docker Hub (ej: dgrisalesp/todoapp-frontend:latest)."
  type        = string
  default     = "dgrisalesp/todoapp-frontend"
}

# --- IAM / Red ---
variable "lab_role_arn" {
  description = "ARN completo del rol IAM 'LabRole' existente en la cuenta."
  type        = string
}

variable "vpc_id" {
  description = "ID de la VPC por defecto donde desplegar."
  type        = string
}

variable "subnet_ids" {
  description = "Lista de al menos DOS IDs de subredes públicas de la VPC por defecto en diferentes AZs."
  type        = list(string)
}

variable "aws_region" {
  description = "Región de AWS a usar."
  type        = string
  default     = "us-east-1"
}

# --- Puertos ---
variable "backend_port" {
  description = "Puerto en el que escucha el contenedor backend."
  type        = number
  default     = 5001
}

variable "frontend_port" {
  description = "Puerto en el que escucha el contenedor frontend."
  type        = number
  default     = 8000
}

# --- Dirección del backend (inyectada en el frontend como TASK_API_BASE_URL) ---
# En el primer apply solo despliega el backend, obtén su IP pública desde
# la consola ECS > Tasks > ENI > Public IP, y luego rellena este valor
# antes del segundo apply que despliega el frontend.
variable "backend_public_ip" {
  description = "IP pública (o DNS) de la tarea Fargate del backend. Se inyecta como TASK_API_BASE_URL en el frontend."
  type        = string
  default     = ""
}

# --- Secretos Flask ---
variable "secret_key" {
  description = "Clave secreta para Flask (usada por flask-wtf para tokens CSRF). Nunca se imprime en logs gracias a sensitive = true."
  type        = string
  sensitive   = true
  default     = "dev-only-insecure-key"
}
