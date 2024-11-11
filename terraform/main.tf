# Provider configuration
provider "aws" {
  region = var.aws_region
}

# --------------------------------- VPC and subnets ----------------------------------
resource "aws_vpc" "main" {
  cidr_block           = "${var.vpc_ip_prefix}.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.vpc_prefix}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.vpc_prefix}-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = count.index == 0 ? "${var.vpc_ip_prefix}.1.0/24" : "${var.vpc_ip_prefix}.2.0/24"
  availability_zone       = count.index == 0 ? "us-east-1a" : "us-east-1b"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.vpc_prefix}-public-subnet-${count.index + 1}"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = count.index == 0 ? "${var.vpc_ip_prefix}.3.0/24" : "${var.vpc_ip_prefix}.4.0/24"
  availability_zone = count.index == 0 ? "us-east-1a" : "us-east-1b"

  tags = {
    Name = "${var.vpc_prefix}-private-subnet-${count.index + 1}"
  }
}

# EIP for NAT Gateway
resource "aws_eip" "nat" {
  domain = "vpc"

  depends_on = [aws_internet_gateway.main]
}

# NAT Gateway
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  depends_on = [aws_internet_gateway.main]

  tags = {
    Name = "${var.vpc_prefix}-nat-gateway"
  }
}

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.vpc_prefix}-public-rt"
  }
}

# Private Route Table
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main.id
  }
  depends_on = [aws_nat_gateway.main]

  tags = {
    Name = "${var.vpc_prefix}-private-rt"
  }
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count          = 2
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# --------------------------------- RDS DB ---------------------------------
resource "aws_security_group" "rds" {
  name        = "${var.vpc_prefix}-rds-sg"
  description = "RDS Security Group"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.vpc_prefix}-rds-sg"
  }
  depends_on = [aws_security_group.ecs_tasks]
}

# RDS Subnet Group
resource "aws_db_subnet_group" "rds" {
  name       = "${var.vpc_prefix}-rds-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${var.vpc_prefix}-rds-subnet-group"
  }
}

# RDS Instance
resource "aws_db_instance" "mysql" {
  identifier        = var.db_identifier
  engine            = "mysql"
  engine_version    = "8.0"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  storage_type      = "gp2"

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  publicly_accessible = false
  skip_final_snapshot = true
  multi_az            = false
  deletion_protection = false
  tags = {
    Name = "${var.vpc_prefix}-rds"
  }
}

# --------------------------------- ECS Cluster ---------------------------------
resource "aws_ecs_cluster" "main" {
  name = var.cluster_name
}

# ECS Task SG
resource "aws_security_group" "ecs_tasks" {
  name        = "${var.vpc_prefix}-tasks-sg"
  description = "Allow inbound traffic for ECS"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "Allow inbound traffic on container port"
    from_port   = var.app_port_to_open_traffic
    to_port     = var.app_port_to_open_traffic
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }


  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.vpc_prefix}-ecs-sg"
  }
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "ecs_logs" {
  name              = "/ecs/${var.task_family}"
  retention_in_days = 1
  tags = {
    Name = "/ecs/${var.task_family}"
  }
}

# Login to docker hub, if not authenticated the pull rate limit is 100 pulls per 6 hours
resource "aws_secretsmanager_secret" "docker_hub" {
  name                    = "docker-hub-credentials"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "docker_hub" {
  secret_id = aws_secretsmanager_secret.docker_hub.id
  secret_string = jsonencode({
    username = var.dockerhub_username,
    password = var.dockerhub_password
  })
}
# ECS Task Definition with environment variables
resource "aws_ecs_task_definition" "app" {
  family                   = var.task_family
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = var.role_for_tasks
  task_role_arn            = var.role_for_tasks

  container_definitions = jsonencode([
    # Init container for database setup
    {
      name      = "${var.container_name}-db-init"
      image     = "mysql:8.0"
      essential = false

      command = [
        "sh",
        "-c",
        <<EOF
        until mysql -h${aws_db_instance.mysql.address} -u${var.db_username} -p${var.db_password} ${var.db_name} -e 'SELECT 1'; do 
          echo waiting for database; 
          sleep 5; 
        done;
        echo '${file("${path.module}/init.sql")}' | mysql -h${aws_db_instance.mysql.address} -u${var.db_username} -p${var.db_password} ${var.db_name}
      EOF
      ]

      environment = [
        {
          name  = "MYSQL_PWD"
          value = var.db_password
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.task_family}"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "init"
        }
      }
    },
    # Main application container
    {
      name      = var.container_name
      image     = var.docker_image
      essential = true

      dependsOn = [
        {
          containerName = "${var.container_name}-db-init"
          condition     = "SUCCESS"
        }
      ]

      portMappings = [
        {
          containerPort = var.container_port
          hostPort      = var.container_port
          protocol      = "tcp"
        }
      ]
      memory            = 512
      memoryReservation = 256
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:${var.container_port}/ || exit 1"]
        interval    = 60
        timeout     = 5
        retries     = 2
        startPeriod = 60
      }
      environment = [
        {
          name  = "FLASK_SECRET_KEY"
          value = var.flask_secret_key
        },
        {
          name  = "AWS_REGION"
          value = var.aws_region
        },
        {
          name  = "ENV"
          value = var.environment
        },
        {
          name  = "API_URL"
          value = "https://${aws_lb.app.dns_name}"
        },
        {
          name  = "PORT"
          value = tostring(var.container_port)
        },
        {
          name  = "COGNITO_DOMAIN"
          value = var.cognito_domain
        },
        {
          name  = "COGNITO_USER_POOL_CLIENT_ID"
          value = aws_cognito_user_pool_client.app_client.id
        },
        {
          name  = "COGNITO_USER_POOL_CLIENT_SECRET"
          value = aws_cognito_user_pool_client.app_client.client_secret
        },
        {
          name  = "DB_HOST"
          value = aws_db_instance.mysql.address
        },
        {
          name  = "DB_PORT"
          value = tostring(var.db_port)
        },
        {
          name  = "DB_NAME"
          value = var.db_name
        },
        {
          name  = "DB_USER"
          value = var.db_username
        },
        {
          name  = "DB_PASSWD"
          value = var.db_password
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/${var.task_family}"
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }
      repositoryCredentials = {
        credentialsParameter = aws_secretsmanager_secret.docker_hub.arn
      }
    }
  ])

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [aws_db_instance.mysql]
}

