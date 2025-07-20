# Production Packaging Guide

This directory collects scripts and notes for distributing the application.
It complements the instructions in `docs/PRODUCTION_INSTRUCTIONS.md`.

## Building a Stand‑alone Binary

Use [PyInstaller](https://pyinstaller.org/) to bundle the GUI and
its dependencies into a single executable:

```bash
pip install pyinstaller
pyinstaller --onefile -n chatgpt_gui src/ui/main.py
```

The resulting binary will appear in the `dist/` folder. Copy it to the
target machine along with any resource files used by the GUI. A basic
spec file is provided as `pyinstaller.spec`.

## Container Image

Alternatively the project can run inside a Docker container. A sample
`Dockerfile` is included that installs the Python dependencies and
launches the GUI or CLI.

```Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "-m", "src.ui.main"]
```

Build and run the image with:

```bash
docker build -t chatgpt-app .
docker run --rm -e OPENAI_API_KEY=sk-... chatgpt-app
```

Use environment variables such as `OPENAI_MODEL` or `AGENT_LOG_FILE`
to configure the application at runtime.
