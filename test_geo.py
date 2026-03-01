import GEOparse
import sys

try:
    gse = GEOparse.get_GEO(geo="GSE31210", destdir="D:/Bioinfo_Temp_Work", silent=False)
    print("Download success!", gse.name)
except Exception as e:
    import traceback
    traceback.print_exc()
