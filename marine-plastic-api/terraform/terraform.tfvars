# CloudEco: Marine Plastic Detection System
# Author: Devesh Gurusinghe ()
# Purpose: Terraform variable values for student's GCP project
# Date: 2026-04-30
#
# This file overrides defaults in variables.tf for a concrete deploy. Keep terraform-key.json
# out of submission; markers run terraform with their own project/key.

project_id   = "fit5225-marine-a1-"
region       = "australia-southeast1"
zone         = "australia-southeast1-b"
machine_type = "e2-custom-4-8192"
image_family = "ubuntu-2204-lts"
vm_count     = 3
vm_names     = ["k8s-master", "k8s-worker-1", "k8s-worker-2"]
network_name = "cloudeco-vpc"
subnet_cidr  = "10.0.1.0/24"
environment  = "production"
