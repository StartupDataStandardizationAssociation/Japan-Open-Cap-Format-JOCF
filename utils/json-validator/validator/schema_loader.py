#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
スキーマローダークラス

JSONスキーマファイルの読み込み、インデックス作成、$ref解決を管理するクラスです。
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, cast
from referencing import Registry
from referencing.jsonschema import DRAFT202012
from .config_manager import ConfigManager
from .types import ObjectType, FileType, SchemaId


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
        self.logger = logging.getLogger('json_validator.schema_loader')
        self.config_manager = config_manager
        self.schema_root_path = config_manager.get_schema_root_path()
        self.file_type_map: Dict[FileType, Dict[str, Any]] = {}
        self.object_type_map: Dict[ObjectType, Dict[str, Any]] = {}
        self.registry: Optional[Registry] = None
        
        self.logger.debug(f"SchemaLoader initialized with root path: {self.schema_root_path}")
    
    def load_all_schemas(self) -> None:
        """
        すべてのスキーマファイルを読み込んでインデックスを作成
        
        schema/files/と schema/objects/配下のすべての.schema.jsonファイルを
        読み込み、file_type_map と object_type_map を構築します。
        
        Raises:
            SchemaLoadError: スキーマの読み込みに失敗した場合
        """
        self.logger.debug("Starting to load all schemas")
        
        # まず既存のマップをクリア
        self.file_type_map.clear()
        self.object_type_map.clear()
        self.logger.debug("Cleared existing schema maps")
        
        # ファイルスキーマを読み込み
        self.load_file_schemas()
        
        # オブジェクトスキーマを読み込み
        self.load_object_schemas()
        
        self.logger.debug(f"Schema loading completed. Files: {len(self.file_type_map)}, Objects: {len(self.object_type_map)}")
    
    def load_file_schemas(self) -> None:
        """
        ファイルスキーマを読み込む
        
        schema/files/配下のスキーマファイルを読み込み、
        file_type_mapを構築します。
        """
        files_dir = self.schema_root_path / "files"
        self.logger.debug(f"Loading file schemas from: {files_dir}")
        
        if not files_dir.exists():
            self.logger.debug(f"Files directory does not exist: {files_dir}")
            return
            
        schema_files = list(files_dir.glob("*.schema.json"))
        self.logger.debug(f"Found {len(schema_files)} file schema files")
        
        for schema_file in schema_files:
            try:
                self.logger.debug(f"Loading file schema: {schema_file}")
                schema = self._load_schema_file(schema_file)
                self._register_file_schema(schema)
                self.logger.debug(f"Successfully loaded file schema: {schema_file}")
            except Exception as e:
                self.logger.debug(f"Failed to load file schema {schema_file}: {e}")
                continue
    
    def load_object_schemas(self) -> None:
        """
        オブジェクトスキーマを読み込む
        
        schema/objects/配下のスキーマファイルを読み込み、
        object_type_mapを構築します。
        """
        objects_dir = self.schema_root_path / "objects"
        self.logger.debug(f"Loading object schemas from: {objects_dir}")
        
        if not objects_dir.exists():
            self.logger.debug(f"Objects directory does not exist: {objects_dir}")
            return
            
        # 再帰的にobjectsディレクトリ内の全ての.schema.jsonファイルを検索
        schema_files = list(objects_dir.rglob("*.schema.json"))
        self.logger.debug(f"Found {len(schema_files)} object schema files")
        
        for schema_file in schema_files:
            try:
                self.logger.debug(f"Loading object schema: {schema_file}")
                schema = self._load_schema_file(schema_file)
                self._register_object_schema(schema)
                self.logger.debug(f"Successfully loaded object schema: {schema_file}")
            except Exception as e:
                self.logger.debug(f"Failed to load object schema {schema_file}: {e}")
                continue
    
    def get_file_schema(self, file_type: FileType) -> Optional[Dict[str, Any]]:
        """
        file_typeに対応するスキーマを取得
        
        Args:
            file_type (FileType): ファイルタイプ
            
        Returns:
            Optional[Dict[str, Any]]: 対応するスキーマ。見つからない場合はNone
        """
        return self.file_type_map.get(file_type)
    
    def get_object_schema(self, object_type: ObjectType) -> Optional[Dict[str, Any]]:
        """
        object_typeに対応するスキーマを取得
        
        Args:
            object_type (ObjectType): オブジェクトタイプ
            
        Returns:
            Optional[Dict[str, Any]]: 対応するスキーマ。見つからない場合はNone
        """
        return self.object_type_map.get(object_type)
    
    def get_registry(self) -> Registry:
        """
        $ref解決のためのRegistryを取得
        
        Returns:
            Registry: 構築されたRegistry
        """
        if self.registry is None:
            self.logger.debug("Building Registry")
            self.registry = self._build_registry()
            self.logger.debug("Registry built successfully")
        # この時点でself.registryは確実にRegistryインスタンス
        assert self.registry is not None
        return self.registry
    
    def get_schema_by_id(self, schema_id: SchemaId) -> Optional[Dict[str, Any]]:
        """
        スキーマID($id)からスキーマを取得
        
        Args:
            schema_id (SchemaId): スキーマID
            
        Returns:
            Optional[Dict[str, Any]]: 対応するスキーマ。見つからない場合はNone
        """
        # Registryから検索（全スキーマが含まれている）
        registry = self.get_registry()
        try:
            resource = registry.get_or_retrieve(schema_id.value)
            return resource.value.contents
        except Exception:
            return None
    
    def get_file_types(self) -> List[FileType]:
        """
        利用可能なfile_typeのリストを取得
        
        Returns:
            List[FileType]: file_typeのリスト
        """
        return list(self.file_type_map.keys())
    
    def get_object_types(self) -> List[ObjectType]:
        """
        利用可能なobject_typeのリストを取得
        
        Returns:
            List[ObjectType]: object_typeのリスト
        """
        return list(self.object_type_map.keys())
    
    def has_object_schema(self, object_type: ObjectType) -> bool:
        """
        指定されたobject_typeのスキーマが存在するかを確認
        
        Args:
            object_type (ObjectType): オブジェクトタイプ
            
        Returns:
            bool: スキーマが存在する場合True
        """
        return object_type in self.object_type_map
    
    
    def preload_schemas(self, schema_paths: List[str]) -> None:
        """
        指定されたスキーマを事前に読み込む
        
        Args:
            schema_paths (List[str]): 読み込むスキーマファイルのパスリスト
        """
        # 現在の実装では、load_all_schemas()ですべてをロードするため、
        # 特定のスキーマのみをプリロードする機能は将来の実装用のプレースホルダー
        for schema_path in schema_paths:
            full_path = self.schema_root_path / schema_path
            if full_path.exists():
                try:
                    schema = self._load_schema_file(full_path)
                    # 適切なマップに追加（register メソッドを使用）
                    self._register_file_schema(schema)
                    self._register_object_schema(schema)
                except Exception:
                    # エラーが発生した場合はスキップ
                    continue
    
    def clear_cache(self) -> None:
        """
        スキーマキャッシュをクリア
        """
        self.registry = None
    
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
        self.logger.debug(f"Reading schema file: {schema_path}")
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        self.logger.debug(f"Successfully parsed JSON from: {schema_path}")
        return cast(Dict[str, Any], schema)
    
    def _register_file_schema(self, schema: Dict[str, Any]) -> None:
        """
        ファイルスキーマを登録する（内部メソッド）
        
        Args:
            schema (Dict[str, Any]): 登録するスキーマ
        """
        file_type_str = self._extract_file_type(schema)
        if file_type_str:
            try:
                file_type = FileType(file_type_str)
                self.file_type_map[file_type] = schema
                self.logger.debug(f"Registered file schema with type: {file_type}")
            except (TypeError, ValueError) as e:
                self.logger.debug(f"Failed to create FileType from '{file_type_str}': {e}")
        else:
            self.logger.debug(f"Could not extract file_type from schema: {schema.get('$id', 'unknown')}")
    
    def _register_object_schema(self, schema: Dict[str, Any]) -> None:
        """
        オブジェクトスキーマを登録する（内部メソッド）
        
        Args:
            schema (Dict[str, Any]): 登録するスキーマ
        """
        object_type_str = self._extract_object_type(schema)
        if object_type_str:
            try:
                object_type = ObjectType(object_type_str)
                self.object_type_map[object_type] = schema
                self.logger.debug(f"Registered object schema with type: {object_type}")
            except (TypeError, ValueError) as e:
                self.logger.debug(f"Failed to create ObjectType from '{object_type_str}': {e}")
        else:
            self.logger.debug(f"Could not extract object_type from schema: {schema.get('$id', 'unknown')}")
    
    def _build_registry(self) -> Registry:
        """
        Registryを構築する（内部メソッド）
        
        Returns:
            Registry: 構築されたRegistry
        """
        self.logger.debug("Building Registry")
        
        # Registryを作成
        registry = Registry()
        
        # ファイルスキーマをRegistryに追加
        file_schema_count = 0
        for schema in self.file_type_map.values():
            schema_id = schema.get("$id")
            if schema_id:
                resource = DRAFT202012.create_resource(schema)
                registry = registry.with_resource(schema_id, resource)
                file_schema_count += 1
                self.logger.debug(f"Added file schema to registry: {schema_id}")
        
        # オブジェクトスキーマをRegistryに追加
        object_schema_count = 0
        for schema in self.object_type_map.values():
            schema_id = schema.get("$id")
            if schema_id:
                resource = DRAFT202012.create_resource(schema)
                registry = registry.with_resource(schema_id, resource)
                object_schema_count += 1
                self.logger.debug(f"Added object schema to registry: {schema_id}")
                
        # その他のスキーマファイル（types, primitives, enums）も読み込む
        registry = self._load_additional_schemas_for_registry(registry)
        
        self.logger.debug(f"Registry created with {file_schema_count} file schemas and {object_schema_count} object schemas")
        return registry
    
    def _extract_file_type(self, schema: Dict[str, Any]) -> Optional[str]:
        """
        スキーマからfile_typeを抽出する（内部メソッド）
        
        Args:
            schema (Dict[str, Any]): 対象スキーマ
            
        Returns:
            Optional[str]: file_type。見つからない場合はNone
        """
        # schema直下のfile_typeのconst値をチェック
        if "file_type" in schema:
            file_type_prop = schema["file_type"]
            if "const" in file_type_prop:
                # const値が存在する場合はそれを返す
                return file_type_prop["const"] if isinstance(file_type_prop["const"], str) else None
            return None

        # properties内のfile_typeのconst値をチェック
        properties = schema.get("properties", {})
        file_type_prop = properties.get("file_type", {})
        if "const" in file_type_prop:       
            # const値が存在する場合はそれを返す
                return file_type_prop["const"] if isinstance(file_type_prop["const"], str) else None
        
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
            object_type_prop = schema["object_type"]
            if "const" in object_type_prop:
                # const値が存在する場合はそれを返す
                return object_type_prop["const"] if isinstance(object_type_prop["const"], str) else None
            return None
        
        # properties内のobject_typeのconst値をチェック
        properties = schema.get("properties", {})
        object_type_prop = properties.get("object_type", {})
        if "const" in object_type_prop:
            # const値が存在する場合はそれを返す
            return object_type_prop["const"] if isinstance(object_type_prop["const"], str) else None
        
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
    
    def _load_additional_schemas_for_registry(self, registry: Registry) -> Registry:
        """
        Registry用に追加のスキーマ（types, primitives, enums）を読み込む
        
        Args:
            registry (Registry): スキーマRegistry
            
        Returns:
            Registry: 更新されたRegistry
        """
        # types, primitives, enumsディレクトリからスキーマを読み込み
        additional_dirs = ["types", "primitives", "enums"]
        
        for dir_name in additional_dirs:
            schema_dir = self.schema_root_path / dir_name
            self.logger.debug(f"Loading additional schemas from: {schema_dir}")
            
            if schema_dir.exists():
                schema_files = list(schema_dir.rglob("*.schema.json"))
                self.logger.debug(f"Found {len(schema_files)} additional schema files in {dir_name}")
                
                for schema_file in schema_files:
                    try:
                        self.logger.debug(f"Loading additional schema: {schema_file}")
                        schema = self._load_schema_file(schema_file)
                        schema_id = schema.get("$id")
                        if schema_id:
                            resource = DRAFT202012.create_resource(schema)
                            registry = registry.with_resource(schema_id, resource)
                            self.logger.debug(f"Added additional schema to registry: {schema_id}")
                    except Exception as e:
                        self.logger.debug(f"Failed to load additional schema {schema_file}: {e}")
                        continue
            else:
                self.logger.debug(f"Additional schema directory does not exist: {schema_dir}")
        
        return registry
    
    def __str__(self) -> str:
        """
        文字列表現を返す
        
        Returns:
            str: スキーマローダーの文字列表現
        """
        return f"SchemaLoader(files={len(self.file_type_map)}, objects={len(self.object_type_map)}, root={self.schema_root_path})"
    
    def __repr__(self) -> str:
        """
        デバッグ用の文字列表現を返す
        
        Returns:
            str: デバッグ用の文字列表現
        """
        return f"SchemaLoader(config_manager={self.config_manager!r}, schema_root_path={self.schema_root_path!r})"