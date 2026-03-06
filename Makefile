.PHONY: migrate build urun grun clean


# Clean temporary files
clean:
	@echo "🧹 Cleaning..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache dist build
	@echo "✅ Clean complete."

#  Apply migrations
migrate:
	poetry run alembic upgrade head


# Build application
build: 
	$(MAKE) clean 
	poetry install
	$(MAKE) migrate


# Run app via Uvicorn
urun:
	poetry run python -m src.main


# Run app via Gunicorn
grun:
	poetry run python -m src.run
