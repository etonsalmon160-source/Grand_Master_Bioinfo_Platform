"""
精确诊断 v2: 逐步验证 metadata index 和 counts columns 是否对齐
"""
import os
from custom_geo_parser import fetch_real_geo_matrix_with_genes
from master_bioinfo_suite import MasterBioinfoPipeline

OUT = r"D:\Bioinfo_Temp_Work\TEST_DIAG2"
os.makedirs(OUT, exist_ok=True)

print("STEP 1: 下载 ...")
counts, metadata = fetch_real_geo_matrix_with_genes("GSE31210")

print(f"\ncounts.columns[:5] = {list(counts.columns[:5])}")
print(f"metadata.index[:5] = {list(metadata.index[:5])}")
print(f"counts columns count = {len(counts.columns)}")
print(f"metadata rows count = {len(metadata)}")

# 关键：检查是否对齐
overlap = set(counts.columns) & set(metadata.index)
print(f"overlap count = {len(overlap)}")
diff1 = set(counts.columns) - set(metadata.index)
diff2 = set(metadata.index) - set(counts.columns)
print(f"in counts but not meta: {len(diff1)}, examples: {list(diff1)[:3]}")
print(f"in meta but not counts: {len(diff2)}, examples: {list(diff2)[:3]}")

# 检查分组
print(f"\nGroup value_counts:\n{metadata['Group'].value_counts()}")

# 测试预处理
pipeline = MasterBioinfoPipeline(out_dir=OUT)
pipeline.run_pre_processing(custom_counts=counts, custom_meta=metadata)

# 测试 DEA 的 cancer/healthy 分组
cancer = pipeline.metadata[pipeline.metadata['Group']=='Cancer'].index
healthy = pipeline.metadata[pipeline.metadata['Group']=='Healthy'].index
print(f"\ncancer count = {len(cancer)}")
print(f"healthy count = {len(healthy)}")

# 测试一个基因的 ttest
import scipy.stats as stats
g = pipeline.log_cpm.index[0]
vals_c = pipeline.log_cpm.loc[g, cancer]
vals_h = pipeline.log_cpm.loc[g, healthy]
print(f"\ngene={g}, cancer vals shape={vals_c.shape}, healthy vals shape={vals_h.shape}")
print(f"cancer vals NaN = {vals_c.isna().sum()}, healthy vals NaN = {vals_h.isna().sum()}")

t, p = stats.ttest_ind(vals_c, vals_h)
print(f"t={t}, p={p}")
print("✅ 单基因 t-test 通过!")
