terraform {
  backend "s3" {}
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.32"
    }
  }
  required_version = "~> 1.10.4"
}

provider "aws" {
  region                    = var.region
  shared_credentials_files  = [var.credentials]
  profile                   = var.profile

  ignore_tags {
    key_prefixes = ["gsfc-ngap"]
  }
}

locals {
  prefix = var.stage

  default_tags = length(var.default_tags) == 0 ? {
    team        = "IandA",
    application = local.prefix,
    environment = var.stage
  } : var.default_tags
}

data "aws_caller_identity" "current" {}