variable "default_tags" {
  type = map(string)
  default = {}
}


##################################################################
# The arn of response sns where CNMResponse lambda shall publish
# messages into
##################################################################

variable "permissions_boundary_arn" {}

variable "credentials" {
  default = "~/.aws/credentials"
}

variable "region" {
  default = "us-west-2"
}

# AWS profile name
variable "profile" {
  type = string
}

# sndbx, sit, uat or ops
variable "stage" {
  default = "sndbx"
}

variable "log_retention_days" {
  type    = number
  default = 14
}

variable "launchpad_gettoken_url" {
  type    = string
  default = "https://api.launchpad.nasa.gov/icam/api/sm/v1/gettoken"
}

# The bucket where launchpad.pfx is stored. Ex. my-sndbx-bucket
variable "launchpad_pfx_file_s3_bucket"{}
# The key to point to launchpad.pfx Ex. /folder1/folder2/launchpad.pfx
variable "launchpad_pfx_file_s3_key" {}

# The secret-id to retrieve PFX file password
variable "launchpad_pfx_password_secret_id" {
  type = string
}
# The ARN of the secret storing pfx passcode
variable "launchpad_pfx_passcode_secret_arn" {}

# Launchpad Token Dispensing Lambada timeout in secs
variable "launchpad_token_dispenser_lambda_timeout" {
  type    = number
  default = 20
}

variable "launchpad_token_dispenser_lambda_memory_size" {
  type    = number
  default = 128
}

variable "launchpad_token_dispenser_lambda_architectures" {
  description = "set architecture for the Lambda function. Valid values are x86_64 and arm64. Default is x86_64"
  type = list(string)
  default = ["x86_64"]
}

# DynamoDB configuration
# the requester for token dispenser lambda will provide a client_id as input.  By using the client_id,
# token is cached in dynamoDB.  This value indicates
# how long the client_id entry will be kept before deletion, in unix EPOCH format. default = 3 days
variable "client_expiration_seconds" {
  type    = number
  default = 259200
}
