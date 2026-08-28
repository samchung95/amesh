package main

import (
	"context"
	"log"

	"github.com/amesh-platform/amesh/providers/terraform/internal/provider"
	"github.com/hashicorp/terraform-plugin-framework/providerserver"
)

var version = "dev"

func main() {
	err := providerserver.Serve(
		context.Background(),
		provider.New(version),
		providerserver.ServeOpts{
			Address:         "registry.terraform.io/amesh/amesh",
			ProtocolVersion: 5,
		},
	)
	if err != nil {
		log.Fatal(err)
	}
}
