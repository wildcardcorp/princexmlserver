.PHONY: help
help:
	@echo "available targets -->\n"
	@cat Makefile | grep ".PHONY" | python3 -c 'import sys; sys.stdout.write("".join(list(map(lambda line: line.replace(".PHONY"+": ", "") if (".PHONY"+": ") in line else "", sys.stdin))))'

start-redis:
	docker run --rm -d --name=redis redis:latest

.PHONY: build
build:
	docker build --platform=linux/amd64 . -t wildcardcorp/princexmlserver:latest
	docker tag wildcardcorp/princexmlserver:latest wildcardcorp/princexmlserver:${ver}

.PHONY: run
run: build
	docker run --platform=linux/amd64 -p 6543:6543 wildcardcorp/princexmlserver:latest

.PHONY: run-licensed
run-licensed: build
	docker-compose run --service-ports princexmlserver

.PHONY: debug
debug: build
	docker run --platform=linux/amd64 -i -t wildcardcorp/princexmlserver:latest /bin/bash
