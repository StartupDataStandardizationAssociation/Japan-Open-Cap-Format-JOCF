#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
スキーマローダークラス

JSONスキーマファイルの読み込み、インデックス作成、$ref解決を管理するクラスです。
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from jsonschema import RefResolver
from .config_manager import ConfigManager


class SchemaLoader:
    """
    スキーマローダークラス
    
    JSONスキーマファイルの読み込み、file_type/object_typeベースのインデックス作成、
    $ref解決のためのRefResolver構築を行います。
    """
    
    def __init__(self, config_manager: ConfigManager):
        """
        スキーマローダーの初期化
        
        Args:
            config_manager (ConfigManager): 設定管理インスタンス
        """
        self.config_manager = config_manager
        self.schema_root_path = config_manager.get_schema_root_path()
        self.file_type_map = {}
        self.object_type_map = {}
        self.ref_resolver = None
    
    def load_all_schemas(self) -> None:
        """
        すべてのスキーマファイルを読み込んでインデックスを作成
        
        schema/files/と schema/objects/配下のすべての.schema.jsonファイルを
        読み込み、file_type_map と object_type_map を構築します。
        
        Raises:
            SchemaLoadError: スキーマの読み込みに失敗した場合
        """
        # まず既存のマップをクリア
        self.file_type_map.clear()
        self.object_type_map.clear()
        
        # ファイルスキーマを読み込み
        self.load_file_schemas()
        
        # オブジェクトスキーマを読み込み
        self.load_object_schemas()
    
    def load_file_schemas(self) -> None:
        """
        ファイルスキーマを読み込む
        
        schema/files/配下のスキーマファイルを読み込み、
        file_type_mapを構築します。
        """
        files_dir = self.schema_root_path / "files"
        if not files_dir.exists():
            return
            
        for schema_file in files_dir.glob("*.schema.json"):
            try:
                schema = self._load_schema_file(schema_file)
                file_type = self._extract_file_type(schema)
                if file_type:
                    self.file_type_map[file_type] = schema
            except Exception:
                # エラーが発生した場合はスキップ（後で適切なエラーハンドリングを追加）
                continue
    
    def load_object_schemas(self) -> None:
        """
        オブジェクトスキーマを読み込む
        
        schema/objects/配下のスキーマファイルを読み込み、
        object_type_mapを構築します。
        """
        objects_dir = self.schema_root_path / "objects"
        if not objects_dir.exists():
            return
            
        # 再帰的にobjectsディレクトリ内の全ての.schema.jsonファイルを検索
        for schema_file in objects_dir.rglob("*.schema.json"):
            try:
                schema = self._load_schema_file(schema_file)
                object_type = self._extract_object_type(schema)
                if object_type:
                    self.object_type_map[object_type] = schema
            except Exception:
                # エラーが発生した場合はスキップ（後で適切なエラーハンドリングを追加）
                continue
    
    def get_file_schema(self, file_type: str) -> Optional[Dict[str, Any]]:
        """
        file_typeに対応するスキーマを取得
        
        Args:
            file_type (str): ファイルタイプ
            
        Returns:
            Optional[Dict[str, Any]]: 対応するスキーマ。見つからない場合はNone
        """
        return self.file_type_map.get(file_type)
    
    def get_object_schema(self, object_type: str) -> Optional[Dict[str, Any]]:
        """
        object_typeに対応するスキーマを取得
        
        Args:
            object_type (str): オブジェクトタイプ
            
        Returns:
            Optional[Dict[str, Any]]: 対応するスキーマ。見つからない場合はNone
        """
        return self.object_type_map.get(object_type)
    
    def get_ref_resolver(self) -> RefResolver:
        """
        $ref解決のためのRefResolverを取得
        
        Returns:
            RefResolver: 構築されたRefResolver
        """
        if self.ref_resolver is None:
            self.ref_resolver = self._build_ref_resolver()
        return self.ref_resolver
    
    def get_schema_by_id(self, schema_id: str) -> Optional[Dict[str, Any]]:
        """
        スキーマID($id)からスキーマを取得
        
        Args:
            schema_id (str): スキーマID
            
        Returns:
            Optional[Dict[str, Any]]: 対応するスキーマ。見つからない場合はNone
        """
        raise NotImplementedError("SchemaLoader.get_schema_by_id() is not implemented yet")
    
    def get_file_types(self) -> List[str]:
        """
        利用可能なfile_typeのリストを取得
        
        Returns:
            List[str]: file_typeのリスト
        """
        raise NotImplementedError("SchemaLoader.get_file_types() is not implemented yet")
    
    def get_object_types(self) -> List[str]:
        """
        利用可能なobject_typeのリストを取得
        
        Returns:
            List[str]: object_typeのリスト
        """
        raise NotImplementedError("SchemaLoader.get_object_types() is not implemented yet")
    
    def get_schema_info(self, file_type: Optional[str] = None, object_type: Optional[str] = None) -> Dict[str, Any]:
        """
        スキーマの詳細情報を取得
        
        Args:
            file_type (str, optional): ファイルタイプ
            object_type (str, optional): オブジェクトタイプ
            
        Returns:
            Dict[str, Any]: スキーマの詳細情報
        """
        raise NotImplementedError("SchemaLoader.get_schema_info() is not implemented yet")
    
    def preload_schemas(self, schema_paths: List[str]) -> None:
        """
        指定されたスキーマを事前に読み込む
        
        Args:
            schema_paths (List[str]): 読み込むスキーマファイルのパスリスト
        """
        raise NotImplementedError("SchemaLoader.preload_schemas() is not implemented yet")
    
    def clear_cache(self) -> None:
        """
        スキーマキャッシュをクリア
        """
        raise NotImplementedError("SchemaLoader.clear_cache() is not implemented yet")
    
    def _load_schema_file(self, schema_path: Path) -> Dict[str, Any]:
        """
        スキーマファイルを読み込む（内部メソッド）
        
        Args:
            schema_path (Path): スキーマファイルのパス
            
        Returns:
            Dict[str, Any]: 読み込まれたスキーマ
            
        Raises:
            SchemaLoadError: ファイルの読み込みに失敗した場合
        """
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _register_file_schema(self, schema: Dict[str, Any], schema_path: Path) -> None:
        """
        ファイルスキーマを登録する（内部メソッド）
        
        Args:
            schema (Dict[str, Any]): 登録するスキーマ
            schema_path (Path): スキーマファイルのパス
        """
        raise NotImplementedError("SchemaLoader._register_file_schema() is not implemented yet")
    
    def _register_object_schema(self, schema: Dict[str, Any], schema_path: Path) -> None:
        """
        オブジェクトスキーマを登録する（内部メソッド）
        
        Args:
            schema (Dict[str, Any]): 登録するスキーマ
            schema_path (Path): スキーマファイルのパス
        """
        raise NotImplementedError("SchemaLoader._register_object_schema() is not implemented yet")
    
    def _build_ref_resolver(self) -> RefResolver:
        """
        RefResolverを構築する（内部メソッド）
        
        Returns:
            RefResolver: 構築されたRefResolver
        """
        # スキーマストアを構築（全てのスキーマを$idをキーとして格納）
        store = {}
        
        # ファイルスキーマをストアに追加
        for schema in self.file_type_map.values():
            schema_id = schema.get("$id")
            if schema_id:
                store[schema_id] = schema
        
        # オブジェクトスキーマをストアに追加
        for schema in self.object_type_map.values():
            schema_id = schema.get("$id")
            if schema_id:
                store[schema_id] = schema
                
        # その他のスキーマファイル（types, primitives, enums）も読み込む
        self._load_additional_schemas_for_resolver(store)
        
        # RefResolverを作成
        base_uri = "https://jocf.startupstandard.org/jocf/main/"
        return RefResolver(base_uri, None, store=store)
    
    def _extract_file_type(self, schema: Dict[str, Any]) -> Optional[str]:
        """
        スキーマからfile_typeを抽出する（内部メソッド）
        
        Args:
            schema (Dict[str, Any]): 対象スキーマ
            
        Returns:
            Optional[str]: file_type。見つからない場合はNone
        """
        # schema直下のfile_typeをチェック
        if "file_type" in schema:
            return schema["file_type"]
        
        # properties内のfile_typeのconst値をチェック
        properties = schema.get("properties", {})
        file_type_prop = properties.get("file_type", {})
        if "const" in file_type_prop:
            return file_type_prop["const"]
        
        return None
    
    def _extract_object_type(self, schema: Dict[str, Any]) -> Optional[str]:
        """
        スキーマからobject_typeを抽出する（内部メソッド）
        
        Args:
            schema (Dict[str, Any]): 対象スキーマ
            
        Returns:
            Optional[str]: object_type。見つからない場合はNone
        """
        # schema直下のobject_typeをチェック
        if "object_type" in schema:
            return schema["object_type"]
        
        # properties内のobject_typeのconst値をチェック
        properties = schema.get("properties", {})
        object_type_prop = properties.get("object_type", {})
        if "const" in object_type_prop:
            return object_type_prop["const"]
        
        return None
    
    def _find_schema_files(self, directory: Path, pattern: str = "*.schema.json") -> List[Path]:
        """
        指定されたディレクトリからスキーマファイルを検索する（内部メソッド）
        
        Args:
            directory (Path): 検索対象ディレクトリ
            pattern (str): ファイル名パターン
            
        Returns:
            List[Path]: 見つかったスキーマファイルのリスト
        """
        if not directory.exists():
            return []
        return list(directory.rglob(pattern))
    
    def _load_additional_schemas_for_resolver(self, store: Dict[str, Dict[str, Any]]) -> None:
        """
        RefResolver用に追加のスキーマ（types, primitives, enums）を読み込む
        
        Args:
            store (Dict[str, Dict[str, Any]]): スキーマストア
        """
        # types, primitives, enumsディレクトリからスキーマを読み込み
        additional_dirs = ["types", "primitives", "enums"]
        
        for dir_name in additional_dirs:
            schema_dir = self.schema_root_path / dir_name
            if schema_dir.exists():
                for schema_file in schema_dir.rglob("*.schema.json"):
                    try:
                        schema = self._load_schema_file(schema_file)
                        schema_id = schema.get("$id")
                        if schema_id:
                            store[schema_id] = schema
                    except Exception:
                        # エラーが発生した場合はスキップ
                        continue
    
    def __str__(self) -> str:
        """
        文字列表現を返す
        
        Returns:
            str: スキーマローダーの文字列表現
        """
        raise NotImplementedError("SchemaLoader.__str__() is not implemented yet")
    
    def __repr__(self) -> str:
        """
        デバッグ用の文字列表現を返す
        
        Returns:
            str: デバッグ用の文字列表現
        """
        raise NotImplementedError("SchemaLoader.__repr__() is not implemented yet")