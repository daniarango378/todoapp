# infra/main.tf

terraform {
  required_version = ">= 1.6.0"
  backend "s3" {
    bucket = "cicd-project-3"
    key    = "dev/terraform.tfstate"
    region = "us-east-1"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ============================================================
# LOGS
# ============================================================

resource "aws_cloudwatch_log_group" "backend_logs" {
  name              = "/ecs/todoapp-${var.environment_name}-backend"
  retention_in_days = 7
  tags = { Environment = var.environment_name }
}

resource "aws_cloudwatch_log_group" "frontend_logs" {
  name              = "/ecs/todoapp-${var.environment_name}-frontend"
  retention_in_days = 7
  tags = { Environment = var.environment_name }
}

# ============================================================
# CLUSTER ECS (compartido por ambos servicios)
# ============================================================

resource "aws_ecs_cluster" "main" {
  name = "todoapp-${var.environment_name}-cluster"
  tags = { Environment = var.environment_name }
}

# ============================================================
# SECURITY GROUPS
# ============================================================

# --- Backend: expone el puerto 5001 directamente a internet ---
# El frontend lo referencia por IP pública de la tarea Fargate.
resource "aws_security_group" "backend_sg" {
  name        = "backend-sg-${var.environment_name}"
  description = "Permite trafico HTTP al backend en el puerto ${var.backend_port}"
  vpc_id      = var.vpc_id

  ingress {
    description = "API backend desde internet"
    from_port   = var.backend_port
    to_port     = var.backend_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Environment = var.environment_name }
}

# --- ALB del frontend: acepta HTTP en el 80 ---
resource "aws_security_group" "frontend_alb_sg" {
  name        = "frontend-alb-sg-${var.environment_name}"
  description = "Permite trafico HTTP al ALB del frontend"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP desde internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Environment = var.environment_name }
}

# --- Servicio ECS del frontend: solo acepta tráfico desde su ALB ---
resource "aws_security_group" "frontend_ecs_sg" {
  name        = "frontend-ecs-sg-${var.environment_name}"
  description = "Permite trafico desde el ALB al servicio ECS frontend"
  vpc_id      = var.vpc_id

  ingress {
    description     = "Trafico desde el ALB del frontend"
    from_port       = var.frontend_port
    to_port         = var.frontend_port
    protocol        = "tcp"
    security_groups = [aws_security_group.frontend_alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Environment = var.environment_name }
}

# ============================================================
# BACKEND — Task Definition + Service (sin ALB)
# ============================================================

resource "aws_ecs_task_definition" "backend" {
  family                   = "todoapp-${var.environment_name}-backend-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  task_role_arn            = var.lab_role_arn
  execution_role_arn       = var.lab_role_arn

  container_definitions = jsonencode([
    {
      name  = "todoapp-${var.environment_name}-backend"
      image = var.backend_docker_image_uri

      portMappings = [
        {
          containerPort = var.backend_port
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "FLASK_SECRET_KEY"
          value = var.secret_key
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.backend_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = { Environment = var.environment_name }
}

resource "aws_ecs_service" "backend" {
  name            = "todoapp-${var.environment_name}-backend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.backend_sg.id]
    assign_public_ip = true # La IP pública es el endpoint que usará el frontend
  }

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  lifecycle {
    ignore_changes = [desired_count]
  }

  tags = { Environment = var.environment_name }
}

# ============================================================
# FRONTEND — ALB + Task Definition + Service
# ============================================================

# --- Load Balancer ---
resource "aws_lb" "frontend" {
  name               = "todoapp-${var.environment_name}-fe-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.frontend_alb_sg.id]
  subnets            = var.subnet_ids

  tags = { Environment = var.environment_name }
}

resource "aws_lb_target_group" "frontend_tg" {
  name        = "tg-fe-${var.environment_name}"
  port        = var.frontend_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip" # Requerido para Fargate

  health_check {
    enabled             = true
    path                = "/"
    port                = tostring(var.frontend_port)
    protocol            = "HTTP"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 15
    timeout             = 5
    matcher             = "200"
  }

  tags = { Environment = var.environment_name }
}

resource "aws_lb_listener" "frontend_http" {
  load_balancer_arn = aws_lb.frontend.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend_tg.arn
  }
}

# --- Task Definition ---
# NOTA: TASK_API_BASE_URL apunta al DNS del ALB del backend si existe,
# o a la IP pública de la tarea backend cuando no hay ALB.
# Actualiza este valor después del primer `apply` del backend
# con la IP pública real asignada a la tarea Fargate.
resource "aws_ecs_task_definition" "frontend" {
  family                   = "todoapp-${var.environment_name}-frontend-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  task_role_arn            = var.lab_role_arn
  execution_role_arn       = var.lab_role_arn

  container_definitions = jsonencode([
    {
      name  = "todoapp-${var.environment_name}-frontend"
      image = var.frontend_docker_image_uri

      portMappings = [
        {
          containerPort = var.frontend_port
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          # Apunta al backend. Cambia esta URL tras obtener la IP/DNS del backend.
          name  = "TASK_API_BASE_URL"
          value = "http://${var.backend_public_ip}:${var.backend_port}"
        },
        {
          name  = "FLASK_SECRET_KEY"
          value = var.secret_key
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.frontend_logs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])

  tags = { Environment = var.environment_name }
}

# --- Servicio ECS del Frontend ---
resource "aws_ecs_service" "frontend" {
  name            = "todoapp-${var.environment_name}-frontend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = [aws_security_group.frontend_ecs_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend_tg.arn
    container_name   = "todoapp-${var.environment_name}-frontend"
    container_port   = var.frontend_port
  }

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  lifecycle {
    ignore_changes = [desired_count]
  }

  depends_on = [aws_lb_listener.frontend_http]

  tags = { Environment = var.environment_name }
}
