#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
型クラス定義

ObjectType、FileType、SchemaIdなどの型安全クラスを定義します。
"""

from typing import Any, Type


class _TypedString:
    """文字列をラップする型安全クラスの基底クラス"""
    
    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError(f"{self.__class__.__name__} value must be a string")
        if not value:
            raise ValueError(f"{self.__class__.__name__} value cannot be empty")
        self._value = value
    
    @property
    def value(self) -> str:
        """内部の文字列値を取得"""
        return self._value
    
    def __str__(self) -> str:
        return self._value
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._value!r})"


class ObjectType(_TypedString):
    """オブジェクトタイプを表現する型安全クラス"""
    pass


class FileType(_TypedString):
    """ファイルタイプを表現する型安全クラス"""
    pass


class SchemaId(_TypedString):
    """スキーマIDを表現する型安全クラス"""
    pass