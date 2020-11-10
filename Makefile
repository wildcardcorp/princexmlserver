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
