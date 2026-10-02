"""
============================================================================
 PREPARACAO DOS DADOS REAIS (NYC Taxi & Limousine Commission - TLC)
============================================================================
 Roda DENTRO do container 'spark' (que tem pandas/pyarrow/requests).
 Este arquivo fica em dados/ e e visto pelo container em /data/preparar_dados.py.
 Os arquivos gerados vao para dados/brutos/ (visto em /data/brutos no container).

 Baixa dois conjuntos ABERTOS e OFICIAIS da cidade de Nova York:
   1) Corridas de taxi amarelo -> vira o nosso CSV cru (amostra real de 300k).
      O original e .parquet; convertemos para CSV (muda so o formato).
   2) Tabela de zonas (taxi_zone_lookup.csv) -> vira a dimensao no MySQL.

 O script e IDEMPOTENTE: se os arquivos ja existem, nao baixa de novo.
============================================================================
"""
import os
import requests
import pandas as pd

RAW = "/data/brutos"
os.makedirs(RAW, exist_ok=True)

TRIPS_PARQUET_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
ZONES_CSV_URL     = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"

TRIPS_PARQUET = f"{RAW}/yellow_tripdata_2024-01.parquet"
TRIPS_CSV     = f"{RAW}/yellow_tripdata.csv"      # <- CSV cru que vai pro HDFS
ZONES_CSV     = f"{RAW}/taxi_zone_lookup.csv"
ZONES_SQL     = f"{RAW}/zones_insert.sql"         # <- INSERTs p/ o MySQL

SAMPLE_ROWS = 300_000   # amostra real (o mes inteiro tem ~3 milhoes)


def download(url: str, dest: str) -> None:
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"[skip] ja existe: {dest}")
        return
    print(f"[download] {url}")
    with requests.get(url, stream=True, timeout=180) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    print(f"[ok] salvo: {dest} ({os.path.getsize(dest) // 1024} KB)")


def build_trips_csv() -> None:
    if os.path.exists(TRIPS_CSV) and os.path.getsize(TRIPS_CSV) > 0:
        print(f"[skip] CSV de corridas ja existe: {TRIPS_CSV}")
        return
    download(TRIPS_PARQUET_URL, TRIPS_PARQUET)
    print("[convert] lendo o parquet oficial com pandas...")
    df = pd.read_parquet(TRIPS_PARQUET)
    print(f"[info] o mes completo tem {len(df):,} corridas reais")
    if len(df) > SAMPLE_ROWS:
        df = df.sample(n=SAMPLE_ROWS, random_state=42).reset_index(drop=True)
        print(f"[info] usando amostra reproduzivel de {len(df):,} corridas")
    df.to_csv(TRIPS_CSV, index=False)
    mb = os.path.getsize(TRIPS_CSV) / 1024 / 1024
    print(f"[ok] CSV cru gerado: {TRIPS_CSV} ({mb:.1f} MB)")
    try:
        os.remove(TRIPS_PARQUET)
    except OSError:
        pass


def build_zones_sql() -> None:
    download(ZONES_CSV_URL, ZONES_CSV)
    z = pd.read_csv(ZONES_CSV)

    def esc(v):
        if pd.isna(v):
            return "NULL"
        return "'" + str(v).replace("'", "''") + "'"

    linhas = ["USE nyc;", "SET autocommit=0;"]
    for _, r in z.iterrows():
        linhas.append(
            "INSERT IGNORE INTO taxi_zones (LocationID,Borough,Zone,service_zone) "
            f"VALUES ({int(r['LocationID'])},{esc(r['Borough'])},"
            f"{esc(r['Zone'])},{esc(r['service_zone'])});"
        )
    linhas.append("COMMIT;")
    with open(ZONES_SQL, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    print(f"[ok] SQL de zonas gerado: {ZONES_SQL} ({len(z)} zonas)")


if __name__ == "__main__":
    build_trips_csv()
    build_zones_sql()
    print("\n=== PREPARACAO DE DADOS CONCLUIDA ===")
    print(f"CSV de corridas : {TRIPS_CSV}")
    print(f"SQL de zonas    : {ZONES_SQL}")
