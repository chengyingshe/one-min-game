FROM python:3.11-slim
RUN pip install --no-cache-dir pygame pyyaml pillow
WORKDIR /game
COPY run_game.py /usr/local/bin/run_game.py
ENTRYPOINT ["python", "/usr/local/bin/run_game.py"]
