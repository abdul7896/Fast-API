# Description to identify the purpose of the KMS key
variable "description" {
  description = "KMS key description"
  type        = string
}

# Alias name for the KMS key (without the "alias/" prefix)
variable "alias" {
  description = "KMS key alias"
  type        = string
}
