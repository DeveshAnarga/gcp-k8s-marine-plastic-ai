# CloudEco: Marine Plastic Detection System
# Author: Devesh Gurusinghe
# Purpose: Terraform variable values for the GCP project
#
# Override defaults in variables.tf for a concrete deploy.
# Keep service-account keys out of the repo; use your own project/key locally.

project_id   = "YOUR_GCP_PROJECT_ID"
region       = "australia-southeast1"
zone         = "australia-southeast1-b"
machine_type = "e2-custom-4-8192"
image_family = "ubuntu-2204-lts"
vm_count     = 3
vm_names     = ["k8s-master", "k8s-worker-1", "k8s-worker-2"]
network_name = "cloudeco-vpc"
subnet_cidr  = "10.0.1.0/24"
environment  = "production"
