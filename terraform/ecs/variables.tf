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