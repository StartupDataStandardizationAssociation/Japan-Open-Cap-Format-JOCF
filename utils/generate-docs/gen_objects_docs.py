#!/usr/bin/env python3

import os
import glob
from schema_to_md.object_schema_to_md import generate

def main():
    # schema/objects配下の全ての.schema.jsonファイルを取得（サブディレクトリ含む）
    schema_dir = os.path.join(os.path.dirname(__file__), '../../schema/objects')
    schema_files = []
    for root, _, _ in os.walk(schema_dir):
        schema_files.extend(glob.glob(os.path.join(root, '*.schema.json')))

    # 各スキーマファイルに対してgenerate()を実行
    for schema_file in schema_files:
        print(f"Processing: {schema_file}")
        try:
            generate(schema_file)
            print(f"Successfully processed {schema_file}")
        except Exception as e:
            print(f"Error processing {schema_file}:")
            print(f"Error: {str(e)}")
            continue

if __name__ == "__main__":
    main()