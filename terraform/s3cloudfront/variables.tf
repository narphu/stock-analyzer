variable "bucket_name" {
  description = "Name of the S3 bucket to host the frontend"
  type        = string
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN for CloudFront"
  type        = string
}


variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}
