# CloudEco: Marine Plastic Detection System
# Author: Devesh Gurusinghe
# Purpose: Terraform variable definitions for customizable infrastructure parameters
# Date: 2026-04-30

# ============================================
# CORE
# ============================================
// Which GCP project bills and owns the resources; must match the service account key you use locally.
variable "project_id" {
  type        = string
  description = "GCP project ID for FIT5225 CloudEco resources."
  default     = "YOUR_GCP_PROJECT_ID"
}

// Regional home for subnet and static IPs; VMs still need an explicit zone (below).
variable "region" {
  type        = string
  description = "Primary GCP region for deployment."
  default     = "australia-southeast1"
}

// All three nodes are colocated in one zone (assignment: australia-southeast1-b) to minimize latency for etcd/API.
variable "zone" {
  type        = string
  description = "Primary GCP zone for VM instances."
  default     = "australia-southeast1-b"
}

# ============================================
# COMPUTE
# ============================================
// e2-custom-4-8192 = exactly 4 vCPU and 8 GiB RAM per assignment (not e2-standard-4 which is 16 GiB).
variable "machine_type" {
  type        = string
  description = "Machine type for Kubernetes master and worker VMs."
  default     = "e2-custom-4-8192"
}

// Ubuntu LTS image stream from Google’s ubuntu-os-cloud project; instances.tf resolves to a concrete image.
variable "image_family" {
  type        = string
  description = "Boot disk image family used for VM instances."
  default     = "ubuntu-2204-lts"
}

// Fixed topology: one apiserver node + two kubelets for the assignment rubric.
variable "vm_count" {
  type        = number
  description = "Total number of VMs (1 master + 2 workers)."
  default     = 3
}

// Order matters: index 0 must be master for outputs and human runbooks.
variable "vm_names" {
  type        = list(string)
  description = "Ordered VM names for Kubernetes cluster nodes."
  default     = ["k8s-master", "k8s-worker-1", "k8s-worker-2"]
}

# ============================================
# NETWORKING
# ============================================
// Logical name for the custom VPC; appears in GCP console and firewall rule prefixes.
variable "network_name" {
  type        = string
  description = "VPC network name for CloudEco infrastructure."
  default     = "cloudeco-vpc"
}

// /24 gives plenty of host addresses for nodes while staying inside RFC1918 private space.
variable "subnet_cidr" {
  type        = string
  description = "Subnet CIDR block for VM networking."
  default     = "10.0.1.0/24"
}

// Propagated to instance labels for cost tracking or future filtering (prod vs dev).
variable "environment" {
  type        = string
  description = "Deployment environment label."
  default     = "production"
}
