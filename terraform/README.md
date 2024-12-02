# How to use terraform when using aws sandbox environment

Note: if you are running terraform multiple times between sessions (or if you refresh the session), you may not need to repeat this (except updating docker tags)

## Preparation (needs to be done only the first time)

1. In the "cognito_domain" field in terraform.tfvars, ensure that it is "pool-domain-iky.auth.us-east-1.amazoncognito.com" (pool-domain-iky was the domain name ilker chose for setup)

## Running terraform

1. Update ~/.aws/credentials (or wherever you store your credentials) to the current session's credentials (I assume you know how to get credentials)
2. Update the role for tasks in tfvars to use the current account id (changes each time)
3. Update docker tags (if needed)
4. Add yourself to trusted entities:
   1. Go to AWS console
   2. Go to IAM
   3. Click Roles, then LabRole
   4. Open the "Trust Relationship" tab
   5. Click "Edit trust policy"
   6. Inside the "Service" array add:
      1. "ecs-tasks.amazonaws.com",
      2. "ecs.amazonaws.com"
   7. After the "Service" array, add:
      1. "AWS": "arn:aws:sts::[account_id]:assumed-role/[Federated user]" (you can find federated user below accountId on the top-right corner)
   8. Ensure there aren't any syntax errors and apply changes
5. Add necessary permissions (Note: this is how I do it, there might be multiple correct ways):
   1. Still on the "LabRole" page, click the "Permissions" tab
   2. Click "Add permissions" and "Attach Policies"
   3. Check the following Permissions (there may be other valid permissions, but I use these):
      1. AmazonCognitoPowerUser
      2. AmazonECS_FullAccess
      3. AmazonSQSFullAccess
      4. SecretsManagerReadWrite
      5. AWSCertificateManagerFullAccess
   4. Click "add permissions"
6. Run "terraform plan" (just to make sure)
7. Run "terraform apply"
