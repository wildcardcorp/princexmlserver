.PHONY=help
help:
	@echo "available targets -->\n"
	@cat Makefile | grep ".PHONY" | python3 -c 'import sys; sys.stdout.write("".join(list(map(lambda line: line.replace(".PHONY"+"=", "") if (".PHONY"+"=") in line else "", sys.stdin))))'

.PHONY=image
image:
	docker build . -t wildcardcorp/princexmlserver:latest

.PHONY=run
run: image
	docker run -p 6543:6543 wildcardcorp/princexmlserver:latest

.PHONY=run-licensed
run-licensed: image
	docker-compose run --service-ports princexmlserver

.PHONY=debug
debug: image
	docker run -i -t wildcardcorp/princexmlserver:latest /bin/bash

.PHONY=freeze
freeze:
	pyenv install -s
	python3 -m venv freeze-env
	freeze-env/bin/python3 -m pip install -e .
	freeze-env/bin/python3 -m pip freeze | grep "==" | tee requirements.txt
	rm -rf freeze-env
	git diff requirements.txt
