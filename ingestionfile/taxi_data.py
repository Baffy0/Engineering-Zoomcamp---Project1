#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sqlalchemy import create_engine
from tqdm import tqdm
import click
import os
import requests
import pyarrow.dataset as ds


def download_parquet_if_not_exists(url, output_path):
    if os.path.exists(output_path):
        print(f"File already exists: {output_path}")
        print("⏭️ Skipping download.")
        return output_path

    print("⬇️ File not found. Starting download...")

    r = requests.get(url, stream=True)
    r.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"Download completed: {output_path}")
    return output_path


@click.command()
@click.option('--pg-user', default='root')
@click.option('--pg-pass', default='root')
@click.option('--pg-host', default='taxi_trips')
@click.option('--pg-port', default=5432, type=int)
@click.option('--pg-db', default='Trips_Ingestion')
@click.option('--url', required=True)
@click.option('--table_name', default='green_trip_data')



def main(pg_user, pg_pass, pg_host, pg_port, pg_db, url, table_name):

    file_path = "data.parquet"

    # Download file
    download_parquet_if_not_exists(url, file_path)

    # Create engine
    engine = create_engine(
        f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
    )

    dataset = ds.dataset(file_path, format="parquet")

    batch_size = 10000
    total_batches = dataset.count_rows() // batch_size + 1

    print("🚀 Starting data ingestion...")

    total_rows = 0

    for i, batch in enumerate(tqdm(dataset.to_batches(batch_size=batch_size), total=total_batches)):
        df_chunk = batch.to_pandas()

        # Convert datetime columns
        df_chunk["lpep_pickup_datetime"] = pd.to_datetime(df_chunk["lpep_pickup_datetime"])
        df_chunk["lpep_dropoff_datetime"] = pd.to_datetime(df_chunk["lpep_dropoff_datetime"])

        df_chunk.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace" if i == 0 else "append",  # ✅ FIX
            index=False,
            method="multi"
        )

        total_rows += len(df_chunk)

    print(f" Loaded {total_rows} rows.")


if __name__ == "__main__":
    main()