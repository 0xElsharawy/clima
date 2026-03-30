terraform {
  required_providers {
    minio = {
      source  = "aminueza/minio"
      version = ">= 1.0.0"
    }
  }
}

provider "minio" {
  minio_server = "localhost:9000"

  minio_user     = "mioadmin"
  minio_password = "mioadmin"
  minio_ssl      = false
}

resource "minio_s3_bucket" "weather_data" {
  bucket        = "weather-bucket"
  acl           = "private"
  force_destroy = true
}
