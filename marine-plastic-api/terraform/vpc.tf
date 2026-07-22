# CloudEco: Marine Plastic Detection System
# Author: Devesh Gurusinghe ()
# Purpose: VPC network and subnet configuration for Kubernetes cluster
# Date: 2026-04-30

# ============================================
# VPC
# ============================================
// Creates an isolated network for the K8s VMs; auto_create_subnetworks=false so we define one explicit subnet (assignment requirement).
resource "google_compute_network" "cloudeco_vpc" {
  name                    = var.network_name
  auto_create_subnetworks = false
}

# ============================================
# SUBNET
# ============================================
// One regional subnet in Sydney region; all three nodes get IPs from this CIDR for east-west cluster traffic.
resource "google_compute_subnetwork" "cloudeco_subnet" {
  name          = "${var.network_name}-subnet"
  network       = google_compute_network.cloudeco_vpc.id
  ip_cidr_range = var.subnet_cidr
  region        = var.region
}
