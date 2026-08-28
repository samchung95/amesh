.PHONY: build docs fmt test

build:
	go build -o build/terraform-provider-amesh .

docs:
	go run github.com/hashicorp/terraform-plugin-docs/cmd/tfplugindocs@v0.25.0 generate --provider-dir . --provider-name amesh

fmt:
	gofmt -w .

test:
	go test ./...
