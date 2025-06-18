provider "aws" {
  region = "us-east-1" # Main region for ECS, ALB, VPC
}

module "network" {
  source = "./network"
}

module "ecs" {
  source = "./ecs"

  vpc_id             = module.network.vpc_id
  public_subnets     = module.network.public_subnets
  ecs_cluster_id     = module.ecs.ecs_cluster_id
  ecs_tasks_sg_id    = module.ecs.ecs_tasks_sg_id
  backend_image      = "896924684176.dkr.ecr.us-east-1.amazonaws.com/stock-analyzer-backend:v0.0.2"
  backend_tg_arn     = module.network.backend_tg_arn
  subnets            = module.network.public_subnets
}

module "s3cloudfront" {
  source      = "./s3cloudfront"
  bucket_name = "shrubb-stock-analyzer-frontend"
  acm_certificate_arn = module.network.frontend_cert_arn
  tags = {
    Project = "StockAnalyzer"
    Env     = "prod"
  }
}

module "ml" {
  source      = "./ml"
  bucket_name = "shrubb-ai-ml-models"
  ecs_task_execution_role_name = module.ecs.ecs_task_execution_role_name
}

