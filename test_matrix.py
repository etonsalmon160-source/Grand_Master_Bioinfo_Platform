import gzip
import urllib.request
import pandas as pd
import io

# Dataset ID
gse_id = "GSE31210"
# NCBI GEO structure: GSEnnn -> GSE[nnn-xxx] -> matrix
# GSE31210 -> GSE31nnn
# URL: https://ftp.ncbi.nlm.nih.gov/geo/series/GSE31nnn/GSE31210/matrix/GSE31210_series_matrix.txt.gz
nnn = gse_id[:-3] + "nnn"
url = f"https://ftp.ncbi.nlm.nih.gov/geo/series/{nnn}/{gse_id}/matrix/{gse_id}_series_matrix.txt.gz"
print(f"Downloading {url} ...")

try:
    response = urllib.request.urlopen(url)
    compressed_file = io.BytesIO(response.read())
    decompressed_file = gzip.GzipFile(fileobj=compressed_file)
    
    # Read the file to extract metadata and counts
    lines = [line.decode('utf-8') for line in decompressed_file.readlines()]
    print("Downloaded successfully! Total lines:", len(lines))
    
    # Simple parse
    data_start = 0
    for i, line in enumerate(lines):
        if line.startswith('!series_matrix_table_begin'):
            data_start = i + 1
            break
            
    header = lines[data_start].strip().split('\t')
    print("Header:", header[:5], "...")
except Exception as e:
    import traceback
    traceback.print_exc()
