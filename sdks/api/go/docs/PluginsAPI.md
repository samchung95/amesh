# \PluginsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreatePluginPolicyRuleApiV1PluginPolicyRulesPost**](PluginsAPI.md#CreatePluginPolicyRuleApiV1PluginPolicyRulesPost) | **Post** /api/v1/plugin-policy/rules | Create Plugin Policy Rule
[**DeletePluginPolicyRuleApiV1PluginPolicyRulesRuleIdDelete**](PluginsAPI.md#DeletePluginPolicyRuleApiV1PluginPolicyRulesRuleIdDelete) | **Delete** /api/v1/plugin-policy/rules/{rule_id} | Delete Plugin Policy Rule
[**DownloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet**](PluginsAPI.md#DownloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet) | **Get** /api/v1/plugin-registry/blobs/{digest} | Download Plugin Registry Bundle
[**EvaluateFlowPluginPolicyApiV1PluginPolicyEvaluatePost**](PluginsAPI.md#EvaluateFlowPluginPolicyApiV1PluginPolicyEvaluatePost) | **Post** /api/v1/plugin-policy/evaluate | Evaluate Flow Plugin Policy
[**ExportPluginRegistryApiV1PluginRegistryOfflineExportGet**](PluginsAPI.md#ExportPluginRegistryApiV1PluginRegistryOfflineExportGet) | **Get** /api/v1/plugin-registry/offline-export | Export Plugin Registry
[**GetEffectivePluginPolicyApiV1PluginPolicyEffectiveGet**](PluginsAPI.md#GetEffectivePluginPolicyApiV1PluginPolicyEffectiveGet) | **Get** /api/v1/plugin-policy/effective | Get Effective Plugin Policy
[**GetPluginPolicyRuleApiV1PluginPolicyRulesRuleIdGet**](PluginsAPI.md#GetPluginPolicyRuleApiV1PluginPolicyRulesRuleIdGet) | **Get** /api/v1/plugin-policy/rules/{rule_id} | Get Plugin Policy Rule
[**GetPluginRegistryIndexApiV1PluginRegistryIndexGet**](PluginsAPI.md#GetPluginRegistryIndexApiV1PluginRegistryIndexGet) | **Get** /api/v1/plugin-registry/index | Get Plugin Registry Index
[**GetPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet**](PluginsAPI.md#GetPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet) | **Get** /api/v1/plugin-registry/packages/{name}/{version} | Get Plugin Registry Package
[**ImportPluginRegistryApiV1PluginRegistryOfflineImportPost**](PluginsAPI.md#ImportPluginRegistryApiV1PluginRegistryOfflineImportPost) | **Post** /api/v1/plugin-registry/offline-import | Import Plugin Registry
[**InstallPluginBundleApiV1PluginsInstallPost**](PluginsAPI.md#InstallPluginBundleApiV1PluginsInstallPost) | **Post** /api/v1/plugins/install | Install Plugin Bundle
[**IsolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet**](PluginsAPI.md#IsolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet) | **Get** /api/v1/plugins/isolated-runtime | Isolated Plugin Runtime Status
[**ListPluginPolicyDecisionsApiV1PluginPolicyDecisionsGet**](PluginsAPI.md#ListPluginPolicyDecisionsApiV1PluginPolicyDecisionsGet) | **Get** /api/v1/plugin-policy/decisions | List Plugin Policy Decisions
[**ListPluginsApiV1PluginsGet**](PluginsAPI.md#ListPluginsApiV1PluginsGet) | **Get** /api/v1/plugins | List Plugins
[**PreviewPluginQuarantineApiV1PluginPolicyQuarantinesPreviewPost**](PluginsAPI.md#PreviewPluginQuarantineApiV1PluginPolicyQuarantinesPreviewPost) | **Post** /api/v1/plugin-policy/quarantines/preview | Preview Plugin Quarantine
[**PublishPluginRegistryPackageApiV1PluginRegistryPackagesPost**](PluginsAPI.md#PublishPluginRegistryPackageApiV1PluginRegistryPackagesPost) | **Post** /api/v1/plugin-registry/packages | Publish Plugin Registry Package
[**QuarantinePluginVersionApiV1PluginPolicyQuarantinesPost**](PluginsAPI.md#QuarantinePluginVersionApiV1PluginPolicyQuarantinesPost) | **Post** /api/v1/plugin-policy/quarantines | Quarantine Plugin Version
[**RefreshPluginsApiV1PluginsRefreshPost**](PluginsAPI.md#RefreshPluginsApiV1PluginsRefreshPost) | **Post** /api/v1/plugins/refresh | Refresh Plugins
[**ReleasePluginQuarantineApiV1PluginPolicyQuarantinesQuarantineIdReleasePost**](PluginsAPI.md#ReleasePluginQuarantineApiV1PluginPolicyQuarantinesQuarantineIdReleasePost) | **Post** /api/v1/plugin-policy/quarantines/{quarantine_id}/release | Release Plugin Quarantine
[**TrustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet**](PluginsAPI.md#TrustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet) | **Get** /api/v1/plugins/trusted-runtime | Trusted Plugin Runtime Status
[**UpdatePluginPolicyRuleApiV1PluginPolicyRulesRuleIdPut**](PluginsAPI.md#UpdatePluginPolicyRuleApiV1PluginPolicyRulesRuleIdPut) | **Put** /api/v1/plugin-policy/rules/{rule_id} | Update Plugin Policy Rule
[**YankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost**](PluginsAPI.md#YankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost) | **Post** /api/v1/plugin-registry/packages/{name}/{version}/yank | Yank Plugin Registry Package



## CreatePluginPolicyRuleApiV1PluginPolicyRulesPost

> PluginPolicyRule CreatePluginPolicyRuleApiV1PluginPolicyRulesPost(ctx).PluginPolicyRuleCreate(pluginPolicyRuleCreate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Create Plugin Policy Rule

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
	pluginPolicyRuleCreate := *openapiclient.NewPluginPolicyRuleCreate(openapiclient.PluginPolicyEffect("ALLOW"), "Reason_example", openapiclient.PluginPolicyScope("INSTANCE"), []openapiclient.PluginPolicyStage{openapiclient.PluginPolicyStage("AUTHORING")}) // PluginPolicyRuleCreate |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.CreatePluginPolicyRuleApiV1PluginPolicyRulesPost(context.Background()).PluginPolicyRuleCreate(pluginPolicyRuleCreate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.CreatePluginPolicyRuleApiV1PluginPolicyRulesPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreatePluginPolicyRuleApiV1PluginPolicyRulesPost`: PluginPolicyRule
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.CreatePluginPolicyRuleApiV1PluginPolicyRulesPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreatePluginPolicyRuleApiV1PluginPolicyRulesPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **pluginPolicyRuleCreate** | [**PluginPolicyRuleCreate**](PluginPolicyRuleCreate.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PluginPolicyRule**](PluginPolicyRule.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeletePluginPolicyRuleApiV1PluginPolicyRulesRuleIdDelete

> DeletePluginPolicyRuleApiV1PluginPolicyRulesRuleIdDelete(ctx, ruleId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Delete Plugin Policy Rule

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
	ruleId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.PluginsAPI.DeletePluginPolicyRuleApiV1PluginPolicyRulesRuleIdDelete(context.Background(), ruleId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.DeletePluginPolicyRuleApiV1PluginPolicyRulesRuleIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**ruleId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDeletePluginPolicyRuleApiV1PluginPolicyRulesRuleIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

 (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DownloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet

> DownloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet(ctx, digest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Download Plugin Registry Bundle

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
	digest := "digest_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.PluginsAPI.DownloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet(context.Background(), digest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.DownloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**digest** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDownloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

 (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## EvaluateFlowPluginPolicyApiV1PluginPolicyEvaluatePost

> PluginPolicyDecision EvaluateFlowPluginPolicyApiV1PluginPolicyEvaluatePost(ctx).Stage(stage).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Evaluate Flow Plugin Policy

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
	stage := openapiclient.PluginPolicyStage("AUTHORING") // PluginPolicyStage |  (optional) (default to "VALIDATION")
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.EvaluateFlowPluginPolicyApiV1PluginPolicyEvaluatePost(context.Background()).Stage(stage).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.EvaluateFlowPluginPolicyApiV1PluginPolicyEvaluatePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `EvaluateFlowPluginPolicyApiV1PluginPolicyEvaluatePost`: PluginPolicyDecision
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.EvaluateFlowPluginPolicyApiV1PluginPolicyEvaluatePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiEvaluateFlowPluginPolicyApiV1PluginPolicyEvaluatePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stage** | [**PluginPolicyStage**](PluginPolicyStage.md) |  | [default to &quot;VALIDATION&quot;]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PluginPolicyDecision**](PluginPolicyDecision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ExportPluginRegistryApiV1PluginRegistryOfflineExportGet

> ExportPluginRegistryApiV1PluginRegistryOfflineExportGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Export Plugin Registry

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
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.PluginsAPI.ExportPluginRegistryApiV1PluginRegistryOfflineExportGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.ExportPluginRegistryApiV1PluginRegistryOfflineExportGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiExportPluginRegistryApiV1PluginRegistryOfflineExportGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

 (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetEffectivePluginPolicyApiV1PluginPolicyEffectiveGet

> EffectivePluginPolicy GetEffectivePluginPolicyApiV1PluginPolicyEffectiveGet(ctx).Namespace(namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Effective Plugin Policy

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
	namespace := "namespace_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.GetEffectivePluginPolicyApiV1PluginPolicyEffectiveGet(context.Background()).Namespace(namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.GetEffectivePluginPolicyApiV1PluginPolicyEffectiveGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetEffectivePluginPolicyApiV1PluginPolicyEffectiveGet`: EffectivePluginPolicy
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.GetEffectivePluginPolicyApiV1PluginPolicyEffectiveGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetEffectivePluginPolicyApiV1PluginPolicyEffectiveGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**EffectivePluginPolicy**](EffectivePluginPolicy.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetPluginPolicyRuleApiV1PluginPolicyRulesRuleIdGet

> PluginPolicyRule GetPluginPolicyRuleApiV1PluginPolicyRulesRuleIdGet(ctx, ruleId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Plugin Policy Rule

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
	ruleId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.GetPluginPolicyRuleApiV1PluginPolicyRulesRuleIdGet(context.Background(), ruleId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.GetPluginPolicyRuleApiV1PluginPolicyRulesRuleIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetPluginPolicyRuleApiV1PluginPolicyRulesRuleIdGet`: PluginPolicyRule
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.GetPluginPolicyRuleApiV1PluginPolicyRulesRuleIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**ruleId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetPluginPolicyRuleApiV1PluginPolicyRulesRuleIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PluginPolicyRule**](PluginPolicyRule.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetPluginRegistryIndexApiV1PluginRegistryIndexGet

> PluginRegistryIndex GetPluginRegistryIndexApiV1PluginRegistryIndexGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Plugin Registry Index

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
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.GetPluginRegistryIndexApiV1PluginRegistryIndexGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.GetPluginRegistryIndexApiV1PluginRegistryIndexGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetPluginRegistryIndexApiV1PluginRegistryIndexGet`: PluginRegistryIndex
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.GetPluginRegistryIndexApiV1PluginRegistryIndexGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetPluginRegistryIndexApiV1PluginRegistryIndexGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PluginRegistryIndex**](PluginRegistryIndex.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet

> PluginRegistryPackage GetPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet(ctx, name, version).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Plugin Registry Package

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
	name := "name_example" // string |
	version := "version_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.GetPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet(context.Background(), name, version).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.GetPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet`: PluginRegistryPackage
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.GetPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**name** | **string** |  |
**version** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PluginRegistryPackage**](PluginRegistryPackage.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ImportPluginRegistryApiV1PluginRegistryOfflineImportPost

> PluginRegistryIndex ImportPluginRegistryApiV1PluginRegistryOfflineImportPost(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Import Plugin Registry

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
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.ImportPluginRegistryApiV1PluginRegistryOfflineImportPost(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.ImportPluginRegistryApiV1PluginRegistryOfflineImportPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ImportPluginRegistryApiV1PluginRegistryOfflineImportPost`: PluginRegistryIndex
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.ImportPluginRegistryApiV1PluginRegistryOfflineImportPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiImportPluginRegistryApiV1PluginRegistryOfflineImportPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PluginRegistryIndex**](PluginRegistryIndex.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## InstallPluginBundleApiV1PluginsInstallPost

> PluginCatalogSnapshot InstallPluginBundleApiV1PluginsInstallPost(ctx).ContentDigest(contentDigest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Install Plugin Bundle

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
	contentDigest := "contentDigest_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.InstallPluginBundleApiV1PluginsInstallPost(context.Background()).ContentDigest(contentDigest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.InstallPluginBundleApiV1PluginsInstallPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `InstallPluginBundleApiV1PluginsInstallPost`: PluginCatalogSnapshot
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.InstallPluginBundleApiV1PluginsInstallPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiInstallPluginBundleApiV1PluginsInstallPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **contentDigest** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PluginCatalogSnapshot**](PluginCatalogSnapshot.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## IsolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet

> IsolatedPluginRuntimeSnapshot IsolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Isolated Plugin Runtime Status

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
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.IsolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.IsolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `IsolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet`: IsolatedPluginRuntimeSnapshot
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.IsolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiIsolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**IsolatedPluginRuntimeSnapshot**](IsolatedPluginRuntimeSnapshot.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListPluginPolicyDecisionsApiV1PluginPolicyDecisionsGet

> []PluginPolicyDecision ListPluginPolicyDecisionsApiV1PluginPolicyDecisionsGet(ctx).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Plugin Policy Decisions

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
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.ListPluginPolicyDecisionsApiV1PluginPolicyDecisionsGet(context.Background()).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.ListPluginPolicyDecisionsApiV1PluginPolicyDecisionsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListPluginPolicyDecisionsApiV1PluginPolicyDecisionsGet`: []PluginPolicyDecision
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.ListPluginPolicyDecisionsApiV1PluginPolicyDecisionsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListPluginPolicyDecisionsApiV1PluginPolicyDecisionsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]PluginPolicyDecision**](PluginPolicyDecision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListPluginsApiV1PluginsGet

> PluginCatalogSnapshot ListPluginsApiV1PluginsGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Plugins

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
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.ListPluginsApiV1PluginsGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.ListPluginsApiV1PluginsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListPluginsApiV1PluginsGet`: PluginCatalogSnapshot
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.ListPluginsApiV1PluginsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListPluginsApiV1PluginsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PluginCatalogSnapshot**](PluginCatalogSnapshot.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PreviewPluginQuarantineApiV1PluginPolicyQuarantinesPreviewPost

> PluginPolicyImpactPreview PreviewPluginQuarantineApiV1PluginPolicyQuarantinesPreviewPost(ctx).PluginQuarantineCreate(pluginQuarantineCreate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Preview Plugin Quarantine

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
	pluginQuarantineCreate := *openapiclient.NewPluginQuarantineCreate("Package_example", "Reason_example", "Version_example") // PluginQuarantineCreate |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.PreviewPluginQuarantineApiV1PluginPolicyQuarantinesPreviewPost(context.Background()).PluginQuarantineCreate(pluginQuarantineCreate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.PreviewPluginQuarantineApiV1PluginPolicyQuarantinesPreviewPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PreviewPluginQuarantineApiV1PluginPolicyQuarantinesPreviewPost`: PluginPolicyImpactPreview
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.PreviewPluginQuarantineApiV1PluginPolicyQuarantinesPreviewPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiPreviewPluginQuarantineApiV1PluginPolicyQuarantinesPreviewPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **pluginQuarantineCreate** | [**PluginQuarantineCreate**](PluginQuarantineCreate.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PluginPolicyImpactPreview**](PluginPolicyImpactPreview.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PublishPluginRegistryPackageApiV1PluginRegistryPackagesPost

> PluginRegistryPackage PublishPluginRegistryPackageApiV1PluginRegistryPackagesPost(ctx).PluginRegistryPublishRequest(pluginRegistryPublishRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Publish Plugin Registry Package

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
	pluginRegistryPublishRequest := *openapiclient.NewPluginRegistryPublishRequest([]openapiclient.PluginRegistryPublishAttachment{*openapiclient.NewPluginRegistryPublishAttachment("ContentBase64_example", openapiclient.PluginRegistryAttachmentKind("sbom"), "MediaType_example")}, "BundleBase64_example", *openapiclient.NewPluginRegistryMetadata("ChangelogUrl_example", "DocumentationUrl_example", "License_example", "SdkRange_example", "SourceUrl_example", "SupportedPlatformRange_example")) // PluginRegistryPublishRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.PublishPluginRegistryPackageApiV1PluginRegistryPackagesPost(context.Background()).PluginRegistryPublishRequest(pluginRegistryPublishRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.PublishPluginRegistryPackageApiV1PluginRegistryPackagesPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PublishPluginRegistryPackageApiV1PluginRegistryPackagesPost`: PluginRegistryPackage
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.PublishPluginRegistryPackageApiV1PluginRegistryPackagesPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiPublishPluginRegistryPackageApiV1PluginRegistryPackagesPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **pluginRegistryPublishRequest** | [**PluginRegistryPublishRequest**](PluginRegistryPublishRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PluginRegistryPackage**](PluginRegistryPackage.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## QuarantinePluginVersionApiV1PluginPolicyQuarantinesPost

> PluginQuarantine QuarantinePluginVersionApiV1PluginPolicyQuarantinesPost(ctx).PluginQuarantineCreate(pluginQuarantineCreate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Quarantine Plugin Version

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
	pluginQuarantineCreate := *openapiclient.NewPluginQuarantineCreate("Package_example", "Reason_example", "Version_example") // PluginQuarantineCreate |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.QuarantinePluginVersionApiV1PluginPolicyQuarantinesPost(context.Background()).PluginQuarantineCreate(pluginQuarantineCreate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.QuarantinePluginVersionApiV1PluginPolicyQuarantinesPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `QuarantinePluginVersionApiV1PluginPolicyQuarantinesPost`: PluginQuarantine
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.QuarantinePluginVersionApiV1PluginPolicyQuarantinesPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiQuarantinePluginVersionApiV1PluginPolicyQuarantinesPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **pluginQuarantineCreate** | [**PluginQuarantineCreate**](PluginQuarantineCreate.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PluginQuarantine**](PluginQuarantine.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RefreshPluginsApiV1PluginsRefreshPost

> PluginCatalogSnapshot RefreshPluginsApiV1PluginsRefreshPost(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Refresh Plugins

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
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.RefreshPluginsApiV1PluginsRefreshPost(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.RefreshPluginsApiV1PluginsRefreshPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RefreshPluginsApiV1PluginsRefreshPost`: PluginCatalogSnapshot
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.RefreshPluginsApiV1PluginsRefreshPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiRefreshPluginsApiV1PluginsRefreshPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PluginCatalogSnapshot**](PluginCatalogSnapshot.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ReleasePluginQuarantineApiV1PluginPolicyQuarantinesQuarantineIdReleasePost

> PluginQuarantine ReleasePluginQuarantineApiV1PluginPolicyQuarantinesQuarantineIdReleasePost(ctx, quarantineId).Reason(reason).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Release Plugin Quarantine

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
	quarantineId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	reason := "reason_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.ReleasePluginQuarantineApiV1PluginPolicyQuarantinesQuarantineIdReleasePost(context.Background(), quarantineId).Reason(reason).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.ReleasePluginQuarantineApiV1PluginPolicyQuarantinesQuarantineIdReleasePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ReleasePluginQuarantineApiV1PluginPolicyQuarantinesQuarantineIdReleasePost`: PluginQuarantine
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.ReleasePluginQuarantineApiV1PluginPolicyQuarantinesQuarantineIdReleasePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**quarantineId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiReleasePluginQuarantineApiV1PluginPolicyQuarantinesQuarantineIdReleasePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **reason** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PluginQuarantine**](PluginQuarantine.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## TrustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet

> TrustedPluginRuntimeSnapshot TrustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Trusted Plugin Runtime Status

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
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.TrustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.TrustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `TrustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet`: TrustedPluginRuntimeSnapshot
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.TrustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiTrustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**TrustedPluginRuntimeSnapshot**](TrustedPluginRuntimeSnapshot.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdatePluginPolicyRuleApiV1PluginPolicyRulesRuleIdPut

> PluginPolicyRule UpdatePluginPolicyRuleApiV1PluginPolicyRulesRuleIdPut(ctx, ruleId).PluginPolicyRuleCreate(pluginPolicyRuleCreate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Update Plugin Policy Rule

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
	ruleId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	pluginPolicyRuleCreate := *openapiclient.NewPluginPolicyRuleCreate(openapiclient.PluginPolicyEffect("ALLOW"), "Reason_example", openapiclient.PluginPolicyScope("INSTANCE"), []openapiclient.PluginPolicyStage{openapiclient.PluginPolicyStage("AUTHORING")}) // PluginPolicyRuleCreate |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.UpdatePluginPolicyRuleApiV1PluginPolicyRulesRuleIdPut(context.Background(), ruleId).PluginPolicyRuleCreate(pluginPolicyRuleCreate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.UpdatePluginPolicyRuleApiV1PluginPolicyRulesRuleIdPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdatePluginPolicyRuleApiV1PluginPolicyRulesRuleIdPut`: PluginPolicyRule
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.UpdatePluginPolicyRuleApiV1PluginPolicyRulesRuleIdPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**ruleId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiUpdatePluginPolicyRuleApiV1PluginPolicyRulesRuleIdPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **pluginPolicyRuleCreate** | [**PluginPolicyRuleCreate**](PluginPolicyRuleCreate.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PluginPolicyRule**](PluginPolicyRule.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## YankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost

> PluginRegistryPackage YankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost(ctx, name, version).PluginRegistryYankRequest(pluginRegistryYankRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Yank Plugin Registry Package

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
	name := "name_example" // string |
	version := "version_example" // string |
	pluginRegistryYankRequest := *openapiclient.NewPluginRegistryYankRequest("Reason_example") // PluginRegistryYankRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PluginsAPI.YankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost(context.Background(), name, version).PluginRegistryYankRequest(pluginRegistryYankRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PluginsAPI.YankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `YankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost`: PluginRegistryPackage
	fmt.Fprintf(os.Stdout, "Response from `PluginsAPI.YankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**name** | **string** |  |
**version** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiYankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **pluginRegistryYankRequest** | [**PluginRegistryYankRequest**](PluginRegistryYankRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PluginRegistryPackage**](PluginRegistryPackage.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
