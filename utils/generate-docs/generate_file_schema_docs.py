#!/usr/bin/env python3

import os
import glob
import subprocess

def main():
    # schema/files/配下の全ての.schema.jsonファイルを取得
    schema_dir = os.path.join(os.path.dirname(__file__), '../../schema/files')
    schema_files = glob.glob(os.path.join(schema_dir, '*.schema.json'))

    # 各スキーマファイルに対してFileSchemaToMd.pyを実行
    for schema_file in schema_files:
        print(f"Processing: {schema_file}")
        try:
            # FileSchemaToMd.pyを実行
            result = subprocess.run(
                ['python3', 'utils/generate-docs/FileSchemaToMd.py', schema_file],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"Successfully processed {schema_file}")
            
        except subprocess.CalledProcessError as e:
            print(f"Error processing {schema_file}:")
            print(f"Error output: {e.stderr}")
            continue

if __name__ == "__main__":
    main()