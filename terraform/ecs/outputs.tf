output "ecs_cluster_id" {
  value = aws_ecs_cluster.main.id
}

output "ecs_tasks_sg_id" {
  value = aws_security_group.ecs_tasks.id
}

output "backend_service_name" {
  value = aws_ecs_service.backend.name
}

output "ecs_task_execution_role_name" {
  value = aws_iam_role.ecs_task_execution.name
}
