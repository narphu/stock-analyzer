output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnets" {
  value = aws_subnet.public[*].id
}

output "backend_tg_arn" {
  value = aws_lb_target_group.backend.arn
}

output "alb_listener_arn" {
  value = aws_lb_listener.https_backend.arn
}

# Output these ARNs for use in other modules
output "frontend_cert_arn" {
  value = aws_acm_certificate.frontend_cert.arn
}

output "backend_cert_arn" {
  value = aws_acm_certificate.backend_cert.arn
}
