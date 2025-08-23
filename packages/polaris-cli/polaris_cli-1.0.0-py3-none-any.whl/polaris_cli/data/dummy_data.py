"""
Dummy data for simulating API responses
"""

import random
from datetime import datetime, timedelta
from typing import Any, Dict, List

# Sample API tokens
SAMPLE_TOKENS = {
    "production": "pk_prod_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
    "staging": "pk_stg_z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g0",
    "development": "pk_dev_f6e5d4c3b2a1z0y9x8w7v6u5t4s3r2q1p0o9n8m7",
    "testing": "pk_test_9i8h7g6f5e4d3c2b1a0z9y8x7w6v5u4t3s2r1q0p"
}


def get_sample_resources() -> List[Dict[str, Any]]:
    """Get sample resource data."""
    return [
        {
            "id": "comp_001",
            "name": "premium-gpu-node-001",
            "type": "Compute",
            "deployment_status": "inactive",  # available
            "price_per_hour": 3.45,
            "cpu_count": 32,
            "gpu_count": 1,
            "gpu_specs": {
                "model_name": "NVIDIA RTX A5000",
                "cuda_cores": 8192,
                "tensor_cores": 256,
                "clock_speed": "1695MHz",
                "memory": "24GB"
            },
            "cpu_specs": {
                "model_name": "AMD EPYC 7452 32-Core Processor",
                "cores": 32,
                "threads": 64,
                "clock_speed": "2.35GHz",
                "cache": "128MB"
            },
            "memory_gb": 256,
            "storage_gb": 2000,
            "last_monitoring_update": "2025-08-21T07:58:10.036675",
            "monitoring_status": {
                "validation_status": "verified"
            },
            "network_info": {
                "region": "Asia Pacific",
                "org": "AS13335 Cloudflare, Inc.",
                "country": "SG",
                "hostname": "premium-gpu-node-001.cloudflare.com",
                "postal": "018989",
                "city": "Singapore",
                "timezone": "Asia/Singapore",
                "loc": "1.2966,103.8558",
                "ip": "149.36.0.218"
            },
            "created_at": "2024-01-15T10:30:00Z",
        },
        {
            "id": "comp_002",
            "name": "high-performance-gpu-002",
            "type": "Compute", 
            "deployment_status": "active",  # in use
            "price_per_hour": 4.85,
            "cpu_count": 48,
            "gpu_count": 2,
            "gpu_specs": {
                "model_name": "NVIDIA RTX 4090",
                "cuda_cores": 16384,
                "tensor_cores": 512,
                "clock_speed": "2520MHz",
                "memory": "24GB"
            },
            "cpu_specs": {
                "model_name": "Intel Xeon Gold 6248R",
                "cores": 48,
                "threads": 96,
                "clock_speed": "3.0GHz",
                "cache": "35.75MB"
            },
            "memory_gb": 512,
            "storage_gb": 4000,
            "last_monitoring_update": "2025-08-21T07:45:22.124583",
            "monitoring_status": {
                "validation_status": "verified"
            },
            "network_info": {
                "region": "North America",
                "org": "AS15169 Google LLC",
                "country": "US",
                "hostname": "high-perf-gpu-002.google.com",
                "postal": "94043",
                "city": "Mountain View",
                "timezone": "America/Los_Angeles",
                "loc": "37.4056,-122.0775",
                "ip": "172.217.164.142"
            },
            "created_at": "2024-01-14T14:20:00Z",
        },
        {
            "id": "comp_003",
            "name": "ml-training-node-003",
            "type": "Compute",
            "deployment_status": "inactive",
            "price_per_hour": 5.25,
            "cpu_count": 64,
            "gpu_count": 1,
            "gpu_specs": {
                "model_name": "NVIDIA A100 80GB",
                "cuda_cores": 6912,
                "tensor_cores": 432,
                "clock_speed": "1410MHz",
                "memory": "80GB"
            },
            "cpu_specs": {
                "model_name": "AMD EPYC 7763 64-Core Processor",
                "cores": 64,
                "threads": 128,
                "clock_speed": "2.45GHz",
                "cache": "256MB"
            },
            "memory_gb": 1024,
            "storage_gb": 8000,
            "last_monitoring_update": "2025-08-21T08:12:45.987234",
            "monitoring_status": {
                "validation_status": "verified"
            },
            "network_info": {
                "region": "Europe",
                "org": "AS16509 Amazon.com, Inc.",
                "country": "IE",
                "hostname": "ml-training-003.amazonaws.com",
                "postal": "D02",
                "city": "Dublin",
                "timezone": "Europe/Dublin",
                "loc": "53.3331,-6.2489",
                "ip": "52.215.34.155"
            },
            "created_at": "2024-01-13T09:15:00Z",
        },
        {
            "id": "comp_004",
            "name": "enterprise-gpu-004",
            "type": "Compute",
            "deployment_status": "active",
            "price_per_hour": 7.95,
            "cpu_count": 56,
            "gpu_count": 4,
            "gpu_specs": {
                "model_name": "NVIDIA H100 SXM",
                "cuda_cores": 14592,
                "tensor_cores": 456,
                "clock_speed": "1980MHz",
                "memory": "80GB"
            },
            "cpu_specs": {
                "model_name": "Intel Xeon Platinum 8358",
                "cores": 56,
                "threads": 112,
                "clock_speed": "2.6GHz",
                "cache": "48MB"
            },
            "memory_gb": 2048,
            "storage_gb": 16000,
            "last_monitoring_update": "2025-08-21T08:05:33.456789",
            "monitoring_status": {
                "validation_status": "verified"
            },
            "network_info": {
                "region": "North America",
                "org": "AS8075 Microsoft Corporation",
                "country": "US",
                "hostname": "enterprise-gpu-004.azure.com",
                "postal": "98052",
                "city": "Redmond",
                "timezone": "America/Los_Angeles",
                "loc": "47.6740,-122.1215",
                "ip": "40.112.72.205"
            },
            "created_at": "2024-01-12T16:45:00Z",
        },
        {
            "id": "comp_005",
            "name": "inference-node-005",
            "type": "Compute",
            "deployment_status": "inactive",
            "price_per_hour": 2.15,
            "cpu_count": 24,
            "gpu_count": 1,
            "gpu_specs": {
                "model_name": "NVIDIA RTX A4000",
                "cuda_cores": 6144,
                "tensor_cores": 192,
                "clock_speed": "1560MHz",
                "memory": "16GB"
            },
            "cpu_specs": {
                "model_name": "Intel Core i9-12900K",
                "cores": 24,
                "threads": 32,
                "clock_speed": "3.2GHz",
                "cache": "30MB"
            },
            "memory_gb": 128,
            "storage_gb": 1000,
            "last_monitoring_update": "2025-08-21T07:52:18.223456",
            "monitoring_status": {
                "validation_status": "verified"
            },
            "network_info": {
                "region": "Asia Pacific",
                "org": "AS7922 Comcast Cable Communications",
                "country": "JP",
                "hostname": "inference-node-005.comcast.com",
                "postal": "105-0011",
                "city": "Tokyo",
                "timezone": "Asia/Tokyo",
                "loc": "35.6762,139.6503",
                "ip": "203.104.105.95"
            },
            "created_at": "2024-01-11T12:00:00Z",
        },
        {
            "id": "comp_008",
            "name": "amd-gpu-node-008",
            "type": "Compute",
            "deployment_status": "active",  # in use
            "price_per_hour": 3.95,
            "cpu_count": 32,
            "gpu_count": 1,
            "gpu_specs": {
                "model_name": "AMD Radeon Pro VII",
                "stream_processors": 3840,
                "tensor_cores": 0,
                "clock_speed": "1750MHz",
                "memory": "16GB"
            },
            "cpu_specs": {
                "model_name": "AMD EPYC 7542 32-Core Processor",
                "cores": 32,
                "threads": 64,
                "clock_speed": "2.9GHz",
                "cache": "128MB"
            },
            "memory_gb": 256,
            "storage_gb": 2000,
            "last_monitoring_update": "2025-08-21T06:45:22.445566",
            "monitoring_status": {
                "validation_status": "verified"
            },
            "network_info": {
                "region": "North America",
                "org": "AS3949 OVHcloud",
                "country": "CA",
                "hostname": "amd-gpu-008.ovhcloud.com",
                "postal": "H3B 4W5",
                "city": "Montreal",
                "timezone": "America/Toronto",
                "loc": "45.5017,-73.5673",
                "ip": "192.99.18.45"
            },
            "created_at": "2024-01-12T14:30:00Z",
        },
        {
            "id": "comp_009",
            "name": "amd-gaming-node-009",
            "type": "Compute",
            "deployment_status": "inactive",  # available
            "price_per_hour": 4.25,
            "cpu_count": 16,
            "gpu_count": 1,
            "gpu_specs": {
                "model_name": "AMD Radeon RX 7900 XTX",
                "stream_processors": 6144,
                "tensor_cores": 0,
                "clock_speed": "2500MHz",
                "memory": "24GB"
            },
            "cpu_specs": {
                "model_name": "AMD Ryzen 9 7950X",
                "cores": 16,
                "threads": 32,
                "clock_speed": "4.5GHz",
                "cache": "64MB"
            },
            "memory_gb": 128,
            "storage_gb": 1000,
            "last_monitoring_update": "2025-08-21T08:12:33.778899",
            "monitoring_status": {
                "validation_status": "verified"
            },
            "network_info": {
                "region": "Europe",
                "org": "AS16509 Amazon.com, Inc.",
                "country": "DE",
                "hostname": "amd-gaming-009.aws-eu.com",
                "postal": "10115",
                "city": "Berlin",
                "timezone": "Europe/Berlin",
                "loc": "52.5200,13.4050",
                "ip": "18.185.45.78"
            },
            "created_at": "2024-01-13T09:15:00Z",
        },
        {
            "id": "comp_006",
            "name": "cpu-workstation-006",
            "type": "Compute",
            "deployment_status": "inactive",
            "price_per_hour": 0.85,
            "cpu_count": 96,
            "gpu_count": 0,  # CPU-only resource
            "gpu_specs": {},  # No GPU
            "cpu_specs": {
                "model_name": "AMD EPYC 7763 64-Core Processor",
                "cores": 96,
                "threads": 192,
                "clock_speed": "2.45GHz",
                "cache": "256MB"
            },
            "memory_gb": 768,
            "storage_gb": 4000,
            "last_monitoring_update": "2025-08-21T08:20:15.654321",
            "monitoring_status": {
                "validation_status": "verified"
            },
            "network_info": {
                "region": "Europe",
                "org": "AS8075 Microsoft Corporation",
                "country": "NL",
                "hostname": "cpu-workstation-006.azure.com",
                "postal": "1012",
                "city": "Amsterdam",
                "timezone": "Europe/Amsterdam",
                "loc": "52.3676,4.9041",
                "ip": "40.115.48.193"
            },
            "created_at": "2024-01-10T11:30:00Z",
        },
        {
            "id": "comp_007",
            "name": "high-memory-cpu-007",
            "type": "Compute",
            "deployment_status": "active", 
            "price_per_hour": 1.25,
            "cpu_count": 128,
            "gpu_count": 0,  # CPU-only resource
            "gpu_specs": {},  # No GPU
            "cpu_specs": {
                "model_name": "Intel Xeon Platinum 8480+",
                "cores": 128,
                "threads": 256,
                "clock_speed": "2.0GHz",
                "cache": "105MB"
            },
            "memory_gb": 2048,
            "storage_gb": 8000,
            "last_monitoring_update": "2025-08-21T07:35:42.987654",
            "monitoring_status": {
                "validation_status": "verified"
            },
            "network_info": {
                "region": "North America",
                "org": "AS15169 Google LLC",
                "country": "CA",
                "hostname": "high-memory-007.google.com",
                "postal": "H3B",
                "city": "Montreal",
                "timezone": "America/Montreal",
                "loc": "45.5017,-73.5673",
                "ip": "35.203.25.122"
            },
            "created_at": "2024-01-09T13:15:00Z",
        }
    ]


