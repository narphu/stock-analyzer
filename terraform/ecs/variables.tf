variable "vpc_id" {}
variable "public_subnets" {
  type = list(string)
}

variable "backend_image" {}
variable "subnets" {
  type = list(string)
}
variable "ecs_tasks_sg_id" {}
variable "backend_tg_arn" {}
variable "ecs_cluster_id" {}
variable "cluster_name" {
  description = "Name of ECS cluster"
  type        = string
  }
variable "service_name" {
  description = "Name of the service within the ECS cluster"
  type        = string
}