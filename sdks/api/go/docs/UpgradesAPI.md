# \UpgradesAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**GetUpgradePolicyApiV1UpgradesPolicyGet**](UpgradesAPI.md#GetUpgradePolicyApiV1UpgradesPolicyGet) | **Get** /api/v1/upgrades/policy | Get Upgrade Policy
[**MigrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost**](UpgradesAPI.md#MigrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost) | **Post** /api/v1/upgrades/configuration/migrate | Migrate Upgrade Configuration
[**PreviewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet**](UpgradesAPI.md#PreviewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet) | **Get** /api/v1/upgrades/events/upcast | Preview Upgrade Event Upcast
[**RunUpgradeEventUpcastApiV1UpgradesEventsUpcastPost**](UpgradesAPI.md#RunUpgradeEventUpcastApiV1UpgradesEventsUpcastPost) | **Post** /api/v1/upgrades/events/upcast | Run Upgrade Event Upcast
[**RunUpgradePostflightApiV1UpgradesPostflightPost**](UpgradesAPI.md#RunUpgradePostflightApiV1UpgradesPostflightPost) | **Post** /api/v1/upgrades/postflight | Run Upgrade Postflight
[**RunUpgradePreflightApiV1UpgradesPreflightPost**](UpgradesAPI.md#RunUpgradePreflightApiV1UpgradesPreflightPost) | **Post** /api/v1/upgrades/preflight | Run Upgrade Preflight



## GetUpgradePolicyApiV1UpgradesPolicyGet

> UpgradePolicy GetUpgradePolicyApiV1UpgradesPolicyGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Get Upgrade Policy

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

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.UpgradesAPI.GetUpgradePolicyApiV1UpgradesPolicyGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `UpgradesAPI.GetUpgradePolicyApiV1UpgradesPolicyGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetUpgradePolicyApiV1UpgradesPolicyGet`: UpgradePolicy
	fmt.Fprintf(os.Stdout, "Response from `UpgradesAPI.GetUpgradePolicyApiV1UpgradesPolicyGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetUpgradePolicyApiV1UpgradesPolicyGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**UpgradePolicy**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## MigrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost

> ConfigurationMigration MigrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost(ctx).ConfigurationMigrationRequest(configurationMigrationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Migrate Upgrade Configuration

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
	configurationMigrationRequest := *openapiclient.NewConfigurationMigrationRequest(map[string]interface{}{"key": interface{}(123)}, openapiclient.ConfigurationMigrationKind("flow"), "TargetVersion_example") // ConfigurationMigrationRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.UpgradesAPI.MigrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost(context.Background()).ConfigurationMigrationRequest(configurationMigrationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `UpgradesAPI.MigrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `MigrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost`: ConfigurationMigration
	fmt.Fprintf(os.Stdout, "Response from `UpgradesAPI.MigrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiMigrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **configurationMigrationRequest** | **ConfigurationMigrationRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**ConfigurationMigration**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PreviewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet

> PersistedEventMigration PreviewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Preview Upgrade Event Upcast

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

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.UpgradesAPI.PreviewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `UpgradesAPI.PreviewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PreviewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet`: PersistedEventMigration
	fmt.Fprintf(os.Stdout, "Response from `UpgradesAPI.PreviewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiPreviewUpgradeEventUpcastApiV1UpgradesEventsUpcastGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**PersistedEventMigration**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RunUpgradeEventUpcastApiV1UpgradesEventsUpcastPost

> PersistedEventMigration RunUpgradeEventUpcastApiV1UpgradesEventsUpcastPost(ctx).PersistedEventMigrationRequest(persistedEventMigrationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Run Upgrade Event Upcast

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
	persistedEventMigrationRequest := *openapiclient.NewPersistedEventMigrationRequest("Confirmation_example", "Reason_example") // PersistedEventMigrationRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.UpgradesAPI.RunUpgradeEventUpcastApiV1UpgradesEventsUpcastPost(context.Background()).PersistedEventMigrationRequest(persistedEventMigrationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `UpgradesAPI.RunUpgradeEventUpcastApiV1UpgradesEventsUpcastPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RunUpgradeEventUpcastApiV1UpgradesEventsUpcastPost`: PersistedEventMigration
	fmt.Fprintf(os.Stdout, "Response from `UpgradesAPI.RunUpgradeEventUpcastApiV1UpgradesEventsUpcastPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiRunUpgradeEventUpcastApiV1UpgradesEventsUpcastPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **persistedEventMigrationRequest** | **PersistedEventMigrationRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**PersistedEventMigration**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RunUpgradePostflightApiV1UpgradesPostflightPost

> UpgradeReport RunUpgradePostflightApiV1UpgradesPostflightPost(ctx).UpgradeReportRequest(upgradeReportRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Run Upgrade Postflight

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
	upgradeReportRequest := *openapiclient.NewUpgradeReportRequest("FromVersion_example", "ToVersion_example") // UpgradeReportRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.UpgradesAPI.RunUpgradePostflightApiV1UpgradesPostflightPost(context.Background()).UpgradeReportRequest(upgradeReportRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `UpgradesAPI.RunUpgradePostflightApiV1UpgradesPostflightPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RunUpgradePostflightApiV1UpgradesPostflightPost`: UpgradeReport
	fmt.Fprintf(os.Stdout, "Response from `UpgradesAPI.RunUpgradePostflightApiV1UpgradesPostflightPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiRunUpgradePostflightApiV1UpgradesPostflightPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **upgradeReportRequest** | **UpgradeReportRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**UpgradeReport**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RunUpgradePreflightApiV1UpgradesPreflightPost

> UpgradeReport RunUpgradePreflightApiV1UpgradesPreflightPost(ctx).UpgradeReportRequest(upgradeReportRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Run Upgrade Preflight

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
	upgradeReportRequest := *openapiclient.NewUpgradeReportRequest("FromVersion_example", "ToVersion_example") // UpgradeReportRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.UpgradesAPI.RunUpgradePreflightApiV1UpgradesPreflightPost(context.Background()).UpgradeReportRequest(upgradeReportRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `UpgradesAPI.RunUpgradePreflightApiV1UpgradesPreflightPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RunUpgradePreflightApiV1UpgradesPreflightPost`: UpgradeReport
	fmt.Fprintf(os.Stdout, "Response from `UpgradesAPI.RunUpgradePreflightApiV1UpgradesPreflightPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiRunUpgradePreflightApiV1UpgradesPreflightPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **upgradeReportRequest** | **UpgradeReportRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**UpgradeReport**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
