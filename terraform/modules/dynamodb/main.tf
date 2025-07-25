# Creates a DynamoDB table for storing user records with email as the primary key
resource "aws_dynamodb_table" "users_table" {
  name         = var.table_name           # Table name provided via variable
  billing_mode = "PAY_PER_REQUEST"        # On-demand billing, no need to manage capacity
  hash_key     = "email"                  # Partition key is the user's email

  # Define primary key attribute (email)
  attribute {
    name = "email"
    type = "S"                            # "S" stands for string type
  }

  # Define secondary attribute for indexing (name)
  attribute {
    name = "name"
    type = "S"
  }

  # Create a Global Secondary Index (GSI) to query users by name
  global_secondary_index {
    name            = "NameIndex"         # Index name
    hash_key        = "name"              # Use 'name' as the index key
    projection_type = "ALL"               # Include all attributes in index queries
  }

  # Enable encryption at rest using a customer-managed KMS key
  server_side_encryption {
    enabled     = true
    kms_key_arn = var.kms_key_arn         # KMS key ARN provided via variable
  }
}