def get_sample_instances() -> List[Dict[str, Any]]:
    """Get sample instance data."""
    base_time = datetime.now() - timedelta(hours=12)
    
    return [
        {
            "id": "inst_001",
            "name": "ml-training-job",
            "status": "running",
            "machine_type": "gpu-nvidia-a100-80gb",
            "region": "us-west-1",
            "price_per_hour": 2.45,
            "image": "pytorch/pytorch:2.1-cuda11.8-devel",
            "created_at": (base_time - timedelta(hours=8)).isoformat() + "Z",
            "ssh_key": "ssh_key_001",
            "disk_size": 500,
            "gpu_count": 1,
            "labels": ["ml", "pytorch", "training"],
        },
        {
            "id": "inst_002",
            "name": "inference-server",
            "status": "running", 
            "machine_type": "gpu-nvidia-rtx4090",
            "region": "us-east-1",
            "price_per_hour": 1.85,
            "image": "nvidia/triton:23.10-py3",
            "created_at": (base_time - timedelta(hours=3)).isoformat() + "Z",
            "ssh_key": "ssh_key_002",
            "disk_size": 200,
            "gpu_count": 2,
            "labels": ["inference", "triton", "production"],
        },
        {
            "id": "inst_003",
            "name": "data-processing",
            "status": "stopped",
            "machine_type": "cpu-amd-epyc-7763", 
            "region": "eu-west-1",
            "price_per_hour": 0.85,
            "image": "python:3.11-slim",
            "created_at": (base_time - timedelta(hours=24)).isoformat() + "Z",
            "ssh_key": "ssh_key_001",
            "disk_size": 100,
            "labels": ["data", "batch", "processing"],
        },
        {
            "id": "inst_004",
            "name": "dev-environment",
            "status": "pending",
            "machine_type": "gpu-nvidia-rtx4090",
            "region": "us-west-1",
            "price_per_hour": 1.85,
            "image": "ubuntu:22.04",
            "created_at": datetime.now().isoformat() + "Z",
            "ssh_key": "ssh_key_003",
            "disk_size": 250,
            "gpu_count": 1,
            "labels": ["development", "testing"],
        }
    ]


