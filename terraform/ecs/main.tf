# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = var.cluster_name
}

# Security group for ECS tasks
resource "aws_security_group" "ecs_tasks" {
  name        = "ecs-tasks-sg"
  description = "Allow traffic from ALB to ECS tasks"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # ALB security group will refine this later
  }

  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "ecs-tasks-sg" }
}

resource "aws_appautoscaling_target" "ecs_service" {
  max_capacity       = 1
  min_capacity       = 0
  resource_id        = "service/${var.cluster_name}/${var.service_name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_scheduled_action" "scale_down" {
  name               = "scale-down-night"
  service_namespace  = "ecs"
  resource_id        = aws_appautoscaling_target.ecs_service.resource_id
  scalable_dimension = "ecs:service:DesiredCount"
  schedule           = "cron(0 1 * * ? *)" # 1 AM UTC
  scalable_target_action {
    min_capacity = 0
    max_capacity = 0
  }
}

resource "aws_appautoscaling_scheduled_action" "scale_up" {
  name               = "scale-up-morning"
  service_namespace  = "ecs"
  resource_id        = aws_appautoscaling_target.ecs_service.resource_id
  scalable_dimension = "ecs:service:DesiredCount"
  schedule           = "cron(0 11 * * ? *)" # 8 AM UTC
  scalable_target_action {
    min_capacity = 1
    max_capacity = 1
  }
}