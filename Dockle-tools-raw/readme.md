## How to use

### Install Library
```
pip install -r requirements.txt
```

### Run Tools

Run for whole project. The folder must include dockerfile/dockercompose and dockerfile in order for this to works

```bash

python docker_smell_analyzer.py --zip ./path/to/your_project.zip
```

Run for single dockerfile

```bash
python docker_smell_analyzer.py --dockerfile ./path/to/Dockerfile
```

Run for single dockercompose file
```bash
python docker_smell_analyzer.py --compose ./path/to/docker-compose.yml
```

## General Idea
The script uses the Egglog logic engine to detect common Dockerfile anti-patterns (called "smells") by:

1. Parsing Dockerfiles
It scans each line of the Dockerfile and converts instructions like FROM, USER, COPY, etc. into logical expressions.

2. Defining Smell Rules
Built-in Egglog rules detect bad practices like:

    - Using the :latest tag

    - Running as USER root

    - Using ADD instead of COPY

    - Omitting a HEALTHCHECK

3. Analyzing with Egglog
The script feeds all parsed instructions into Egglog, which applies the rules and flags any matching smells.

4. Returning Results
Detected smells are printed in a readable format.

The script can analyze a ZIP of projects, a single Dockerfile, or (future) a docker-compose.yml file.

## Future Improvement

This tool is a work in progress and will continue to be improved over time. Planned enhancements include:

1. 🛠 Support for analyzing docker-compose.yml files

2. 🧼 Automatic suggestions and fixes for detected smells

3. 📄 JSON/HTML report output

4. ⚙️ CI/CD integration for DevOps pipelines

Contributions, ideas, and feedback are welcome to help make this tool even better!