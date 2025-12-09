// State backend configuration for the dev environment.
// For this PoC we use a local backend (terraform.tfstate in this folder).
// In a real setup, you would typically move this to S3 + DynamoDB.

terraform {
  backend "local" {
    path = "terraform.tfstate"
  }
}
