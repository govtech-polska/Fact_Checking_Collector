provider "aws" {
  region = "eu-central-1"
}
terraform {
  backend "s3" {
  }
}

data "aws_route53_zone" "selected" {
  name = var.domain
}

data "terraform_remote_state" "infra" {
  backend = "s3"

  config = {
    bucket = var.bucket
    key    = var.infra_statefile_key
    region = var.region
  }
}

resource "aws_iam_user" "collector" {
  name = "sfnf-collector-${var.environment}-s3"
  path = "/system/"
}

resource "aws_iam_access_key" "collector" {
  user = aws_iam_user.collector.name
}

resource "aws_iam_user_policy" "collector" {
  name = "sfnf-collector-${var.environment}-s3-access"
  user = aws_iam_user.collector.name

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "s3:*"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
EOF
}


module "s3_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "sfnf-collector-${var.environment}"
  acl    = "public-read"

  cors_rule = [
    {
      allowed_headers = ["*"]
      allowed_methods = ["GET", "HEAD"]
      allowed_origins = ["*"]
      expose_headers  = ["ETag"]
      max_age_seconds = 3000
    }
  ]

  versioning = {
    enabled = false
  }

}

module "service" {
  source                       = "git@github.com:dook/sfnf-infra.git//modules/terraform-aws-fargate"
  name_preffix                 = "${var.environment}-sfnf-collector"
  region                       = "eu-central-1"
  vpc_id                       = var.vpc_id
  availability_zones           = [var.azs]
  public_subnets_ids           = var.public_subnets
  private_subnets_ids          = var.private_subnets
  access_cidr_list             = ["0.0.0.0/0"]
  port_lb_external             = "443"
  container_name               = "sfnf-collector-${var.environment}"
  container_image              = "${var.ecr_registry}:${var.image_tag}"
  container_cpu                = 256
  container_memory             = 1024
  container_memory_reservation = 1024
  container_port               = 8000

  internal        = false
  certificate_arn = var.certificate_arn
  create_elb      = false
  elb_sg_id       = data.terraform_remote_state.infra.outputs.elb_sg_id


  environment = [
    {
      name  = "DB_READER_HOST"
      value = var.postgres_host
    },
    {
      name  = "DB_WRITER_HOST"
      value = var.postgres_host
    },
    {
      name  = "COLLECTOR_PORT"
      value = "8000"
    },
    {
      name  = "COLLECTOR_HOST"
      value = "0.0.0.0"
    },
    {
      name  = "IMAGE_BUCKET"
      value = "sfnf-collector-${var.environment}"
    },
    {
      name  = "AWS_ACCESS_KEY_ID"
      value = aws_iam_access_key.collector.id
    },
    {
      name  = "AWS_SECRET_ACCESS_KEY"
      value = aws_iam_access_key.collector.secret
    },
    {
      name  = "DB_PORT"
      value = "5432"
    },
    {
      name  = "DB_NAME"
      value = "fh${var.environment}"
    },
    {
      name  = "DB_USER"
      value = var.postgres_username
    },
    {
      name  = "DB_PASSWORD"
      value = var.postgres_password
    },
    {
      name  = "DB_DRIVER"
      value = "postgres"
    },
    {
      name  = "COLLECTOR_LOG_LEVEL"
      value = var.log_level
    },
    {
      name  = "RECAPTCHA_THRESHOLD"
      value = 0.8
    },
    {
      name  = "RECAPTCHA_SECRET"
      value = var.recaptcha_secret
    }
  ]
}

resource aws_lb_listener_rule service {
  listener_arn = data.terraform_remote_state.infra.outputs.elb_https_listener_arn

  action {
    type             = "forward"
    target_group_arn = module.service.lb_target_group_arn
  }

  condition {
    host_header {
      values = [var.fqdn]
    }
  }
}

resource "aws_route53_record" "alb_public_web_endpoint" {
  zone_id = data.aws_route53_zone.selected.zone_id
  name    = var.fqdn
  type    = "A"

  alias {
    name                   = data.terraform_remote_state.infra.outputs.elb_dns_name
    zone_id                = data.terraform_remote_state.infra.outputs.elb_zone_id
    evaluate_target_health = true
  }
}
