import os
import argparse
import tempfile
import zipfile
import shutil
from dockerfile_linter import DockerLinterRefactorer
from dockercompose_linter import ComposeLinter


def print_report(filepath, smells):
    relative_path = os.path.basename(filepath)
    print(f"\n--- 📄 Report for: {relative_path} ---")
    if not smells:
        print("✅ No smells detected.")
        return

    for smell_type, details in smells.items():
        print(f"  [⚠️ {smell_type}]")
        for detail in details:
            print(f"    - {detail}")
    print("--------------------------------" + "-" * len(relative_path))

def handle_dockerfile(tool, file_path, output_path):
    smells = tool.process_file(file_path)
    print_report(file_path, smells)
    if output_path:
        tool.refactor_and_save(output_path)

def handle_zip(tool, zip_path, output_dir):
    if output_dir and os.path.exists(output_dir) and not os.path.isdir(output_dir):
        print(f"❌ Error: Output path '{output_dir}' exists and is not a directory.")
        return
        
    temp_dir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        found = 0
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.lower() == "dockerfile":
                    found += 1
                    file_path = os.path.join(root, file)
                    smells = tool.process_file(file_path)
                    print_report(os.path.relpath(file_path, temp_dir), smells)
                    if output_dir:
                        refactored_path = os.path.join(output_dir, os.path.relpath(file_path, temp_dir))
                        tool.refactor_and_save(refactored_path)
        
        if found == 0: print("No files named 'Dockerfile' found in the ZIP archive.")

    finally:
        shutil.rmtree(temp_dir)

def handle_compose(tool, file_path):
    smells = tool.process_file(file_path)
    print_report(file_path, smells)
    print("\nNote: Auto-refactoring is not supported for Docker Compose files.")


def main():
    parser = argparse.ArgumentParser(
        description="Linter and Refactoring Tool for Docker and Docker Compose.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dockerfile", type=str, help="Path to a single Dockerfile.")
    group.add_argument("--zip", type=str, help="Path to a ZIP archive containing a project.")
    group.add_argument("--compose", type=str, help="Path to a docker-compose.yml file.")

    parser.add_argument(
        "--output", "-o", type=str,
        help="Output path for refactored file(s).\n"
             "For --dockerfile, this is a file path.\n"
             "For --zip, this is a directory path."
    )
    args = parser.parse_args()
    
    if args.dockerfile:
        tool = DockerLinterRefactorer()
        handle_dockerfile(tool, args.dockerfile, args.output)
    elif args.zip:
        tool = DockerLinterRefactorer()
        handle_zip(tool, args.zip, args.output)
    elif args.compose:
        tool = ComposeLinter()
        handle_compose(tool, args.compose)
    
if __name__ == "__main__":
    main()