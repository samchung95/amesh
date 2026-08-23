# UpgradesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getUpgradePolicyApiV1UpgradesPolicyGet**](UpgradesApi.md#getUpgradePolicyApiV1UpgradesPolicyGet) | **GET** /api/v1/upgrades/policy | Get Upgrade Policy |
| [**getUpgradePolicyApiV1UpgradesPolicyGetWithHttpInfo**](UpgradesApi.md#getUpgradePolicyApiV1UpgradesPolicyGetWithHttpInfo) | **GET** /api/v1/upgrades/policy | Get Upgrade Policy |
| [**migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost**](UpgradesApi.md#migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost) | **POST** /api/v1/upgrades/configuration/migrate | Migrate Upgrade Configuration |
| [**migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePostWithHttpInfo**](UpgradesApi.md#migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePostWithHttpInfo) | **POST** /api/v1/upgrades/configuration/migrate | Migrate Upgrade Configuration |
| [**previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet**](UpgradesApi.md#previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet) | **GET** /api/v1/upgrades/events/upcast | Preview Upgrade Event Upcast |
| [**previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGetWithHttpInfo**](UpgradesApi.md#previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGetWithHttpInfo) | **GET** /api/v1/upgrades/events/upcast | Preview Upgrade Event Upcast |
| [**runUpgradeEventUpcastApiV1UpgradesEventsUpcastPost**](UpgradesApi.md#runUpgradeEventUpcastApiV1UpgradesEventsUpcastPost) | **POST** /api/v1/upgrades/events/upcast | Run Upgrade Event Upcast |
| [**runUpgradeEventUpcastApiV1UpgradesEventsUpcastPostWithHttpInfo**](UpgradesApi.md#runUpgradeEventUpcastApiV1UpgradesEventsUpcastPostWithHttpInfo) | **POST** /api/v1/upgrades/events/upcast | Run Upgrade Event Upcast |
| [**runUpgradePostflightApiV1UpgradesPostflightPost**](UpgradesApi.md#runUpgradePostflightApiV1UpgradesPostflightPost) | **POST** /api/v1/upgrades/postflight | Run Upgrade Postflight |
| [**runUpgradePostflightApiV1UpgradesPostflightPostWithHttpInfo**](UpgradesApi.md#runUpgradePostflightApiV1UpgradesPostflightPostWithHttpInfo) | **POST** /api/v1/upgrades/postflight | Run Upgrade Postflight |
| [**runUpgradePreflightApiV1UpgradesPreflightPost**](UpgradesApi.md#runUpgradePreflightApiV1UpgradesPreflightPost) | **POST** /api/v1/upgrades/preflight | Run Upgrade Preflight |
| [**runUpgradePreflightApiV1UpgradesPreflightPostWithHttpInfo**](UpgradesApi.md#runUpgradePreflightApiV1UpgradesPreflightPostWithHttpInfo) | **POST** /api/v1/upgrades/preflight | Run Upgrade Preflight |



## getUpgradePolicyApiV1UpgradesPolicyGet

> UpgradePolicy getUpgradePolicyApiV1UpgradesPolicyGet(authorization, xAmeshCSRF)

Get Upgrade Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.UpgradesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        UpgradesApi apiInstance = new UpgradesApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            UpgradePolicy result = apiInstance.getUpgradePolicyApiV1UpgradesPolicyGet(authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling UpgradesApi#getUpgradePolicyApiV1UpgradesPolicyGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**UpgradePolicy**](UpgradePolicy.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getUpgradePolicyApiV1UpgradesPolicyGetWithHttpInfo

> ApiResponse<UpgradePolicy> getUpgradePolicyApiV1UpgradesPolicyGetWithHttpInfo(authorization, xAmeshCSRF)

Get Upgrade Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.UpgradesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        UpgradesApi apiInstance = new UpgradesApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<UpgradePolicy> response = apiInstance.getUpgradePolicyApiV1UpgradesPolicyGetWithHttpInfo(authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling UpgradesApi#getUpgradePolicyApiV1UpgradesPolicyGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**UpgradePolicy**](UpgradePolicy.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost

> ConfigurationMigration migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost(configurationMigrationRequest, authorization, xAmeshCSRF)

Migrate Upgrade Configuration

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.UpgradesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        UpgradesApi apiInstance = new UpgradesApi(defaultClient);
        ConfigurationMigrationRequest configurationMigrationRequest = new ConfigurationMigrationRequest(); // ConfigurationMigrationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ConfigurationMigration result = apiInstance.migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost(configurationMigrationRequest, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling UpgradesApi#migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **configurationMigrationRequest** | [**ConfigurationMigrationRequest**](ConfigurationMigrationRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**ConfigurationMigration**](ConfigurationMigration.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePostWithHttpInfo

> ApiResponse<ConfigurationMigration> migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePostWithHttpInfo(configurationMigrationRequest, authorization, xAmeshCSRF)

Migrate Upgrade Configuration

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.UpgradesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        UpgradesApi apiInstance = new UpgradesApi(defaultClient);
        ConfigurationMigrationRequest configurationMigrationRequest = new ConfigurationMigrationRequest(); // ConfigurationMigrationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<ConfigurationMigration> response = apiInstance.migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePostWithHttpInfo(configurationMigrationRequest, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling UpgradesApi#migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **configurationMigrationRequest** | [**ConfigurationMigrationRequest**](ConfigurationMigrationRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**ConfigurationMigration**](ConfigurationMigration.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet

> PersistedEventMigration previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet(authorization, xAmeshCSRF)

Preview Upgrade Event Upcast

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.UpgradesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        UpgradesApi apiInstance = new UpgradesApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            PersistedEventMigration result = apiInstance.previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet(authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling UpgradesApi#previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**PersistedEventMigration**](PersistedEventMigration.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGetWithHttpInfo

> ApiResponse<PersistedEventMigration> previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGetWithHttpInfo(authorization, xAmeshCSRF)

Preview Upgrade Event Upcast

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.UpgradesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        UpgradesApi apiInstance = new UpgradesApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<PersistedEventMigration> response = apiInstance.previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGetWithHttpInfo(authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling UpgradesApi#previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**PersistedEventMigration**](PersistedEventMigration.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## runUpgradeEventUpcastApiV1UpgradesEventsUpcastPost

> PersistedEventMigration runUpgradeEventUpcastApiV1UpgradesEventsUpcastPost(persistedEventMigrationRequest, authorization, xAmeshCSRF)

Run Upgrade Event Upcast

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.UpgradesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        UpgradesApi apiInstance = new UpgradesApi(defaultClient);
        PersistedEventMigrationRequest persistedEventMigrationRequest = new PersistedEventMigrationRequest(); // PersistedEventMigrationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            PersistedEventMigration result = apiInstance.runUpgradeEventUpcastApiV1UpgradesEventsUpcastPost(persistedEventMigrationRequest, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling UpgradesApi#runUpgradeEventUpcastApiV1UpgradesEventsUpcastPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **persistedEventMigrationRequest** | [**PersistedEventMigrationRequest**](PersistedEventMigrationRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**PersistedEventMigration**](PersistedEventMigration.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## runUpgradeEventUpcastApiV1UpgradesEventsUpcastPostWithHttpInfo

> ApiResponse<PersistedEventMigration> runUpgradeEventUpcastApiV1UpgradesEventsUpcastPostWithHttpInfo(persistedEventMigrationRequest, authorization, xAmeshCSRF)

Run Upgrade Event Upcast

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.UpgradesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        UpgradesApi apiInstance = new UpgradesApi(defaultClient);
        PersistedEventMigrationRequest persistedEventMigrationRequest = new PersistedEventMigrationRequest(); // PersistedEventMigrationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<PersistedEventMigration> response = apiInstance.runUpgradeEventUpcastApiV1UpgradesEventsUpcastPostWithHttpInfo(persistedEventMigrationRequest, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling UpgradesApi#runUpgradeEventUpcastApiV1UpgradesEventsUpcastPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **persistedEventMigrationRequest** | [**PersistedEventMigrationRequest**](PersistedEventMigrationRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**PersistedEventMigration**](PersistedEventMigration.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## runUpgradePostflightApiV1UpgradesPostflightPost

> UpgradeReport runUpgradePostflightApiV1UpgradesPostflightPost(upgradeReportRequest, authorization, xAmeshCSRF)

Run Upgrade Postflight

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.UpgradesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        UpgradesApi apiInstance = new UpgradesApi(defaultClient);
        UpgradeReportRequest upgradeReportRequest = new UpgradeReportRequest(); // UpgradeReportRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            UpgradeReport result = apiInstance.runUpgradePostflightApiV1UpgradesPostflightPost(upgradeReportRequest, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling UpgradesApi#runUpgradePostflightApiV1UpgradesPostflightPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **upgradeReportRequest** | [**UpgradeReportRequest**](UpgradeReportRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**UpgradeReport**](UpgradeReport.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## runUpgradePostflightApiV1UpgradesPostflightPostWithHttpInfo

> ApiResponse<UpgradeReport> runUpgradePostflightApiV1UpgradesPostflightPostWithHttpInfo(upgradeReportRequest, authorization, xAmeshCSRF)

Run Upgrade Postflight

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.UpgradesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        UpgradesApi apiInstance = new UpgradesApi(defaultClient);
        UpgradeReportRequest upgradeReportRequest = new UpgradeReportRequest(); // UpgradeReportRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<UpgradeReport> response = apiInstance.runUpgradePostflightApiV1UpgradesPostflightPostWithHttpInfo(upgradeReportRequest, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling UpgradesApi#runUpgradePostflightApiV1UpgradesPostflightPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **upgradeReportRequest** | [**UpgradeReportRequest**](UpgradeReportRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**UpgradeReport**](UpgradeReport.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## runUpgradePreflightApiV1UpgradesPreflightPost

> UpgradeReport runUpgradePreflightApiV1UpgradesPreflightPost(upgradeReportRequest, authorization, xAmeshCSRF)

Run Upgrade Preflight

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.UpgradesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        UpgradesApi apiInstance = new UpgradesApi(defaultClient);
        UpgradeReportRequest upgradeReportRequest = new UpgradeReportRequest(); // UpgradeReportRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            UpgradeReport result = apiInstance.runUpgradePreflightApiV1UpgradesPreflightPost(upgradeReportRequest, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling UpgradesApi#runUpgradePreflightApiV1UpgradesPreflightPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **upgradeReportRequest** | [**UpgradeReportRequest**](UpgradeReportRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**UpgradeReport**](UpgradeReport.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## runUpgradePreflightApiV1UpgradesPreflightPostWithHttpInfo

> ApiResponse<UpgradeReport> runUpgradePreflightApiV1UpgradesPreflightPostWithHttpInfo(upgradeReportRequest, authorization, xAmeshCSRF)

Run Upgrade Preflight

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.UpgradesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        UpgradesApi apiInstance = new UpgradesApi(defaultClient);
        UpgradeReportRequest upgradeReportRequest = new UpgradeReportRequest(); // UpgradeReportRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<UpgradeReport> response = apiInstance.runUpgradePreflightApiV1UpgradesPreflightPostWithHttpInfo(upgradeReportRequest, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling UpgradesApi#runUpgradePreflightApiV1UpgradesPreflightPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **upgradeReportRequest** | [**UpgradeReportRequest**](UpgradeReportRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**UpgradeReport**](UpgradeReport.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |
