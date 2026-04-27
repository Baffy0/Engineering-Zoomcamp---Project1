# Engineering-Zoomcamp---Project1
# Module 1 Homework: Docker & SQL

This repository contains my solution for **Module 1 Homework** from the *Data Engineering Zoomcamp*.

---

## 🐳 Docker

### Question 1: Understanding Docker Images

Run a Python container:

```bash
docker run -it --rm --entrypoint=bash python:3.13
```

Check the pip version:

```bash
pip --version
```

**Answer:**

```
26
```

---

### Question 2: Docker Networking & Docker Compose

Given the `docker-compose.yaml`:

```yaml
services:
  db:
    container_name: postgres
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: 'postgres'
      POSTGRES_PASSWORD: 'postgres'
      POSTGRES_DB: 'taxi_data'
    ports:
      - '5433:5432'
    volumes:
      - vol-pgdata:/var/lib/postgresql/data
```

Since pgAdmin and Postgres are on the same Docker network, containers communicate using:

* **Hostname:** `db`
* **Port:** `5432`

The mapping `5433:5432` is only for host-to-container access.

**Answer:**

```
db:5432
```

---

## 📦 Prepare the Data

Download taxi trips data:

```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet
```

Download taxi zones dataset:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

---

## 🏗️ Data Architecture

*(Add architecture image here if available)*

---

## ⚙️ Steps

```bash
docker compose up -d
```

> Take note of the network name created by Docker Compose.

```bash
docker compose ps
```

Build the ingestion image:

```bash
docker build -t taxi_ingestion-python .
```

Run the container:

```bash
docker run -it --rm \
  --network module13_taxi_ingestion \
  --name taxi_ingestion-python-container \
  taxi_ingestion-python
```

Run ingestion scripts:

```bash
uv run python green_taxi.py
uv run python zones_taxi.py
```

---

## 🔐 pgAdmin Access

Open:

```
http://localhost:8086
```

Login credentials:

```
admin@taxi.com
root
```

### Connect to Postgres:

```
Host name/address: taxi_ingestion_db
Port: 5432
Maintenance database: taxi_db
Username: root
Password: root
```

---

## 🧮 SQL Queries

### Question 3: Counting Short Trips

```sql
SELECT 
    COUNT(*) AS Trips_less_1mile
FROM green_taxi_table
WHERE lpep_pickup_datetime >= '2025-11-01' 
  AND lpep_pickup_datetime < '2025-12-01'
  AND trip_distance <= 1;
```

**Answer:**

```
8007
```

---

### Question 4: Longest Trip for Each Day

```sql
SELECT 
    pickup_date
FROM
    (SELECT
         DATE(lpep_pickup_datetime) AS pickup_date,
         SUM(trip_distance) AS TotalDist
     FROM green_taxi_table
     WHERE trip_distance < 100
     GROUP BY DATE(lpep_pickup_datetime)
     ORDER BY SUM(trip_distance) DESC) AS T
LIMIT 1;
```

**Answer:**

```
2025-11-20
```

---

### Question 5: Biggest Pickup Zone

```sql
SELECT 
    Z."Zone",
    SUM(G.total_amount) AS SumofMoneyPaid
FROM green_taxi_table AS G
JOIN zones Z ON G."PULocationID" = Z."LocationID"
WHERE DATE(lpep_pickup_datetime) = '2025-11-18'
GROUP BY Z."Zone"
ORDER BY SumofMoneyPaid DESC;
```

**Answer:**

```
East Harlem North
```

---

### Question 6: Largest Tip

```sql
SELECT 
    Z1."Zone" AS dropoff_zone,
    G.tip_amount
FROM green_taxi_table AS G
JOIN zones Z1 ON G."DOLocationID" = Z1."LocationID"
JOIN zones Z2 ON G."PULocationID" = Z2."LocationID"
WHERE 
    Z2."Zone" = 'East Harlem North'
    AND G.lpep_pickup_datetime >= '2025-11-01'
    AND G.lpep_pickup_datetime < '2025-12-01'
ORDER BY G.tip_amount DESC
LIMIT 1;
```

**Answer:**

```
Yorkville West
```

---

## 🧹 Cleanup

```bash
docker compose down
```

---

## ☁️ Terraform

### Setup

Created the following files:

* `main.tf`
* `variables.tf`
* `outputs.tf`
* `terraform.tfvars`

Configured GCP access and permissions.

---

### Commands Used

```bash
terraform init
terraform plan
terraform apply
```

---

### Question 7: Terraform Workflow

Correct workflow sequence:

```bash
terraform init
terraform apply -auto-approve
terraform destroy
```

**Answer:**

```
terraform init, terraform apply -auto-approve, terraform destroy
```

---

## 📚 References

* https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
* https://registry.terraform.io/modules/terraform-google-modules/bigquery/google/latest
* https://cloud.google.com/blog/products/data-analytics/introducing-the-bigquery-terraform-module
* https://registry.terraform.io/providers/hashicorp/google/4.35.0/docs/resources/storage_bucket

---

## 🔗 Alternative Solution

* https://github.com/stephandoh/zoomcamp57877

---

