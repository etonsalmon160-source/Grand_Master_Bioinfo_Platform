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
    从自然语言描述中抽取所有 GSE 编号。
    例如："分析肺腺癌 GSE31210 和 GSE30219" -> ['GSE31210', 'GSE30219']
    """
    if not text or not text.strip():
        return []
    found = GSE_PATTERN.findall(text)
    # 去重且保持顺序
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
        help="使用简化流程（不转移 D 盘、不销毁临时目录，结果留在当前目录 Run_<GSE>_Results）",
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


def main():
    result = parse_launcher_args()
    if result[0] is None:
        # 交互模式
        gse_list = interactive_prompt()
        if not gse_list:
            logger.error("未输入有效内容或未识别到 GSE 编号。")
            sys.exit(1)
        # 交互模式默认用简化流程，避免动 D 盘
        use_simple = True
        no_notify = True
        dry_run = False
    else:
        gse_list, _is_nl, args = result
        use_simple = getattr(args, "simple", False)
        no_notify = getattr(args, "no_notify", False)
        dry_run = getattr(args, "dry_run", False)

    if dry_run:
        logger.info(" [dry-run] 将依次运行 %d 个数据集: %s", len(gse_list), gse_list)
        return

    logger.info("将依次运行 %d 个数据集: %s", len(gse_list), gse_list)

    for i, gse_id in enumerate(gse_list):
        if i > 0:
            logger.info("休眠 5 秒后处理下一个任务...")
            import time
            time.sleep(5)
        try:
            if use_simple:
                run_workflow_simple(gse_id)
            else:
                run_workflow_full(gse_id, no_notify=no_notify)
        except Exception as e:
            logger.exception("处理 %s 时失败: %s", gse_id, e)
            sys.exit(1)

    logger.info("全部任务完成。")


if __name__ == "__main__":
    main()
