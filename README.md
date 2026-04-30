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
  postgres:
    image: postgres:13
    container_name: taxi_trips
    environment:
      POSTGRES_USER: root
      POSTGRES_PASSWORD: root
      POSTGRES_DB: Trips_Ingestion
    ports:
      - "5432:5432"
    networks:
      - taxi_network
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

##  Prepare the Data

Download taxi trips data:

```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2025-11.parquet
```

Download taxi zones dataset:

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv
```

---

##  Data Architecture
<img src="https://github.com/user-attachments/assets/43689321-35c4-45ba-ac86-2cbb00e3212a" width="680"/>


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
docker build -t taxi_data .
```

Run the container:

```bash
docker run -it --rm \
  --network taxi_nextwork \
  --name taxi_zone \
  taxi_data
```

Run ingestion scripts:

```bash
uv run python taxi_data.py
uv run python taxi_zone.py
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
Host name/address: Trips_Ingestion
Port: 5432
Maintenance database: taxi_db
Username: root
Password: root
```

---

## SQL Queries

### Question 3: Counting Short Trips

```sql
SELECT 
    COUNT(*) AS short_trip_count
FROM green_taxi_table AS gtt
WHERE gtt.lpep_pickup_datetime >= '2025-11-01'
  AND gtt.lpep_pickup_datetime < '2025-12-01'
  AND gtt.trip_distance <= 1;
```

**Answer:**

```
8007
```

---

### Question 4: Longest Trip for Each Day

```sql
SELECT 
    daily_data.pickup_day
FROM (
    SELECT
        DATE(gtt.lpep_pickup_datetime) AS pickup_day,
        SUM(gtt.trip_distance) AS total_distance
    FROM green_taxi_table AS gtt
    WHERE gtt.trip_distance < 100
    GROUP BY DATE(gtt.lpep_pickup_datetime)
    ORDER BY total_distance DESC
) AS daily_data
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
    zn."Zone" AS zone_name,
    SUM(gt.total_amount) AS total_revenue
FROM green_taxi_table AS gt
JOIN zones AS zn 
    ON gt."PULocationID" = zn."LocationID"
WHERE DATE(gt.lpep_pickup_datetime) = '2025-11-18'
GROUP BY zn."Zone"
ORDER BY total_revenue DESC;
```

**Answer:**

```
East Harlem North
```

---

### Question 6: Largest Tip

```sql
SELECT 
    dz."Zone" AS dropoff_zone_name,
    gt.tip_amount AS highest_tip
FROM green_taxi_table AS gt
JOIN zones AS dz 
    ON gt."DOLocationID" = dz."LocationID"
JOIN zones AS pz 
    ON gt."PULocationID" = pz."LocationID"
WHERE 
    pz."Zone" = 'East Harlem North'
    AND gt.lpep_pickup_datetime >= '2025-11-01'
    AND gt.lpep_pickup_datetime < '2025-12-01'
ORDER BY gt.tip_amount DESC
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