def get_sample_clusters() -> List[Dict[str, Any]]:
    """Get sample cluster data."""
    return [
        {
            "id": "cluster_001",
            "name": "ml-training-cluster",
            "status": "running",
            "node_count": 4,
            "machine_type": "gpu-nvidia-a100-80gb",
            "region": "us-west-1",
            "created_at": "2024-01-10T08:00:00Z",
            "auto_scale": True,
            "min_nodes": 2,
            "max_nodes": 10,
            "price_per_hour": 9.80,
        },
        {
            "id": "cluster_002",
            "name": "inference-cluster",
            "status": "scaling",
            "node_count": 8,
            "machine_type": "gpu-nvidia-rtx4090",
            "region": "us-east-1",
            "created_at": "2024-01-09T15:30:00Z",
            "auto_scale": True,
            "min_nodes": 4,
            "max_nodes": 20,
            "price_per_hour": 14.80,
        }
    ]


def get_sample_templates() -> List[Dict[str, Any]]:
    """Get sample template data."""
    return [
        {
            "id": "pytorch-training",
            "name": "PyTorch GPU Training",
            "category": "Machine Learning",
            "description": "Complete PyTorch environment optimized for deep learning training with CUDA 11.8, cuDNN, and popular ML libraries.",
            "image": "pytorch/pytorch:2.1-cuda11.8-devel",
            "docker_hub": "https://hub.docker.com/r/pytorch/pytorch",
            "requirements": {
                "gpu_required": True,
                "min_ram": "8GB",
                "min_storage": "25GB"
            },
            "compatibility": {
                "cpu": True,
                "gpu": True
            },
            "created_at": "2024-01-08T10:00:00Z",
            "updated_at": "2024-01-15T14:30:00Z",
            "downloads": 1247,
            "rating": 4.8,
        },
        {
            "id": "tensorflow-jupyter", 
            "name": "TensorFlow Jupyter Lab",
            "category": "Machine Learning",
            "description": "TensorFlow 2.14 with GPU support, Jupyter Lab, and essential data science libraries for interactive ML development.",
            "image": "tensorflow/tensorflow:2.14.0-gpu-jupyter",
            "docker_hub": "https://hub.docker.com/r/tensorflow/tensorflow",
            "requirements": {
                "gpu_required": False,
                "min_ram": "4GB",
                "min_storage": "15GB"
            },
            "compatibility": {
                "cpu": True,
                "gpu": True
            },
            "created_at": "2024-01-07T16:20:00Z",
            "updated_at": "2024-01-14T11:15:00Z",
            "downloads": 892,
            "rating": 4.6,
        },
        {
            "id": "fastapi-serve",
            "name": "FastAPI Model Server",
            "category": "Deployment",
            "description": "Production-ready FastAPI server for ML model inference with automatic docs, health checks, and monitoring.",
            "image": "tiangolo/uvicorn-gunicorn-fastapi:python3.11",
            "docker_hub": "https://hub.docker.com/r/tiangolo/uvicorn-gunicorn-fastapi",
            "requirements": {
                "gpu_required": False,
                "min_ram": "2GB",
                "min_storage": "5GB"
            },
            "compatibility": {
                "cpu": True,
                "gpu": False
            },
            "created_at": "2024-01-10T14:20:00Z",
            "updated_at": "2024-01-16T16:45:00Z",
            "downloads": 543,
            "rating": 4.5,
        },
        {
            "id": "vscode-remote",
            "name": "VS Code Remote Dev",
            "category": "Development",
            "description": "Full development environment with VS Code Server, Git, Docker, and common dev tools for remote coding.",
            "image": "codercom/code-server:latest",
            "docker_hub": "https://hub.docker.com/r/codercom/code-server", 
            "requirements": {
                "gpu_required": False,
                "min_ram": "2GB",
                "min_storage": "10GB"
            },
            "compatibility": {
                "cpu": True,
                "gpu": False
            },
            "created_at": "2024-01-03T16:45:00Z",
            "updated_at": "2024-01-13T13:15:00Z",
            "downloads": 789,
            "rating": 4.7,
        },
        {
            "id": "stable-diffusion",
            "name": "Stable Diffusion WebUI",
            "category": "AI Art",
            "description": "AUTOMATIC1111 Stable Diffusion WebUI for AI image generation with popular models and extensions pre-installed.",
            "image": "hlky/stable-diffusion-webui:latest",
            "docker_hub": "https://hub.docker.com/r/hlky/stable-diffusion-webui",
            "requirements": {
                "gpu_required": True,
                "min_ram": "16GB",
                "min_storage": "50GB"
            },
            "compatibility": {
                "cpu": False,
                "gpu": True
            },
            "created_at": "2024-01-12T11:30:00Z", 
            "updated_at": "2024-01-17T09:20:00Z",
            "downloads": 1856,
            "rating": 4.9,
        },
        {
            "id": "ubuntu-desktop",
            "name": "Ubuntu Desktop 22.04",
            "category": "OS",
            "description": "Full Ubuntu Desktop environment accessible via web browser with VNC support.",
            "image": "dorowu/ubuntu-desktop-lxde-vnc:latest",
            "docker_hub": "https://hub.docker.com/r/dorowu/ubuntu-desktop-lxde-vnc",
            "requirements": {
                "gpu_required": False,
                "min_ram": "4GB",
                "min_storage": "20GB"
            },
            "compatibility": {
                "cpu": True,
                "gpu": True
            },
            "created_at": "2024-01-05T08:30:00Z", 
            "updated_at": "2024-01-18T12:15:00Z",
            "downloads": 2341,
            "rating": 4.4,
        },
        {
            "id": "jupyter-datascience",
            "name": "Jupyter Data Science Stack", 
            "category": "Data Science",
            "description": "Complete data science environment with Python, R, Julia, pandas, scikit-learn, and visualization tools.",
            "image": "jupyter/datascience-notebook:latest",
            "docker_hub": "https://hub.docker.com/r/jupyter/datascience-notebook",
            "requirements": {
                "gpu_required": False,
                "min_ram": "4GB",
                "min_storage": "15GB"
            },
            "compatibility": {
                "cpu": True,
                "gpu": True
            },
            "created_at": "2024-01-06T14:00:00Z",
            "updated_at": "2024-01-19T10:30:00Z", 
            "downloads": 1523,
            "rating": 4.6,
        }
    ]


