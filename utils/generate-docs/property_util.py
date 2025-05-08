#!/usr/bin/env python3

from typing import Dict, Any
from schema_id_util import extract_ref_relative_path, extract_file_name_wo_extension

def get_property_type(prop: Dict[str, Any]) -> str:
    """
    プロパティの型情報を取得する
    """
    if 'type' in prop:
        if prop['type'] == 'array' and 'items' in prop:
            # array型の場合
            items = prop['items']
            if 'oneOf' in items:
                # oneOfの場合は$refの値を列挙
                refs = []
                for item in items['oneOf']:
                    if '$ref' in item:
                        ref_file_name = extract_file_name_wo_extension(item['$ref'])
                        ref_relative_path = extract_ref_relative_path(item['$ref'])
                        # ref_file_nameとref_relative_pathをMarkdown形式で追加
                        refs.append(f"[{ref_file_name}]({ref_relative_path})")
                return f"one of: <br> - {'<br> - '.join(refs)}"
            # 単純な$refの場合
            if '$ref' in items:
                ref_file_name = extract_file_name_wo_extension(items['$ref'])
                ref_relative_path = extract_ref_relative_path(items['$ref'])
                return f"array of [{ref_file_name}]({ref_relative_path})"
            # それ以外の型の場合はitemsの型を取得
            return f"array of {get_property_type(items)}"
        # それ以外の型の場合
        return prop['type']
    elif 'const' in prop:
        return f"const ({prop['const']})"
    elif '$ref' in prop:
        ref_file_name = extract_file_name_wo_extension(prop['$ref'])
        ref_relative_path = extract_ref_relative_path(prop['$ref'])
        return f"[{ref_file_name}]({ref_relative_path})"
    return 'unknown'