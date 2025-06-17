.PHONY: build clean run test 

build:
	docker build -t rbac-app .

clean:
	docker rmi rbac-app || true

run:
	docker run -p 9000:8000 rbac-app
	echo "http://localhost:9000/docs"

test:
	docker run --rm -v $(PWD)/htmlcov:/app/htmlcov rbac-app pytest --cov=rbac --cov-report=term-missing --cov-report=html