def get_sample_billing_data() -> List[Dict[str, Any]]:
    """Get sample billing data."""
    return [
        {
            "period": "2024-01",
            "resource": "inst_001",
            "resource_name": "ml-training-job",
            "usage": "180.5 hours",
            "cost": 442.25,
            "status": "paid",
            "invoice_id": "inv_20240131_001",
        },
        {
            "period": "2024-01",
            "resource": "inst_002", 
            "resource_name": "inference-server",
            "usage": "720.0 hours",
            "cost": 1332.00,
            "status": "paid",
            "invoice_id": "inv_20240131_002",
        },
        {
            "period": "2024-01",
            "resource": "cluster_001",
            "resource_name": "ml-training-cluster", 
            "usage": "1440.0 hours",
            "cost": 14112.00,
            "status": "paid",
            "invoice_id": "inv_20240131_003",
        },
        {
            "period": "2024-02",
            "resource": "inst_004",
            "resource_name": "dev-environment",
            "usage": "24.5 hours",
            "cost": 45.33,
            "status": "pending",
            "invoice_id": "inv_20240228_001",
        }
    ]


def get_sample_ssh_keys() -> List[Dict[str, Any]]:
    """Get sample SSH key data."""
    return [
        {
            "id": "ssh_key_001",
            "name": "laptop-key",
            "fingerprint": "SHA256:nThbg6kXUpJWGl7E1IGOCspRomTxdCARLviKw6E5SY8",
            "key_type": "ssh-rsa",
            "bits": 2048,
            "created_at": "2024-01-01T00:00:00Z",
            "last_used": "2024-01-15T08:30:00Z",
            "is_default": True,
        },
        {
            "id": "ssh_key_002", 
            "name": "server-key",
            "fingerprint": "SHA256:6NzgUy1OvKv3i8nQzqxNpzx5V7m1CKd4Z8L2R1wGc3A",
            "key_type": "ssh-ed25519", 
            "bits": 256,
            "created_at": "2024-01-05T12:00:00Z",
            "last_used": "2024-01-14T16:45:00Z",
            "is_default": False,
        },
        {
            "id": "ssh_key_003",
            "name": "backup-key",
            "fingerprint": "SHA256:8FzKLm2nP4qW9vX1b5YtE3cGh6dJ7kR0sU8iO4M9nZ2",
            "key_type": "ssh-rsa",
            "bits": 4096,
            "created_at": "2024-01-10T14:30:00Z", 
            "last_used": "2024-01-12T10:15:00Z",
            "is_default": False,
        }
    ]


