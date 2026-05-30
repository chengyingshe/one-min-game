.PHONY: sdk-test mcp-server mcp-test templates template-test-flappy template-test-shooter template-test-platformer test-all clean playground-up playground-down playground-build

# SDK tests
sdk-test:
	cd runtime/pygame-sdk && python -m pytest tests/ -v

# MCP server
mcp-server:
	cd apps/mcp-server && pip install -e .

mcp-test:
	cd apps/mcp-server && python -m pytest tests/ -v

# Template tests
templates: template-test-flappy template-test-shooter template-test-platformer

template-test-flappy:
	cd templates/flappy && python -m pytest -v

template-test-shooter:
	cd templates/shooter && python -m pytest -v

template-test-platformer:
	cd templates/platformer && python -m pytest -v

# Full test suite
test-all: sdk-test mcp-test templates

# Clean
clean:
	rm -rf generated-games/*/bin generated-games/*/__pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Playground
playground-start:
	docker compose -f docker/docker-compose.yml up -d --build

playground-stop:
	docker compose -f docker/docker-compose.yml down
