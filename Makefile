.PHONY: help
help:
	@echo "available targets -->\n"
	@cat Makefile | grep ".PHONY" | python3 -c 'import sys; sys.stdout.write("".join(list(map(lambda line: line.replace(".PHONY"+": ", "") if (".PHONY"+": ") in line else "", sys.stdin))))'


.PHONY: build
build:
	docker build --platform=linux/amd64 -f Dockerfile . -t princexmlserver:dev
	docker build --platform=linux/amd64 -f Dockerfile.tests . -t princexmlserver:tests

.PHONY: test
test: build
	docker run -it --rm --platform=linux/amd64 princexmlserver:tests

.PHONY: quicktest
quicktest:
	docker run -it --rm --platform=linux/amd64 -v $$(pwd):/usr/src/app/ princexmlserver:tests pytest --cov=princexmlserver

.PHONY: start-redis
start-redis:
	docker run -d -it --rm --platform=linux/amd64 --name=redis redis:latest

.PHONY: start-princexmlserver
start-princexmlserver: build
	docker run -d -it --rm --platform=linux/amd64 --name=princexmlserver -p 6543:6543 princexmlserver:dev pserve /usr/src/app/docker.ini use_redis=true redis_host=redis
