# CloudEco: Marine Plastic Detection System
# Author: Devesh Gurusinghe
# Purpose: Terraform GCP provider configuration for infrastructure
# Date: 2026-04-30

# ============================================
# TERRAFORM & PROVIDER
# ============================================
// Locks Terraform CLI version and pins the Google provider so plans/applies stay reproducible.
terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

// Tells Terraform which GCP project/region to talk to; service account JSON must live next to terraform/ .
provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = file("../terraform-key.json")
}
