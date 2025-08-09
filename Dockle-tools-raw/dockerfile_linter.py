from collections import defaultdict
import yaml
import re

class DockerLinterRefactorer:
    def __init__(self):
        self._reset()

    def _reset(self):
        self.smells = defaultdict(list)
        self._lines = []
        self._original_path = None

    def _analyze(self):
        has_healthcheck = False
        last_cmd = None

        for i, line in enumerate(self._lines):
            line_num = i + 1
            parts = line.strip().split()
            if not parts:
                continue
            
            cmd = parts[0].upper()

            if cmd == "FROM":
                if len(parts) > 1 and parts[1].endswith(":latest"):
                    self.smells["Use Pinned Versions"].append(f"Line {line_num}: Avoid using the ':latest' tag.")
            
            elif cmd == "ADD":
                self.smells["Prefer COPY"].append(f"Line {line_num}: 'ADD' is used. 'COPY' is generally preferred.")

            elif cmd == "USER" and len(parts) > 1 and parts[1].lower() == "root":
                self.smells["Avoid Root User"].append(f"Line {line_num}: Avoid running as the root user for security.")
                
            elif cmd == "HEALTHCHECK":
                has_healthcheck = True

            elif cmd == "RUN" and last_cmd == "RUN":
                self.smells["Inefficient Layering"].append(f"Line {line_num}: This RUN can be merged with the previous one.")

            last_cmd = cmd

        if not has_healthcheck:
            self.smells["Missing HEALTHCHECK"].append("The Dockerfile is missing a HEALTHCHECK instruction.")
            
        return self.smells

    def _refactor(self):
        refactored_lines = []
        i = 0
        while i < len(self._lines):
            line = self._lines[i] 
            line_strip = line.strip()
            
            if line_strip.upper().startswith("ADD "):
                line = line.replace(re.findall(r"^\s*ADD", line, re.IGNORECASE)[0], "COPY")
                refactored_lines.append(line)
                i += 1
                continue

            if line_strip.upper().startswith("RUN "):
                run_commands = [line_strip[4:].strip()]
                j = i + 1
                while j < len(self._lines):
                    next_line = self._lines[j].strip()
                    if next_line.upper().startswith("RUN "):
                        run_commands.append(next_line[4:].strip())
                        j += 1
                    else:
                        break
                
                if len(run_commands) > 1:
                    merged_command = "RUN " + " && \\\n    ".join(run_commands)
                    refactored_lines.append(merged_command + "\n")
                else:
                    refactored_lines.append(line)
                
                i = j 
            else:
                refactored_lines.append(line)
                i += 1
        
        if not any(line.upper().strip().startswith("HEALTHCHECK") for line in refactored_lines):
             refactored_lines.append("\n# TODO: Add a HEALTHCHECK instruction to check if your application is running correctly.\n")

        self._lines = "".join(refactored_lines)

    def process_file(self, dockerfile_path):
        self._reset()
        self._original_path = dockerfile_path
        with open(dockerfile_path, "r", encoding="utf-8") as f:
            self._lines = f.readlines()
        return self._analyze()

    def refactor_and_save(self, output_path):
        self._refactor()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(self._lines)
        print(f"✅ Refactored '{os.path.basename(self._original_path)}' saved to: {output_path}")