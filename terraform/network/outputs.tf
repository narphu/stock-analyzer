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
  value = aws_lb_listener.https.arn
}

output "frontend_acm_cert_arn" {
  value = aws_acm_certificate.cert.arn
}
