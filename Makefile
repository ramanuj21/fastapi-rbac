# Makefile

.PHONY: build test clean

build:
	docker build -t rbac-app .

test:
	docker run --rm rbac-app pytest

run:
	docker run -p 9000:8000 rbac-app
	echo "http://localhost:9000/docs"

clean:
	docker rmi rbac-app || true
