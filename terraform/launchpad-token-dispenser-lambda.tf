data "aws_region" "current" {}

resource "aws_lambda_function" "launchpad_token_dispenser_lambda" {
  filename          = "../dist/token-dispenser_lambda.zip"
  function_name     = "${var.stage}-launchpad_token_dispenser"
  role              = aws_iam_role.launchpad_token_dispenser_lambda_role.arn
  handler           = "token_dispenser.token_dispenser_lambda.handler"
  tags              = local.default_tags
  source_code_hash  = filebase64sha256("../dist/token-dispenser_lambda.zip")
  architectures     = var.launchpad_token_dispenser_lambda_architectures
  runtime           = "python3.12"
  timeout           = var.launchpad_token_dispenser_lambda_timeout
  memory_size       = var.launchpad_token_dispenser_lambda_memory_size

  depends_on = [aws_cloudwatch_log_group.launchpad_token_dispenser_lambda_log_group]

  environment {
    variables = {
      REGION                           = data.aws_region.current.name
      LAUNCHPAD_GETTOKEN_URL           = var.launchpad_gettoken_url
      # If CLIENT has not renew/request token for this amount of time, it's DynamoDB entry will be deleted
      CLIENT_EXPIRATION_TIME           = var.client_expiration_seconds
      # The secret-id point to the Launchpad pfx password
      LAUNCHPAD_PFX_PASSWORD_SECRET_ID = var.launchpad_pfx_password_secret_id
      # The bucket will launchpad.pfx is stored. Ex. my-sndbx-bucket
      LAUNCHPAD_PFX_FILE_S3_BUCKET="dyen-cumulus-internal"
      # The key to point to launchpad.pfx Ex. /folder1/folder2/launchpad.pfx
      LAUNCHPAD_PFX_FILE_S3_KEY="/dyen-cumulus/crypto/launchpad.pfx"
      # DynamoDB cache table name
      DYNAMO_DB_CACHE_TABLE_NAME       = "${aws_dynamodb_table.launchpad_token_dispenser_cache_table.name}"
    }
  }
}

resource "aws_cloudwatch_log_group" "launchpad_token_dispenser_lambda_log_group" {
  name              = "/aws/lambda/${var.stage}-launchpad_token_dispenser"
  retention_in_days = var.log_retention_days
}




