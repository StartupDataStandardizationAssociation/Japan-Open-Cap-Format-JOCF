#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
設定管理モジュール（後方互換性用）

新しいConfigManagerクラスを使用するための互換性レイヤーです。
実際の実装は config_manager.py に移動されました。
"""

# 新しいConfigManagerクラスをインポート
from .config_manager import (
    ConfigManager,
    get_config_manager,
    reset_config_manager,
    load_config_from_dict,
)

from pathlib import Path
from typing import Dict, Any, Optional


class Config(ConfigManager):
    """後方互換性のためのエイリアス"""

    pass


def get_config() -> ConfigManager:
    """
    グローバル設定インスタンスを取得（後方互換性用）

    Returns:
        ConfigManager: 設定管理インスタンス
    """
    return get_config_manager()


def reset_config():
    """グローバル設定インスタンスをリセット（後方互換性用）"""
    reset_config_manager()