# --------------------------------- ALB Load Balancer ---------------------------------
resource "aws_lb_target_group" "app" {
  name        = "${var.vpc_prefix}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 30
    interval            = 60
    path                = "/"
    port                = var.container_port
  }

  tags = {
    Name = "${var.vpc_prefix}-target-group"
  }
}

# Application Load Balancer
resource "aws_lb" "app" {
  name               = "${var.vpc_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  tags = {
    Name = "${var.vpc_prefix}-alb"
  }
  lifecycle {
    create_before_destroy = true
  }
}

# ALB Security Group
resource "aws_security_group" "alb" {
  name        = "${var.vpc_prefix}-alb-sg"
  description = "ALB Security Group"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.vpc_prefix}-alb-sg"
  }
}

# --------------------------------- ECS Service ---------------------------------
resource "aws_ecs_service" "app" {
  name                 = "${var.vpc_prefix}-app-service"
  cluster              = aws_ecs_cluster.main.id
  task_definition      = aws_ecs_task_definition.app.arn
  desired_count        = 1
  launch_type          = "FARGATE"
  force_new_deployment = true

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = var.container_name
    container_port   = var.container_port
  }
  lifecycle {
    create_before_destroy = true
    ignore_changes        = [desired_count]
  }
  depends_on = [
    aws_lb_listener.http,
    aws_ecs_task_definition.app,
    aws_lb_target_group.app
  ]
}

# --------------------------------- Cognito Client / ELB Callback Binding ---------------------------------
data "aws_cognito_user_pools" "existing" {
  name = var.cognito_user_pool_name
}

resource "aws_cognito_user_pool_client" "app_client" {
  name            = var.cognito_user_pool_client_name
  user_pool_id    = data.aws_cognito_user_pools.existing.ids[0]
  generate_secret = true
  callback_urls = concat(var.callback_urls, [
    "https://${aws_lb.app.dns_name}/auth/callback"
  ])

  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = var.oauth_scopes
  supported_identity_providers         = ["COGNITO"]

  explicit_auth_flows = [
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]

  refresh_token_validity = 30
  access_token_validity  = 60
  id_token_validity      = 60

  token_validity_units {
    refresh_token = "days"
    access_token  = "minutes"
    id_token      = "minutes"
  }

  prevent_user_existence_errors = "ENABLED"
  enable_token_revocation       = true
}
# --------------------------------- ALB HTTPS/Certificate ---------------------------------

# Generate private key
resource "tls_private_key" "private_key" {
  algorithm = "RSA"
  rsa_bits  = 2048
}

# Generate self-signed certificate
resource "tls_self_signed_cert" "certificate" {
  private_key_pem = tls_private_key.private_key.private_key_pem

  subject {
    common_name  = aws_lb.app.dns_name
    organization = "TopTable"
    country      = "PT"
    locality     = "Aveiro"
    province     = "Aveiro"
  }

  validity_period_hours = 2160 # 90 days
  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
  ]
}

# Import certificate to ACM
resource "aws_acm_certificate" "cert" {
  private_key      = tls_private_key.private_key.private_key_pem
  certificate_body = tls_self_signed_cert.certificate.cert_pem

  lifecycle {
    create_before_destroy = true
  }
}

# HTTPS Listener
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.app.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-2016-08"
  certificate_arn   = aws_acm_certificate.cert.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }

  depends_on = [aws_lb_target_group.app]
}

# HTTP Listener with redirect to HTTPS
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }

  depends_on = [aws_lb_target_group.app]
}

# --------------------------------- Outputs ---------------------------------
output "alb_dns_name" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.app.dns_name
}

output "target_group_arn" {
  description = "The ARN of the Target Group"
  value       = aws_lb_target_group.app.arn
}

output "rds_endpoint" {
  value     = aws_db_instance.mysql.endpoint
  sensitive = false
}

output "rds_database_name" {
  value     = aws_db_instance.mysql.db_name
  sensitive = false
}

output "rds_username" {
  value     = aws_db_instance.mysql.username
  sensitive = true
}

locals {
  common_tags = {
    Environment = var.environment
    Project     = var.vpc_prefix
    ManagedBy   = "Terraform"
  }
}

