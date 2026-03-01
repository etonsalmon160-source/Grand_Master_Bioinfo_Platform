import os
import shutil
import time
import requests
import json
import logging
from datetime import datetime
from master_bioinfo_suite import MasterBioinfoPipeline

# ----------------- CONFIGURATION -----------------
# 硬盘管控限制：C盘太满，工作区转移至 D 盘
TEMP_WORK_DIR = r"D:\Bioinfo_Temp_Work"   # 临时下载与计算目录（用完即删）
FINAL_RES_DIR = r"D:\Bioinfo_Final_Reports" # 最终报告与精美图表永久保存位置
PUSHPLUS_TOKEN = "b5300e241cad4d73b36533b5c950e22d"
# -------------------------------------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def notify_boss(msg_title, msg_content):
    """通过 PushPlus 将进度汇报给 Boss (微信)。若环境变量 OPENCLAW_NO_NOTIFY=1 则不发送。"""
    if os.environ.get("OPENCLAW_NO_NOTIFY") == "1":
        return
    url = "https://www.pushplus.plus/send"
    data = {
        "token": PUSHPLUS_TOKEN,
        "title": msg_title,
        "content": msg_content,
        "template": "markdown"
    }
    try:
        requests.post(url, json=data, timeout=5)
    except:
        pass

def setup_d_drive_environment():
    """初始化 D 盘工作环境，确保干净"""
    logging.info("初始化硬盘目录...")
    os.makedirs(FINAL_RES_DIR, exist_ok=True)
    
    # 如果上次有残留临时文件，清理掉
    if os.path.exists(TEMP_WORK_DIR):
        shutil.rmtree(TEMP_WORK_DIR)
    os.makedirs(TEMP_WORK_DIR)

def process_single_dataset(dataset_id, n_genes, n_samples):
    """
    处理单个数据集：
    1. 下载到临时目录
    2. 分析
    3. 转移结果
    4. 销毁临时数据
    """
    logging.info(f"==== 🚀 开始处理任务: {dataset_id} ====")
    notify_boss(f"📥 自动任务接管: {dataset_id}", f"后台智能脚本开始处理 `{dataset_id}`。\n\n**内存与硬盘策略**: 数据将下载至 D 盘临时安全沙箱。")
    
    logging.info(f"[{dataset_id}] 正在连接远端 NCBI GEO 数据库下载真实数据 (至 {TEMP_WORK_DIR}) ... (请耐心等待, 可能达数百MB)")
    
    # 初始化咱们的“生信大模型”流水线，指定输出先挂载到 D盘临时目录
    pipeline = MasterBioinfoPipeline(out_dir=os.path.join(TEMP_WORK_DIR, f"{dataset_id}_output"))
    pipeline.dataset_id = dataset_id
    
    try:
        from custom_geo_parser import fetch_real_geo_matrix_with_genes
        counts, metadata = fetch_real_geo_matrix_with_genes(dataset_id.split('_')[0])
        
        logging.info(f"[{dataset_id}] 成功获取真实表达矩阵 (含基因 Symbol 映射): {counts.shape[0]} 基因, {counts.shape[1]} 样本。")
        
        # 汇报自主决策结果
        decision = metadata['DecisionReason'].iloc[0] if 'DecisionReason' in metadata.columns else "标准分析"
        mode = metadata['AnalysisMode'].iloc[0] if 'AnalysisMode' in metadata.columns else "DEA"
        logging.info(f"[{dataset_id}] 🧠 自主决策: {decision} | 分析模式: {mode}")
        notify_boss(f"🧠 {dataset_id} 自主决策", f"**分组策略**: {decision}\n\n**分析模式**: {mode}\n\n正在自动执行后续分析流程...")
        
        # 把真实的 GEO counts 和 metadata 喂给预处理模块
        pipeline.run_pre_processing(custom_counts=counts, custom_meta=metadata)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        logging.error(f"HTTPS 下载/解析失败: {e}，不再回退，直接抛出以便排错。")
        raise e
    
    time.sleep(2) # 给机器一点喘息时间
    
    logging.info(f"[{dataset_id}] 跑差异表达式 (DEA)...")
    pipeline.run_dea()
    time.sleep(2)
    
    logging.info(f"[{dataset_id}] 跑共表达网络与机器学习 (WGCNA & ML)...")
    pipeline.run_wgcna_lite()
    if hasattr(pipeline, 'run_advanced_ml'):
        pipeline.run_advanced_ml()
    else:
        pipeline.run_ml_biomarkers()
    time.sleep(5)  # 模型训练需要时间
    
    logging.info(f"[{dataset_id}] 生成最终报告...")
    pipeline.generate_report()
    
    # ============== 核心硬盘管理逻辑 ==============
    logging.info(f"[{dataset_id}] 分析完成，开始执行硬盘清理策略。")
    
    # 1. 把精华结果（图表、Markdown报告）转移到最终保留目录
    final_output_path = os.path.join(FINAL_RES_DIR, dataset_id)
    if os.path.exists(final_output_path):
        shutil.rmtree(final_output_path)
    
    # 将临时目录下的精华输出，移动到永久层
    shutil.copytree(pipeline.out_dir, final_output_path)
    
    # 2. 物理销毁临时“海量数据”以腾出 D 盘空间
    logging.info(f"[{dataset_id}] 正在销毁 {TEMP_WORK_DIR} 下的 Gb 级原始缓存...")
    shutil.rmtree(TEMP_WORK_DIR)
    # 重新建一个空的给下一个任务用
    os.makedirs(TEMP_WORK_DIR)
    
    logging.info(f"[{dataset_id}] 空间已释放，结果已归档至: {final_output_path}")
    
    # 微信报喜
    msg = f"""
    ## ✅ 数据集 {dataset_id} 分析完毕！
    
    **关键发现**:
    核心标志基因已被锁定！(Top Gene: **{pipeline.top_gene}**)
    
    **硬盘状态评估**:
    - 🧹 原始脏数据及大缓存已安全销毁，您的 C 盘与 D 盘空间安全。
    - 📁 核心报告和超清图表已永久保存在：`{final_output_path}`
    
    *OpenClaw 智能流水线执行完毕。*
    """
    notify_boss(f"✅ {dataset_id} 结果出炉", msg)

def auto_pilot_mode():
    """连贯处理多个任务的工作流大脑"""
    setup_d_drive_environment()
    
    print("\n" + "="*50)
    print(" 🦞 OpenClaw 生信智能挂机脚本启动")
    print(f" 工作沙箱: {TEMP_WORK_DIR} (用完即焚)")
    print(f" 最终归档: {FINAL_RES_DIR} (永久保留)")
    print("="*50 + "\n")
    
    # 任务队列：三个经典的肺腺癌 (LUAD) 数据集
    task_queue = [
        {"id": "GSE31210_LUAD_Cohort", "genes": 2500, "samples": 40},
        {"id": "GSE30219_LUAD_Validation", "genes": 2200, "samples": 30},
        {"id": "GSE19188_LUAD_Metastasis", "genes": 3000, "samples": 50}
    ]
    
    for task in task_queue:
        try:
            process_single_dataset(task['id'], task['genes'], task['samples'])
            logging.info("休眠 10 秒后开启下一个任务，防止被封 IP / 过温...")
            time.sleep(10)
        except Exception as e:
            logging.error(f"任务 {task['id']} 失败: {e}")
            notify_boss(f"❌ 任务失败: {task['id']}", f"遇到错误: {e}")

if __name__ == "__main__":
    auto_pilot_mode()
