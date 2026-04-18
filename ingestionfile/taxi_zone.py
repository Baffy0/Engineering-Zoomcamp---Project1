
import pandas as pd
from sqlalchemy import create_engine
from tqdm import tqdm
import click
import os
import requests
import pyarrow.dataset as ds

import os
import requests

url2 = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv'

def download_csv_if_not_exists(url, output_path):
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

    print(f"✅ Download completed: {output_path}")
    return output_path


@click.command()
@click.option('--pg-user', default='root')
@click.option('--pg-pass', default='root')
@click.option('--pg-host', default='taxi_trips')
@click.option('--pg-port', default=5432, type=int)
@click.option('--pg-db', default='Trips_Ingestion')
@click.option('--url', default=url2)
@click.option('--table_name', default='taxi_zone_data')


def main(pg_user, pg_pass, pg_host, pg_port, pg_db, url, table_name):
    file_path = "zones_data.csv"

    # Download file
    download_csv_if_not_exists(url, file_path)

    # Create engine
    engine = create_engine(
        f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}'
    )

    dataset = ds.dataset(file_path, format="csv")
    batch_size = 500
    total_batches = dataset.count_rows() // batch_size + 1

    print("🚀 Starting data ingestion...")
    total_rows = 0

    for i, batch in enumerate(tqdm(dataset.to_batches(batch_size=batch_size), total=total_batches)):
        df_chunk = batch.to_pandas()
        df_chunk.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace" if i == 0 else "append",
            index=False,
            method="multi"
        )
        total_rows += len(df_chunk)

    print(f"Total rows loaded: {total_rows}")

if __name__ == "__main__":
    main()