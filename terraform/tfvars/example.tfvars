stage = "sndbx"
log_retention_days = 14
permissions_boundary_arn ="arn:aws:iam::06xxxxxxxxx:policy/XXXXXRoleBoundary"
launchpad_pfx_password_secret_id="prefix-message-template-launchpad-passphrase0000000000000"
launchpad_pfx_passcode_secret_arn = "arn:aws:secretsmanager:us-west-2:06xxxxxxxxx:secret:prefix-message-template-launchpad-passphrase0000000000000-SolCpg"
# The bucket where launchpad.pfx is stored. Ex. my-sndbx-bucket
launchpad_pfx_file_s3_bucket="my-bucket-internal"
# The key to point to launchpad.pfx Ex. /folder1/folder2/launchpad.pfx
launchpad_pfx_file_s3_key="my-prefix/crypto/launchpad.pfx"