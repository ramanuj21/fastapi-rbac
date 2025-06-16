# Makefile

.PHONY: build test clean

build:
	docker build -t rbac-test .

test:
	docker run --rm rbac-test

clean:
	docker rmi rbac-test || true
