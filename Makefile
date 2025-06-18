.PHONY: build clean run test test-local install lock

build:
	docker build -t rbac-app .

clean:
	docker rmi rbac-app || true

run:
	@echo "Launching RBAC API at http://localhost:9000/docs"
	docker run -p 9000:8000 rbac-app

test:
	docker run --rm -v $(PWD)/htmlcov:/app/htmlcov rbac-app \
		pytest --cov=rbac --cov-report=term-missing --cov-report=html

test-local:
	pytest --cov=rbac --cov-report=term-missing --cov-report=html

lock:
	poetry lock --no-update

install: lock
	poetry install
