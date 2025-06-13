resource "aws_acm_certificate" "cert" {
  domain_name       = "stock-analyzer.shrubb.ai"
  validation_method = "DNS"
  provider = aws.us_east_1

  tags = {
    Name = "stock-analyzer-cert"
  }
}