def get_sample_profiles() -> List[Dict[str, Any]]:
    """Get sample user profile data."""
    return [
        {
            "name": "production",
            "api_key": SAMPLE_TOKENS["production"],
            "is_default": True,
            "created_at": "2024-01-01T00:00:00Z",
            "last_used": "2024-01-15T10:30:00Z",
        },
        {
            "name": "staging",
            "api_key": SAMPLE_TOKENS["staging"], 
            "is_default": False,
            "created_at": "2024-01-03T10:00:00Z",
            "last_used": "2024-01-14T15:20:00Z",
        },
        {
            "name": "development",
            "api_key": SAMPLE_TOKENS["development"],
            "is_default": False,
            "created_at": "2024-01-05T16:30:00Z",
            "last_used": "2024-01-13T09:45:00Z",
        }
    ]


def get_sample_machine_types() -> Dict[str, List[Dict[str, Any]]]:
    """Get sample machine type data organized by category."""
    return {
        "cpu": [
            {
                "id": "cpu-intel-xeon-gold-6248r",
                "name": "Intel Xeon Gold 6248R",
                "provider": "intel",
                "series": "xeon-scalable",
                "generation": "cascade-lake",
                "cores": 24,
                "threads": 48,
                "base_frequency": 3.0,
                "boost_frequency": 4.0,
                "memory_support": "up to 1TB",
                "architecture": "x86_64",
                "price_per_hour": 0.65,
                "availability_score": 0.96,
            },
            {
                "id": "cpu-amd-epyc-7763",
                "name": "AMD EPYC 7763",
                "provider": "amd", 
                "series": "epyc",
                "generation": "milan",
                "cores": 64,
                "threads": 128,
                "base_frequency": 2.45,
                "boost_frequency": 3.5,
                "memory_support": "up to 4TB",
                "architecture": "x86_64", 
                "price_per_hour": 0.85,
                "availability_score": 0.99,
            },
            {
                "id": "cpu-intel-core-i9-13900k",
                "name": "Intel Core i9-13900K",
                "provider": "intel",
                "series": "core",
                "generation": "raptor-lake",
                "cores": 24,
                "threads": 32,
                "base_frequency": 3.0,
                "boost_frequency": 5.8,
                "memory_support": "up to 128GB",
                "architecture": "x86_64",
                "price_per_hour": 0.45,
                "availability_score": 0.92,
            }
        ],
        "gpu": [
            {
                "id": "gpu-nvidia-h100-sxm",
                "name": "NVIDIA H100 SXM",
                "provider": "nvidia",
                "series": "h-series",
                "generation": "hopper",
                "memory_gb": 80,
                "memory_type": "HBM3",
                "compute_capability": "9.0",
                "tensor_cores": "4th Gen",
                "architecture": "hopper",
                "price_per_hour": 4.25,
                "availability_score": 0.94,
                "fp16_performance": "1979 TFLOPs",
                "fp32_performance": "67 TFLOPs",
            },
            {
                "id": "gpu-nvidia-a100-80gb",
                "name": "NVIDIA A100 80GB", 
                "provider": "nvidia",
                "series": "a-series",
                "generation": "ampere", 
                "memory_gb": 80,
                "memory_type": "HBM2e",
                "compute_capability": "8.0",
                "tensor_cores": "3rd Gen",
                "architecture": "ampere",
                "price_per_hour": 2.45,
                "availability_score": 0.98,
                "fp16_performance": "312 TFLOPs",
                "fp32_performance": "19.5 TFLOPs",
            },
            {
                "id": "gpu-nvidia-rtx4090", 
                "name": "NVIDIA RTX 4090",
                "provider": "nvidia",
                "series": "rtx",
                "generation": "ada-lovelace",
                "memory_gb": 24,
                "memory_type": "GDDR6X",
                "compute_capability": "8.9",
                "tensor_cores": "4th Gen",
                "architecture": "ada-lovelace", 
                "price_per_hour": 1.85,
                "availability_score": 0.95,
                "fp16_performance": "165 TFLOPs",
                "fp32_performance": "83 TFLOPs",
            },
            {
                "id": "gpu-amd-mi250x",
                "name": "AMD Instinct MI250X",
                "provider": "amd",
                "series": "instinct",
                "generation": "cdna2",
                "memory_gb": 128,
                "memory_type": "HBM2e",
                "compute_capability": "N/A",
                "tensor_cores": "Matrix Cores",
                "architecture": "cdna2",
                "price_per_hour": 2.15,
                "availability_score": 0.89,
                "fp16_performance": "383 TFLOPs",
                "fp32_performance": "95.7 TFLOPs",
            }
        ],
        "storage": [
            {
                "id": "storage-nvme-gen4-2tb",
                "name": "NVMe Gen4 SSD 2TB",
                "type": "NVMe SSD",
                "capacity_gb": 2000,
                "iops_read": 70000,
                "iops_write": 65000,
                "throughput_read": "7000 MB/s",
                "throughput_write": "6500 MB/s",
                "interface": "PCIe 4.0 x4",
                "price_per_hour": 0.25,
                "availability_score": 0.99,
            },
            {
                "id": "storage-sata-ssd-4tb",
                "name": "SATA SSD 4TB",
                "type": "SATA SSD",
                "capacity_gb": 4000,
                "iops_read": 100000,
                "iops_write": 90000,
                "throughput_read": "560 MB/s",
                "throughput_write": "530 MB/s",
                "interface": "SATA 3.0",
                "price_per_hour": 0.15,
                "availability_score": 0.995,
            },
            {
                "id": "storage-hdd-10tb",
                "name": "Enterprise HDD 10TB",
                "type": "HDD",
                "capacity_gb": 10000,
                "iops_read": 210,
                "iops_write": 200,
                "throughput_read": "250 MB/s", 
                "throughput_write": "240 MB/s",
                "interface": "SATA 3.0",
                "price_per_hour": 0.05,
                "availability_score": 0.98,
            }
        ]
    }


