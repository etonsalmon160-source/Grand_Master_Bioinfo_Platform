#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 生信工作流启动器
支持两种启动方式：
  1. 传统 GSE 号：直接传入一个或多个 GSE 编号
  2. 自然语言描述：用一句话描述任务，自动从中识别 GSE 编号并执行
"""

import re
import sys
import argparse
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

# GSE 编号正则：GSE + 数字（常见为 5–8 位）
GSE_PATTERN = re.compile(r"GSE\d+", re.IGNORECASE)


def parse_gse_from_text(text: str) -> list[str]:
    """
    智能语言引擎：从自然语言描述中抽取显式 GSE，或根据语义推断并分配优质数据集。
    """
    if not text or not text.strip():
        return []
    
    found = GSE_PATTERN.findall(text)
    
    # === 🤖 Grand Master AI NLP Intent Engine ===
    if not found:
        text_l = text.lower()
        if "肺腺癌" in text_l or "luad" in text_l or "lung adenocarcinoma" in text_l:
            # 智能量词识别
            if "一" in text_l or "1" in text_l:
                found = ["GSE31210"]
                logger.info("🤖 [AI 助理] 已识别意图：1个肺腺癌数据集。自动分配经典队列：GSE31210")
            elif "三" in text_l or "3" in text_l:
                found = ["GSE31210", "GSE30219", "GSE19188"]
                logger.info("🤖 [AI 助理] 已识别意图：3个肺腺癌数据集。自动联动三大经典队列进行联合分析...")
            else:
                # 默认匹配两个，用于触发牛逼的 Flexible ML 交叉验证
                found = ["GSE31210", "GSE30219"]
                logger.info("🤖 [AI 助理] 已识别意图：多队列肺腺癌联合分析。自动分配优质训练与独立验证集：GSE31210, GSE30219")
        elif "鳞癌" in text_l or "lusc" in text_l:
            found = ["GSE73403"]
            logger.info("🤖 [AI 助理] 已识别意图：肺鳞癌队列分析。自动分配：GSE73403")

    seen = set()
    unique = []
    for g in found:
        g_upper = g.upper()
        if g_upper not in seen:
            seen.add(g_upper)
            unique.append(g_upper)
    return unique


def is_gse_like(s: str) -> bool:
    """判断字符串是否形如 GSE 编号（GSE + 数字）。"""
    return bool(s and GSE_PATTERN.fullmatch(s.strip().upper()))


def parse_launcher_args(argv: list[str] | None = None):
    """
    解析启动器参数，区分「传统 GSE 模式」与「自然语言模式」。
    返回 (gse_list, is_nl_mode)。
    """
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="OpenClaw 生信工作流启动器：支持 GSE 号或自然语言描述",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  传统 GSE 启动：
    python launcher.py GSE31210
    python launcher.py GSE31210 GSE30219 GSE19188
    python launcher.py --gse GSE31210 GSE30219

  自然语言启动：
    python launcher.py "分析肺腺癌数据集 GSE31210"
    python launcher.py "跑一下 GSE31210 和 GSE30219 的差异表达"
    python launcher.py --nl "请对 GSE19188 做完整分析"

  交互模式（不传参数）：
    python launcher.py
        """,
    )
    parser.add_argument(
        "positional",
        nargs="*",
        help="GSE 编号（如 GSE31210）或一整句自然语言描述",
    )
    parser.add_argument(
        "--gse",
        nargs="+",
        metavar="ID",
        help="显式指定一个或多个 GSE 编号",
    )
    parser.add_argument(
        "-n",
        "--nl",
        "--natural",
        dest="natural_language",
        metavar="TEXT",
        help="自然语言描述，从中自动识别 GSE 编号",
    )
    parser.add_argument(
        "--no-notify",
        action="store_true",
        help="关闭微信/PushPlus 通知（仅本地运行）",
    )
    parser.add_argument(
        "--simple",
        action="store_true",
        default=True,
        help="简约模式：在当前目录运行，不依赖 D 盘（默认方案）",
    )
    parser.add_argument(
        "--full",
        dest="simple",
        action="store_false",
        help="全量模式：开启 D 盘持久化存储与自动化归档（需电脑有 D 盘）",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅解析参数并打印将要运行的 GSE 列表，不执行流程",
    )
    args = parser.parse_args(argv)

    gse_list = []
    is_nl_mode = False

    if args.gse:
        # 显式 --gse GSE1 GSE2
        for x in args.gse:
            if is_gse_like(x):
                gse_list.append(x.strip().upper())
            else:
                logger.warning("忽略非法 GSE 编号: %s", x)
    elif args.natural_language:
        # 显式 --nl "描述"
        is_nl_mode = True
        gse_list = parse_gse_from_text(args.natural_language)
        logger.info("自然语言解析: 「%s」 -> GSE 列表: %s", args.natural_language.strip(), gse_list)
    elif args.positional:
        first = args.positional[0]
        # 若第一个参数像 GSE，则全部按 GSE 解析
        if is_gse_like(first):
            for x in args.positional:
                if is_gse_like(x):
                    gse_list.append(x.strip().upper())
        else:
            # 否则整句当作自然语言
            is_nl_mode = True
            text = " ".join(args.positional)
            gse_list = parse_gse_from_text(text)
            logger.info("自然语言解析: 「%s」 -> GSE 列表: %s", text, gse_list)
    else:
        # 无参数：交互模式
        return None, False, args

    if not gse_list and (args.gse or args.natural_language or args.positional):
        logger.error("未识别到任何有效的 GSE 编号，请检查输入。")
        sys.exit(1)

    return gse_list, is_nl_mode, args


