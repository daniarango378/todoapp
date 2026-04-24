# infra/outputs.tf

# ============================================================
# BACKEND
# ============================================================

output "backend_ecs_cluster_name" {
  description = "Nombre del ECS Cluster compartido"
  value       = aws_ecs_cluster.main.name
}

output "backend_ecs_service_name" {
  description = "Nombre del ECS Service del backend"
  value       = aws_ecs_service.backend.name
}

# La IP pública de la tarea backend NO es un output de Terraform porque
# Fargate la asigna dinámicamente en el momento del arranque.
# Para obtenerla después del apply:
#   aws ecs list-tasks --cluster <cluster_name> --service-name <backend_service_name>
#   aws ecs describe-tasks --cluster <cluster_name> --tasks <task_arn>
#   # Busca el campo "privateIpv4Address" y luego la ENI para la IP pública, o usa:
#   aws ec2 describe-network-interfaces --filters Name=description,Values="*<task_id>*" \
#     --query "NetworkInterfaces[0].Association.PublicIp"
output "backend_ip_hint" {
  description = "Cómo obtener la IP pública del backend tras el apply"
  value       = "Ejecuta: aws ecs describe-tasks --cluster ${aws_ecs_cluster.main.name} --tasks $(aws ecs list-tasks --cluster ${aws_ecs_cluster.main.name} --service-name ${aws_ecs_service.backend.name} --query 'taskArns[0]' --output text) --query 'tasks[0].attachments[0].details' --region ${var.aws_region}"
}

# ============================================================
# FRONTEND
# ============================================================

output "frontend_alb_dns_name" {
  description = "DNS Name del Application Load Balancer del frontend"
  value       = aws_lb.frontend.dns_name
}

output "frontend_alb_url" {
  description = "URL completa del ALB del frontend (con http://)"
  value       = "http://${aws_lb.frontend.dns_name}/"
}

output "frontend_ecs_service_name" {
  description = "Nombre del ECS Service del frontend"
  value       = aws_ecs_service.frontend.name
}
