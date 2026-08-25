# \AgentsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CompareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet**](AgentsAPI.md#CompareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet) | **Get** /api/v1/namespaces/{namespace}/agent/definitions/{key}/compare | Compare Agent Definition Revisions
[**CreateAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost**](AgentsAPI.md#CreateAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost) | **Post** /api/v1/namespaces/{namespace}/agent/mcp-connections | Create Agent Mcp Connection Revision
[**CreateAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost**](AgentsAPI.md#CreateAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost) | **Post** /api/v1/namespaces/{namespace}/agent/resources | Create Agent Resource Revision
[**DiagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet**](AgentsAPI.md#DiagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet) | **Get** /api/v1/namespaces/{namespace}/agent/model-policies/{key}/migration | Diagnose Model Policy Migration
[**DiscoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost**](AgentsAPI.md#DiscoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost) | **Post** /api/v1/namespaces/{namespace}/agent/mcp-connections/discover | Discover Agent Mcp Connection
[**GetAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet**](AgentsAPI.md#GetAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet) | **Get** /api/v1/namespaces/{namespace}/agent/mcp-connections/{key} | Get Agent Mcp Connection
[**GetAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet**](AgentsAPI.md#GetAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet) | **Get** /api/v1/namespaces/{namespace}/agent/resources/{kind}/{key} | Get Agent Resource
[**ListAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet**](AgentsAPI.md#ListAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet) | **Get** /api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/tools | List Agent Mcp Connection Tools
[**ListAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet**](AgentsAPI.md#ListAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet) | **Get** /api/v1/namespaces/{namespace}/agent/mcp-connections | List Agent Mcp Connections
[**ListAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet**](AgentsAPI.md#ListAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet) | **Get** /api/v1/namespaces/{namespace}/agent/resources | List Agent Resources
[**ResolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost**](AgentsAPI.md#ResolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost) | **Post** /api/v1/namespaces/{namespace}/agent/definitions/{key}/resolve | Resolve Agent Definition



## CompareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet

> AgentRevisionComparison CompareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet(ctx, namespace, key).FromRevision(fromRevision).ToRevision(toRevision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Compare Agent Definition Revisions

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	key := "key_example" // string |
	fromRevision := int32(56) // int32 |
	toRevision := int32(56) // int32 |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentsAPI.CompareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet(context.Background(), namespace, key).FromRevision(fromRevision).ToRevision(toRevision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentsAPI.CompareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CompareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet`: AgentRevisionComparison
	fmt.Fprintf(os.Stdout, "Response from `AgentsAPI.CompareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**key** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiCompareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **fromRevision** | **int32** |  |
 **toRevision** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AgentRevisionComparison**](AgentRevisionComparison.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost

> McpConnectionRevision CreateAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost(ctx, namespace).McpConnectionSpec(mcpConnectionSpec).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Create Agent Mcp Connection Revision

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	mcpConnectionSpec := *openapiclient.NewMcpConnectionSpec("CredentialRef_example", "Endpoint_example", "Key_example", "Namespace_example", []string{"ToolAllowlist_example"}, []openapiclient.McpToolPin{*openapiclient.NewMcpToolPin(map[string]interface{}{"key": interface{}(123)}, "Name_example")}) // McpConnectionSpec |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentsAPI.CreateAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost(context.Background(), namespace).McpConnectionSpec(mcpConnectionSpec).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentsAPI.CreateAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost`: McpConnectionRevision
	fmt.Fprintf(os.Stdout, "Response from `AgentsAPI.CreateAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiCreateAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **mcpConnectionSpec** | [**McpConnectionSpec**](McpConnectionSpec.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**McpConnectionRevision**](McpConnectionRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost

> AgentResourceRevision CreateAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost(ctx, namespace).Spec(spec).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Create Agent Resource Revision

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	spec := openapiclient.Spec{AgentDefinitionSpecInput: openapiclient.NewAgentDefinitionSpecInput(*openapiclient.NewAgentEvaluationPolicy(), *openapiclient.NewAgentHardLimitsInput(int32(123), *openapiclient.NewMaxcostusd(), int32(123), int32(123), int32(123), int32(123), int32(123), int32(123)), map[string]interface{}{"key": interface{}(123)}, "Instructions_example", "Key_example", *openapiclient.NewAgentMemoryPolicy(), *openapiclient.NewAgentResourceRef("Key_example", int32(123)), "Namespace_example", map[string]interface{}{"key": interface{}(123)}, *openapiclient.NewAgentPermissions(), "Title_example")} // Spec |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentsAPI.CreateAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost(context.Background(), namespace).Spec(spec).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentsAPI.CreateAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost`: AgentResourceRevision
	fmt.Fprintf(os.Stdout, "Response from `AgentsAPI.CreateAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiCreateAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **spec** | [**Spec**](Spec.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AgentResourceRevision**](AgentResourceRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DiagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet

> ProviderMigrationDiagnostic DiagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet(ctx, namespace, key).FromRevision(fromRevision).ToRevision(toRevision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Diagnose Model Policy Migration

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	key := "key_example" // string |
	fromRevision := int32(56) // int32 |
	toRevision := int32(56) // int32 |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentsAPI.DiagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet(context.Background(), namespace, key).FromRevision(fromRevision).ToRevision(toRevision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentsAPI.DiagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DiagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet`: ProviderMigrationDiagnostic
	fmt.Fprintf(os.Stdout, "Response from `AgentsAPI.DiagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**key** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDiagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **fromRevision** | **int32** |  |
 **toRevision** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**ProviderMigrationDiagnostic**](ProviderMigrationDiagnostic.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DiscoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost

> McpDiscoveryResult DiscoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost(ctx, namespace).McpConnectionDiscoveryRequest(mcpConnectionDiscoveryRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Discover Agent Mcp Connection

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	mcpConnectionDiscoveryRequest := *openapiclient.NewMcpConnectionDiscoveryRequest("CredentialRef_example", "Endpoint_example") // McpConnectionDiscoveryRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentsAPI.DiscoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost(context.Background(), namespace).McpConnectionDiscoveryRequest(mcpConnectionDiscoveryRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentsAPI.DiscoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DiscoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost`: McpDiscoveryResult
	fmt.Fprintf(os.Stdout, "Response from `AgentsAPI.DiscoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDiscoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **mcpConnectionDiscoveryRequest** | [**McpConnectionDiscoveryRequest**](McpConnectionDiscoveryRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**McpDiscoveryResult**](McpDiscoveryResult.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet

> McpConnectionRevision GetAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet(ctx, namespace, key).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Agent Mcp Connection

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	key := "key_example" // string |
	revision := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentsAPI.GetAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet(context.Background(), namespace, key).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentsAPI.GetAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet`: McpConnectionRevision
	fmt.Fprintf(os.Stdout, "Response from `AgentsAPI.GetAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**key** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **revision** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**McpConnectionRevision**](McpConnectionRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet

> AgentResourceRevision GetAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet(ctx, namespace, kind, key).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Agent Resource

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	kind := openapiclient.AgentResourceKind("PROMPT") // AgentResourceKind |
	key := "key_example" // string |
	revision := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentsAPI.GetAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet(context.Background(), namespace, kind, key).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentsAPI.GetAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet`: AgentResourceRevision
	fmt.Fprintf(os.Stdout, "Response from `AgentsAPI.GetAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**kind** | [**AgentResourceKind**](.md) |  |
**key** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



 **revision** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AgentResourceRevision**](AgentResourceRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet

> []map[string]interface{} ListAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet(ctx, namespace, key).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Agent Mcp Connection Tools

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	key := "key_example" // string |
	revision := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentsAPI.ListAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet(context.Background(), namespace, key).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentsAPI.ListAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet`: []map[string]interface{}
	fmt.Fprintf(os.Stdout, "Response from `AgentsAPI.ListAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**key** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **revision** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]map[string]interface{}**](map.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet

> []McpConnectionRevision ListAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet(ctx, namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Agent Mcp Connections

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentsAPI.ListAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet(context.Background(), namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentsAPI.ListAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet`: []McpConnectionRevision
	fmt.Fprintf(os.Stdout, "Response from `AgentsAPI.ListAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]McpConnectionRevision**](McpConnectionRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet

> []AgentResourceRevision ListAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet(ctx, namespace).Kind(kind).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Agent Resources

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	kind := openapiclient.AgentResourceKind("PROMPT") // AgentResourceKind |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentsAPI.ListAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet(context.Background(), namespace).Kind(kind).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentsAPI.ListAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet`: []AgentResourceRevision
	fmt.Fprintf(os.Stdout, "Response from `AgentsAPI.ListAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListAgentResourcesApiV1NamespacesNamespaceAgentResourcesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **kind** | [**AgentResourceKind**](AgentResourceKind.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]AgentResourceRevision**](AgentResourceRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ResolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost

> AgentCapabilityPin ResolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost(ctx, namespace, key).AgentResolutionRequest(agentResolutionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Resolve Agent Definition

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	key := "key_example" // string |
	agentResolutionRequest := *openapiclient.NewAgentResolutionRequest(int32(123), "SubjectRef_example") // AgentResolutionRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentsAPI.ResolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost(context.Background(), namespace, key).AgentResolutionRequest(agentResolutionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentsAPI.ResolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ResolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost`: AgentCapabilityPin
	fmt.Fprintf(os.Stdout, "Response from `AgentsAPI.ResolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**key** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiResolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **agentResolutionRequest** | [**AgentResolutionRequest**](AgentResolutionRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AgentCapabilityPin**](AgentCapabilityPin.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
