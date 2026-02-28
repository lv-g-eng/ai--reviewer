# VPC Module

This module creates a highly available VPC with public and private subnets across multiple availability zones.

## Features

- **Multi-AZ Architecture**: Deploys across 2 availability zones for high availability
- **Public Subnets**: For load balancers and bastion hosts with internet access
- **Private Subnets**: For application servers and databases with NAT gateway access
- **Internet Gateway**: Provides internet access for public subnets
- **NAT Gateways**: One per AZ for high availability, provides internet access for private subnets
- **VPC Flow Logs**: Optional network traffic logging for security and monitoring
- **Proper Routing**: Separate route tables for public and private subnets

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                          VPC (10.0.0.0/16)                  │
│                                                             │
│  ┌──────────────────────┐    ┌──────────────────────┐     │
│  │   Availability Zone 1 │    │   Availability Zone 2 │     │
│  │                       │    │                       │     │
│  │  ┌─────────────────┐ │    │  ┌─────────────────┐ │     │
│  │  │ Public Subnet   │ │    │  │ Public Subnet   │ │     │
│  │  │ 10.0.0.0/20     │ │    │  │ 10.0.1.0/20     │ │     │
│  │  │                 │ │    │  │                 │ │     │
│  │  │  ┌───────────┐  │ │    │  │  ┌───────────┐  │ │     │
│  │  │  │ NAT GW 1  │  │ │    │  │  │ NAT GW 2  │  │ │     │
│  │  │  └───────────┘  │ │    │  │  └───────────┘  │ │     │
│  │  └─────────────────┘ │    │  └─────────────────┘ │     │
│  │           │           │    │           │           │     │
│  │  ┌─────────────────┐ │    │  ┌─────────────────┐ │     │
│  │  │ Private Subnet  │ │    │  │ Private Subnet  │ │     │
│  │  │ 10.0.2.0/20     │ │    │  │ 10.0.3.0/20     │ │     │
│  │  │                 │ │    │  │                 │ │     │
│  │  │  App Servers    │ │    │  │  App Servers    │ │     │
│  │  │  Databases      │ │    │  │  Databases      │ │     │
│  │  └─────────────────┘ │    │  └─────────────────┘ │     │
│  └──────────────────────┘    └──────────────────────┘     │
│                                                             │
│                    ┌──────────────────┐                    │
│                    │ Internet Gateway │                    │
│                    └──────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
                              │
                         Internet
```

## Usage

```hcl
module "vpc" {
  source = "./modules/vpc"

  project_name       = "ai-code-reviewer"
  environment        = "staging"
  vpc_cidr           = "10.0.0.0/16"
  availability_zones = ["us-east-1a", "us-east-1b"]
  enable_flow_logs   = true

  tags = {
    Team = "DevOps"
    Cost = "Infrastructure"
  }
}
```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| project_name | Name of the project for resource naming | string | - | yes |
| environment | Environment name (dev, staging, prod) | string | - | yes |
| vpc_cidr | CIDR block for VPC | string | "10.0.0.0/16" | no |
| availability_zones | List of availability zones (minimum 2) | list(string) | - | yes |
| enable_flow_logs | Enable VPC Flow Logs | bool | true | no |
| tags | Additional tags to apply | map(string) | {} | no |

## Outputs

| Name | Description |
|------|-------------|
| vpc_id | ID of the VPC |
| vpc_cidr | CIDR block of the VPC |
| public_subnet_ids | List of public subnet IDs |
| private_subnet_ids | List of private subnet IDs |
| internet_gateway_id | ID of the Internet Gateway |
| nat_gateway_ids | List of NAT Gateway IDs |
| nat_gateway_public_ips | List of NAT Gateway public IPs |

## Subnet CIDR Allocation

The module automatically calculates subnet CIDRs from the VPC CIDR:
- Public subnets: First N /20 blocks (where N = number of AZs)
- Private subnets: Next N /20 blocks

For a /16 VPC CIDR (e.g., 10.0.0.0/16) with 2 AZs:
- Public Subnet 1: 10.0.0.0/20 (4,096 IPs)
- Public Subnet 2: 10.0.16.0/20 (4,096 IPs)
- Private Subnet 1: 10.0.32.0/20 (4,096 IPs)
- Private Subnet 2: 10.0.48.0/20 (4,096 IPs)

## High Availability

- **Multi-AZ Deployment**: Resources distributed across 2+ availability zones
- **Redundant NAT Gateways**: One NAT Gateway per AZ prevents single point of failure
- **Independent Route Tables**: Each private subnet has its own route table pointing to its AZ's NAT Gateway

## Security

- **Network Isolation**: Private subnets have no direct internet access
- **VPC Flow Logs**: Optional traffic logging for security monitoring and compliance
- **Least Privilege Routing**: Only necessary routes configured

## Cost Optimization

- NAT Gateways are the primary cost driver (~$0.045/hour per gateway + data transfer)
- For development environments, consider using a single NAT Gateway
- VPC Flow Logs incur CloudWatch Logs storage costs

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.0 |
| aws | >= 4.0 |

## Compliance

This module implements:
- **Requirement 4.5**: VPC with public and private subnets across 2 availability zones
- High availability through multi-AZ architecture
- Network segmentation for security