# Helper functions to get filtered data
def filter_resources(resources: List[Dict[str, Any]], **filters) -> List[Dict[str, Any]]:
    """Filter resources based on criteria."""
    filtered = resources
    
    for key, value in filters.items():
        if value is None:
            continue
            
        if key == "type" and value:
            filtered = [r for r in filtered if r.get("type", "").lower() == value.lower()]
        elif key == "provider" and value:
            # Filter by GPU or CPU provider
            def has_provider(resource, provider_name):
                gpu_specs = resource.get("gpu_specs", {})
                cpu_specs = resource.get("cpu_specs", {})
                gpu_model = gpu_specs.get("model_name", "").lower()
                cpu_model = cpu_specs.get("model_name", "").lower()
                
                return (provider_name.lower() in gpu_model or 
                       provider_name.lower() in cpu_model)
            
            filtered = [r for r in filtered if has_provider(r, value)]
        elif key == "region" and value:
            filtered = [r for r in filtered 
                       if r.get("network_info", {}).get("region", "").lower() == value.lower()]
        elif key == "status" and value:
            filtered = [r for r in filtered if r.get("deployment_status", "").lower() == value.lower()]
        elif key == "available_only" and value:
            filtered = [r for r in filtered if r.get("deployment_status", "").lower() == "inactive"]
    
    return filtered


