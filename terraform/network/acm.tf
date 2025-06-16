resource "aws_acm_certificate" "cert" {
  domain_name       = "stock-analyzer.shrubb.ai"
  validation_method = "DNS"
  tags = {
    Name = "stock-analyzer-cert"
  }
}