resource "aws_acm_certificate" "frontend_cert" {
  domain_name       = "stock-analyzer.shrubb.ai"
  validation_method = "DNS"
  tags = {
    Name = "stock-analyzer-frontend-cert"
  }
}
resource "aws_acm_certificate" "backend_cert" {
  domain_name       = "api.stock-analyzer.shrubb.ai"
  validation_method = "DNS"
  tags = {
    Name = "stock-analyzer-backend-cert"
  }
}