def run_workflow_simple(gse_id: str) -> None:
    """
    简化流程：当前目录运行，结果保存在 Run_<GSE>_Results，不依赖 D 盘与通知。
    复用 run_real_datasets 的逻辑。
    """
    from custom_geo_parser import fetch_real_geo_matrix_with_genes
    from master_bioinfo_suite import MasterBioinfoPipeline

    logger.info("Starting run for %s (simple mode)", gse_id)
    counts, meta = fetch_real_geo_matrix_with_genes(gse_id)
    logger.info("Fetched counts: %s, meta: %s", counts.shape, meta.shape)

    pipeline = MasterBioinfoPipeline(out_dir=f"Run_{gse_id}_Results")
    pipeline.run_pre_processing(custom_counts=counts, custom_meta=meta)
    pipeline.run_dea()
    pipeline.run_deg_heatmap()
    pipeline.run_wgcna_lite()
    if hasattr(pipeline, "run_advanced_ml"):
        pipeline.run_advanced_ml()
    else:
        try:
            pipeline.run_ml_biomarkers()
        except Exception:
            logger.warning("No ML entrypoint found, skipping ML step")
    if hasattr(pipeline, "run_survival") and callable(pipeline.run_survival):
        pipeline.run_survival()
    if hasattr(pipeline, "run_enrichment") and callable(pipeline.run_enrichment):
        pipeline.run_enrichment()
    pipeline.generate_report()
    logger.info("Completed run for %s. Results saved to %s", gse_id, pipeline.out_dir)


def run_workflow_full(dataset_id: str, no_notify: bool = False) -> None:
    """
    完整流程：D 盘临时目录、结果归档、可选 PushPlus 通知。
    复用 auto_agent_workflow 的 process_single_dataset。
    """
    from auto_agent_workflow import process_single_dataset

    # 若关闭通知，需在 auto_agent_workflow 内屏蔽；此处仅传参，若该模块支持环境变量可在这里设置
    if no_notify:
        import os
        os.environ["OPENCLAW_NO_NOTIFY"] = "1"

    try:
        # process_single_dataset 接受 id（可带后缀如 GSE31210_LUAD）和 n_genes, n_samples（仅占位）
        process_single_dataset(dataset_id, n_genes=3000, n_samples=50)
    finally:
        if no_notify:
            import os
            os.environ.pop("OPENCLAW_NO_NOTIFY", None)


def interactive_prompt():
    """交互式输入一行，解析为 GSE 列表或自然语言。"""
    print("\n" + "=" * 50)
    print("  OpenClaw 生信工作流启动器（交互模式）")
    print("=" * 50)
    print("  请输入 GSE 编号或自然语言描述，例如：")
    print("    GSE31210")
    print("    GSE31210 GSE30219")
    print("    分析肺腺癌数据集 GSE31210 和 GSE30219")
    print("=" * 50 + "\n")
    try:
        line = input(">>> ").strip()
    except EOFError:
        return []
    if not line:
        return []
    if is_gse_like(line.split()[0]):
        return [x.upper() for x in line.split() if is_gse_like(x)]
    return parse_gse_from_text(line)


