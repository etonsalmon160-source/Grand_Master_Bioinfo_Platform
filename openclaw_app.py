#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OpenClaw UI placeholder and configuration helper.
This is a simplified UI wrapper intended for the Python-first release path.
"""

import os
import json
import requests
import streamlit as st

# Local config path
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "openclaw_config.json")


def _load_config() -> dict:
    if os.path.exists(_CONFIG_PATH):
        try:
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {}


def _save_config(cfg: dict) -> None:
    try:
        with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def main():
    st.set_page_config(page_title="OpenClaw 生信工作流", layout="wide")
    cfg = _load_config()
    with st.sidebar.expander("⚙️ 模型与报告配置", expanded=True):
        api_url = st.text_input(
            "论文级报告解读 API URL", value=cfg.get("interpret_url", "")
        )
        api_key = st.text_input(
            "API Key / Token", value=cfg.get("api_key", ""), type="password"
        )
        report_level = st.selectbox(
            "报告级别",
            ["标准报告", "论文初稿（推荐）"],
            index=1 if cfg.get("report_level", "paper_draft") == "paper_draft" else 0,
        )
        save_to_config = st.checkbox(
            "保存到本地配置文件（openclaw_config.json）", value=True
        )
        if st.button("💾 保存配置", use_container_width=True):
            interpret_url = str(api_url or "").strip()
            key = str(api_key or "").strip()
            level = (
                "paper_draft"
                if report_level.startswith("论文") or report_level == "论文初稿（推荐）"
                else "standard"
            )
            if save_to_config:
                cfg["interpret_url"] = interpret_url
                cfg["api_key"] = key
                cfg["report_level"] = level
                _save_config(cfg)
                st.success("配置已保存，下次启动软件会自动读取。")
            else:
                st.success("配置已更新（未写入本地配置文件），将应用于当前会话环境。")
            os.environ["OPENCLAW_INTERPRET_URL"] = interpret_url
            os.environ["OPENCLAW_API_KEY"] = key
            os.environ["OPENCLAW_REPORT_LEVEL"] = level
        # 启动时绑定环境变量
        os.environ.setdefault("OPENCLAW_INTERPRET_URL", cfg.get("interpret_url", ""))
        os.environ.setdefault("OPENCLAW_API_KEY", cfg.get("api_key", ""))
        os.environ.setdefault(
            "OPENCLAW_REPORT_LEVEL", cfg.get("report_level", "paper_draft")
        )

    st.title("OpenClaw 生信工作流（简化 UI）")
    st.write("在此处可以测试 API、配置并启动工作流。实际工作流执行请在后端脚本中完成。")

    if st.button("🧪 测试 OpenClaw API"):
        url = str(cfg.get("interpret_url", "")).strip()
        key = str(cfg.get("api_key", "")).strip()
        if not url:
            st.error("请在上方输入 API URL。")
        else:
            headers = {}
            if key:
                headers["Authorization"] = f"Bearer {key}"
            try:
                resp = requests.get(url, headers=headers, timeout=5)
                st.info(f"HTTP {resp.status_code} {resp.reason}")
                st.code(resp.text[:2000])
            except Exception as e:
                st.error(f"请求失败：{e}")

    if st.button("🚀 启动工作流（占位）"):
        st.info("此处应调用实际工作流执行逻辑。")


if __name__ == "__main__":
    main()
