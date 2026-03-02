.PHONY: package run

# Simple packaging helpers
package:
	docker build -t myapp:latest .

run:
	docker run --rm -p 8080:8080 myapp:latest
