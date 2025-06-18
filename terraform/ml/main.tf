resource "aws_s3_bucket" "ml_model_bucket" {
  bucket = var.bucket_name
  force_destroy = true

  tags = {
    Name = var.bucket_name
    Env  = "prod"
    Project = "StockAnalyzer"
  }
}

resource "aws_s3_bucket_versioning" "ml_model_bucket" {
  bucket = aws_s3_bucket.ml_model_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# IAM Role for SageMaker Training Job
resource "aws_iam_role" "sagemaker_execution" {
  name = "shrubb-ai-sagemaker-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "sagemaker.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# IAM Policy for SageMaker Training Role
resource "aws_iam_role_policy" "sagemaker_policy" {
  name = "shrubb-ai-sagemaker-policy"
  role = aws_iam_role.sagemaker_execution.name

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Resource = [
          "${aws_s3_bucket.ml_model_bucket.arn}",
          "${aws_s3_bucket.ml_model_bucket.arn}/*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "cloudwatch:*",
          "logs:*",
          "ecr:*"
        ],
        Resource = "*"
      }
    ]
  })
}

# IAM Policy for ECS to Download from S3
resource "aws_iam_policy" "ecs_model_read_policy" {
  name = "shrubb-ecs-read-models"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Resource = [
          "${aws_s3_bucket.ml_model_bucket.arn}",
          "${aws_s3_bucket.ml_model_bucket.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_attach_model_policy" {
  role       = var.ecs_task_execution_role_name
  policy_arn = aws_iam_policy.ecs_model_read_policy.arn
}