def run_workflow_flexible_ml(train_gse: str, test_gse: str, use_simple: bool = True) -> None:
    """
    Advanced Flexible ML: Train on one GSE and validate on another.
    """
    from custom_geo_parser import fetch_real_geo_matrix_with_genes
    from master_bioinfo_suite import MasterBioinfoPipeline

    logger.info(f"🚀 [Flexible ML] Training on {train_gse}, Validating on {test_gse}")
    
    # 1. Fetch Training Data
    train_counts, train_meta = fetch_real_geo_matrix_with_genes(train_gse)
    
    # 2. Fetch Validation Data
    test_counts, test_meta = fetch_real_geo_matrix_with_genes(test_gse)

    # 3. Initialize Pipeline
    out_dir = f"Run_FlexibleML_{train_gse}_vs_{test_gse}"
    pipeline = MasterBioinfoPipeline(out_dir=out_dir)
    pipeline.dataset_id = f"Train_{train_gse}_Test_{test_gse}"
    
    # Inject External Validation into Pipeline object before running ML
    pipeline.external_val_counts = test_counts
    pipeline.external_val_meta = test_meta

    # 4. Run Steps
    pipeline.run_pre_processing(custom_counts=train_counts, custom_meta=train_meta)
    pipeline.run_dea()
    pipeline.run_deg_heatmap()
    pipeline.run_wgcna_lite()
    pipeline.run_advanced_ml() # Will detect external_val
    pipeline.run_survival()
    pipeline.run_enrichment()
    
    # Intersect biomarkers for Venn
    train_sig = pipeline.sig_genes
    pipeline.run_venn_analysis(other_sig_lists=[test_counts.index.tolist()], labels=["Validation Cohort"])
    
    pipeline.generate_report()
    logger.info(f"Done. Results in {out_dir}")

def main():
    # Expand natural language to support disease synonyms
    DISEASE_MAP = {
        "肺腺癌": "GSE31210", 
        "LUAD": "GSE31210",
        "肺癌": "GSE31210",
        "乳腺癌": "GSE20685",
        "BRCA": "GSE20685"
    }

    result = parse_launcher_args()
    if result[0] is None:
        # Prompt user to check if they want flexible ML
        print("\n[AI Suggestion] Found multiple GSEs or specific intent? Type 'train:GSE1 test:GSE2' for flexible ML.")
        gse_list = interactive_prompt()
        if not gse_list:
            logger.error("No input.")
            sys.exit(1)
        use_simple = True
        no_notify = True
        dry_run = False
        args = None
    else:
        gse_list, _is_nl, args = result
        use_simple = getattr(args, "simple", False)
        no_notify = getattr(args, "no_notify", False)
        dry_run = getattr(args, "dry_run", False)

    # Check for direct disease names in command line
    raw_args = " ".join(sys.argv)
    for disease, gse in DISEASE_MAP.items():
        if disease in raw_args and gse not in gse_list:
            logger.info(f"Recognized intent for '{disease}', adding default dataset {gse}")
            gse_list.append(gse)

    if dry_run:
        logger.info(" [dry-run] GSE queue: %s", gse_list)
        return

    # Logical decision: If 2 GSEs provided and intent is ML, consider Flexible ML
    if len(gse_list) >= 2 and ("ml" in raw_args.lower() or "machine" in raw_args.lower() or "机器学习" in raw_args):
        logger.info("Detecting multi-GSE ML intent. Entering Flexible ML Mode.")
        run_workflow_flexible_ml(gse_list[0], gse_list[1], use_simple=use_simple)
    else:
        for i, gse_id in enumerate(gse_list):
            if i > 0: time.sleep(2)
            try:
                if use_simple: run_workflow_simple(gse_id)
                else: run_workflow_full(gse_id, no_notify=no_notify)
            except Exception as e:
                logger.exception("Failed %s: %s", gse_id, e); sys.exit(1)

    logger.info("All tasks completed.")

if __name__ == "__main__":
    import time
    main()
