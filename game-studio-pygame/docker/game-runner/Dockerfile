FROM python:3.11-slim
RUN sed -i 's|deb.debian.org|mirrors.cloud.tencent.com|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || true && \
    apt-get update && apt-get install -y --no-install-recommends fontconfig fonts-noto-cjk && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -i https://mirrors.cloud.tencent.com/pypi/simple/ --trusted-host mirrors.cloud.tencent.com pygame pyyaml pillow
WORKDIR /game
COPY run_game.py /usr/local/bin/run_game.py
ENTRYPOINT ["python", "/usr/local/bin/run_game.py"]
