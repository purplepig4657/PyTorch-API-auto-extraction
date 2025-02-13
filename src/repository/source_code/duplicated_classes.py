import os
import ast
from collections import defaultdict

def find_duplicate_classes(root_dir):
    class_names = defaultdict(list)  # 클래스 이름을 키로, 경로 리스트를 값으로 저장

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        tree = ast.parse(f.read(), filename=file_path)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                class_names[node.name].append(file_path)
                except Exception as e:
                    print(f"Error parsing {file_path}: {e}")

    # 중복 클래스 이름 출력
    duplicates = {name: paths for name, paths in class_names.items() if len(paths) > 1}
    if duplicates:
        print("Duplicate classes found:")
        for name, paths in duplicates.items():
            print(f"Class '{name}' is found in:")
            for path in paths:
                print(f"  - {path}")
        print(duplicates.keys())
    else:
        print("No duplicate classes found.")

if __name__ == "__main__":
    project_root = input("Enter the project root directory: ").strip()
    if os.path.isdir(project_root):
        find_duplicate_classes(project_root)
    else:
        print(f"Invalid directory: {project_root}")