def sort_resources(resources: List[Dict[str, Any]], sort_by: str = "price") -> List[Dict[str, Any]]:
    """Sort resources by specified criteria."""
    sort_key = "price_per_hour"
    reverse = False
    
    if sort_by == "performance":
        # For GPU resources, sort by compute capability or cores
        sort_key = lambda x: x.get("compute_capability", x.get("cpu_cores", 0))
        reverse = True
    elif sort_by == "availability": 
        sort_key = "availability_score"
        reverse = True
    elif sort_by == "name":
        sort_key = "name"
    
    if callable(sort_key):
        return sorted(resources, key=sort_key, reverse=reverse)
    else:
        return sorted(resources, key=lambda x: x.get(sort_key, 0), reverse=reverse)


def search_resources(query: str, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Search resources by name, type, GPU/CPU specs, or other fields."""
    query_lower = query.lower()
    results = []
    
    for resource in resources:
        # Get GPU and CPU specs for searching
        gpu_specs = resource.get("gpu_specs", {})
        cpu_specs = resource.get("cpu_specs", {})
        network_info = resource.get("network_info", {})
        
        searchable_fields = [
            resource.get("name", ""),
            resource.get("type", ""),
            gpu_specs.get("model_name", ""),
            cpu_specs.get("model_name", ""),
            network_info.get("region", ""),
            network_info.get("country", ""),
            network_info.get("city", ""),
            resource.get("deployment_status", ""),
            str(resource.get("gpu_count", "")),
            str(resource.get("cpu_count", "")),
            gpu_specs.get("memory", ""),
        ]
        
        searchable_text = " ".join(str(field).lower() for field in searchable_fields)
        
        if query_lower in searchable_text:
            results.append(resource)
    
    return results
