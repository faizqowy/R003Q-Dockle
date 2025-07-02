import zipfile
import tempfile
import os
import shutil
import re
import argparse
from egglog import Program


class DockerSmellEgglogAnalyzer:
    def __init__(self):
        self.program = Program()
        self._define_instructions()
        self._define_smell_rules()

    def _define_instructions(self):
        self.program.function("from", 2)
        self.program.function("run", 1)
        self.program.function("user", 1)
        self.program.function("copy", 2)
        self.program.function("add", 2)
        self.program.function("healthcheck", 1)
        self.program.function("expose", 1)
        self.program.function("workdir", 1)
        self.program.function("smell", 1)

    def _define_smell_rules(self):
        self.program.rewrite("avoid-latest", 'from(image, "latest")', 'smell("Avoid using :latest tag")')
        self.program.rewrite("avoid-root-user", 'user("root")', 'smell("Avoid using USER root")')
        self.program.rewrite("avoid-copy-dot", 'copy(".", "/app")', 'smell("Avoid COPY . /app")')
        self.program.rewrite("avoid-add", 'add(src, dst)', 'smell("Prefer COPY over ADD unless extracting archives")')
        self.program.rewrite("missing-healthcheck", 'from(image, tag)', 'smell("Missing HEALTHCHECK instruction")')

    def analyze_dockerfile(self, dockerfile_path: str):
        with open(dockerfile_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        for line in lines:
            if line.startswith("FROM"):
                match = re.match(r"FROM\s+(\S+):?(\S+)?", line)
                if match:
                    image = match.group(1)
                    tag = match.group(2) if match.group(2) else "latest"
                    self.program.expression(f'from("{image}", "{tag}")')
            elif line.startswith("RUN"):
                cmd = line[4:].strip().replace('"', '\\"')
                self.program.expression(f'run("{cmd}")')
            elif line.startswith("USER"):
                user = line[5:].strip()
                self.program.expression(f'user("{user}")')
            elif line.startswith("COPY"):
                parts = line.split()
                if len(parts) >= 3:
                    src, dst = parts[1], parts[2]
                    self.program.expression(f'copy("{src}", "{dst}")')
            elif line.startswith("ADD"):
                parts = line.split()
                if len(parts) >= 3:
                    src, dst = parts[1], parts[2]
                    self.program.expression(f'add("{src}", "{dst}")')
            elif line.startswith("HEALTHCHECK"):
                self.program.expression('healthcheck("exists")')
            elif line.startswith("WORKDIR"):
                self.program.expression(f'workdir("{line[8:].strip()}")')
            elif line.startswith("EXPOSE"):
                self.program.expression(f'expose("{line[7:].strip()}")')

    def analyze_project_zip(self, zip_path: str):
        temp_dir = tempfile.mkdtemp()
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file.lower() == "dockerfile":
                        dockerfile_path = os.path.join(root, file)
                        print(f"📦 Found Dockerfile: {dockerfile_path}")
                        self.analyze_dockerfile(dockerfile_path)

            self.program.run()
            results = self.program.query('smell(x)')
            return [res[0] for res in results]
        finally:
            shutil.rmtree(temp_dir)

    def analyze_single_dockerfile(self, path: str):
        print(f"📄 Analyzing Dockerfile: {path}")
        self.analyze_dockerfile(path)
        self.program.run()
        results = self.program.query('smell(x)')
        return [res[0] for res in results]


def main():
    parser = argparse.ArgumentParser(description="Egglog-based Docker Smell Analyzer")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--zip", help="Path to the project ZIP file")
    group.add_argument("--dockerfile", help="Path to a single Dockerfile")
    group.add_argument("--compose", help="(Not yet supported) Path to docker-compose.yml file")

    args = parser.parse_args()

    analyzer = DockerSmellEgglogAnalyzer()

    if args.zip:
        smells = analyzer.analyze_project_zip(args.zip)
    elif args.dockerfile:
        smells = analyzer.analyze_single_dockerfile(args.dockerfile)
    elif args.compose:
        print("🚧 Support for analyzing docker-compose.yml is not implemented yet.")
        return
    else:
        print("❌ No valid input source provided.")
        return

    print("\n=== Docker Smell Report ===")
    if smells:
        for smell in smells:
            print("🔍", smell)
    else:
        print("✅ No smells found! Great job!")


if __name__ == "__main__":
    main()
