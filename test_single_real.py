"""
精确诊断: 只跑 GSE31210 的真实数据下载 + 预处理 + DEA，
完全不吞异常，所有错误全部暴露。
"""
import os
import traceback
from custom_geo_parser import fetch_real_geo_matrix_with_genes
from master_bioinfo_suite import MasterBioinfoPipeline

OUT = r"D:\Bioinfo_Temp_Work\TEST_DIAG"
os.makedirs(OUT, exist_ok=True)

print("=" * 60)
print("STEP 1: 下载 GSE31210 真实 Series Matrix ...")
print("=" * 60)
counts, metadata = fetch_real_geo_matrix_with_genes("GSE31210")
print(f"\n✅ 表达矩阵 shape: {counts.shape}")
print(f"✅ 元数据 shape: {metadata.shape}")
print(f"✅ 前10个基因名: {list(counts.index[:10])}")
print(f"✅ 分组分布:\n{metadata['Group'].value_counts()}")
print(f"✅ 表达矩阵 NaN 总数: {counts.isna().sum().sum()}")
print(f"✅ 前 5x5 数据:\n{counts.iloc[:5, :5]}")

print("\n" + "=" * 60)
print("STEP 2: 初始化 Pipeline + 预处理 ...")
print("=" * 60)
pipeline = MasterBioinfoPipeline(out_dir=OUT)
pipeline.run_pre_processing(custom_counts=counts, custom_meta=metadata)

print(f"\n✅ log_cpm shape: {pipeline.log_cpm.shape}")
print(f"✅ log_cpm NaN 总数: {pipeline.log_cpm.isna().sum().sum()}")
print(f"✅ log_cpm 前10个基因: {list(pipeline.log_cpm.index[:10])}")

print("\n" + "=" * 60)
print("STEP 3: 差异表达分析 DEA ...")
print("=" * 60)
pipeline.run_dea()
print(f"✅ 显著基因数: {len(pipeline.sig_genes)}")
print(f"✅ Top 10 显著基因: {pipeline.sig_genes[:10]}")

print("\n" + "=" * 60)
print("STEP 4: WGCNA ...")
print("=" * 60)
pipeline.run_wgcna_lite()

print("\n" + "=" * 60)
print("STEP 5: Advanced ML (LASSO + RF) ...")
print("=" * 60)
pipeline.run_advanced_ml()

print(f"\n✅ Top Gene (最终标志物): {pipeline.top_gene}")

print("\n" + "=" * 60)
print("STEP 6: 生成报告 ...")
print("=" * 60)
pipeline.generate_report()

print("\n🎉 全流程完毕! 检查目录:", OUT)
