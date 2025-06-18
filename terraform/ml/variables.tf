variable "bucket_name" {
  description = "Name of the S3 bucket to host ML Models"
  default =  "shrubb-ai-ml-models"
  type        = string
}

variable "ecs_task_execution_role_name" {
    description = "Name of ECS role"
    type = string
}