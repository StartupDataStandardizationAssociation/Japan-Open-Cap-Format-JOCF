#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
型クラスのテスト

ObjectType、FileType、SchemaIdクラスのテストを行います。
"""

import pytest
from validator.types import ObjectType, FileType, SchemaId


class TestObjectType:
    """ObjectTypeクラスのテスト"""

    def test_create_object_type(self):
        """ObjectTypeを正常に作成できることをテスト"""
        obj_type = ObjectType("StockClass")
        assert str(obj_type) == "StockClass"
        assert obj_type.value == "StockClass"

    def test_object_type_equality(self):
        """ObjectTypeの等価性をテスト"""
        obj_type1 = ObjectType("StockClass")
        obj_type2 = ObjectType("StockClass")
        obj_type3 = ObjectType("Transaction")

        assert obj_type1 == obj_type2
        assert obj_type1 != obj_type3

    def test_object_type_hash(self):
        """ObjectTypeがハッシュ可能であることをテスト"""
        obj_type1 = ObjectType("StockClass")
        obj_type2 = ObjectType("StockClass")

        # 辞書のキーとして使用できる
        type_dict = {obj_type1: "test"}
        assert type_dict[obj_type2] == "test"

    def test_object_type_empty_string(self):
        """空文字列でObjectTypeを作成した場合のテスト"""
        with pytest.raises(ValueError, match="ObjectType value cannot be empty"):
            ObjectType("")

    def test_object_type_none(self):
        """NoneでObjectTypeを作成した場合のテスト"""
        with pytest.raises(TypeError):
            ObjectType(None)


class TestFileType:
    """FileTypeクラスのテスト"""

    def test_create_file_type(self):
        """FileTypeを正常に作成できることをテスト"""
        file_type = FileType("OCF_TRANSACTIONS_FILE")
        assert str(file_type) == "OCF_TRANSACTIONS_FILE"
        assert file_type.value == "OCF_TRANSACTIONS_FILE"

    def test_file_type_equality(self):
        """FileTypeの等価性をテスト"""
        file_type1 = FileType("OCF_TRANSACTIONS_FILE")
        file_type2 = FileType("OCF_TRANSACTIONS_FILE")
        file_type3 = FileType("OCF_STOCK_CLASSES_FILE")

        assert file_type1 == file_type2
        assert file_type1 != file_type3

    def test_file_type_hash(self):
        """FileTypeがハッシュ可能であることをテスト"""
        file_type1 = FileType("OCF_TRANSACTIONS_FILE")
        file_type2 = FileType("OCF_TRANSACTIONS_FILE")

        # 辞書のキーとして使用できる
        type_dict = {file_type1: "test"}
        assert type_dict[file_type2] == "test"

    def test_file_type_empty_string(self):
        """空文字列でFileTypeを作成した場合のテスト"""
        with pytest.raises(ValueError, match="FileType value cannot be empty"):
            FileType("")


class TestSchemaId:
    """SchemaIdクラスのテスト"""

    def test_create_schema_id(self):
        """SchemaIdを正常に作成できることをテスト"""
        schema_id = SchemaId(
            "https://jocf.startupstandard.org/jocf/main/schema/objects/StockClass.schema.json"
        )
        expected = "https://jocf.startupstandard.org/jocf/main/schema/objects/StockClass.schema.json"
        assert str(schema_id) == expected
        assert schema_id.value == expected

    def test_schema_id_equality(self):
        """SchemaIdの等価性をテスト"""
        schema_id1 = SchemaId(
            "https://jocf.startupstandard.org/jocf/main/schema/objects/StockClass.schema.json"
        )
        schema_id2 = SchemaId(
            "https://jocf.startupstandard.org/jocf/main/schema/objects/StockClass.schema.json"
        )
        schema_id3 = SchemaId(
            "https://jocf.startupstandard.org/jocf/main/schema/objects/Transaction.schema.json"
        )

        assert schema_id1 == schema_id2
        assert schema_id1 != schema_id3

    def test_schema_id_hash(self):
        """SchemaIdがハッシュ可能であることをテスト"""
        schema_id1 = SchemaId(
            "https://jocf.startupstandard.org/jocf/main/schema/objects/StockClass.schema.json"
        )
        schema_id2 = SchemaId(
            "https://jocf.startupstandard.org/jocf/main/schema/objects/StockClass.schema.json"
        )

        # 辞書のキーとして使用できる
        id_dict = {schema_id1: "test"}
        assert id_dict[schema_id2] == "test"

    def test_schema_id_empty_string(self):
        """空文字列でSchemaIdを作成した場合のテスト"""
        with pytest.raises(ValueError, match="SchemaId value cannot be empty"):
            SchemaId("")


class TestTypeInteroperability:
    """型クラス間の相互運用性テスト"""

    def test_different_types_not_equal(self):
        """異なる型クラス同士は等価でないことをテスト"""
        obj_type = ObjectType("StockClass")
        file_type = FileType("StockClass")
        schema_id = SchemaId("StockClass")

        assert obj_type != file_type
        assert obj_type != schema_id
        assert file_type != schema_id
