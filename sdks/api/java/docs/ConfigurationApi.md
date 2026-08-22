# ConfigurationApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet**](ConfigurationApi.md#evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet) | **GET** /api/v1/feature-flags/{key}/evaluate | Evaluate Feature Flag |
| [**evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGetWithHttpInfo**](ConfigurationApi.md#evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGetWithHttpInfo) | **GET** /api/v1/feature-flags/{key}/evaluate | Evaluate Feature Flag |
| [**getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet**](ConfigurationApi.md#getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet) | **GET** /api/v1/configuration/diagnostics | Get Configuration Diagnostics |
| [**getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGetWithHttpInfo**](ConfigurationApi.md#getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGetWithHttpInfo) | **GET** /api/v1/configuration/diagnostics | Get Configuration Diagnostics |
| [**getEffectiveConfigurationApiV1ConfigurationGet**](ConfigurationApi.md#getEffectiveConfigurationApiV1ConfigurationGet) | **GET** /api/v1/configuration | Get Effective Configuration |
| [**getEffectiveConfigurationApiV1ConfigurationGetWithHttpInfo**](ConfigurationApi.md#getEffectiveConfigurationApiV1ConfigurationGetWithHttpInfo) | **GET** /api/v1/configuration | Get Effective Configuration |
| [**listFeatureFlagsApiV1FeatureFlagsGet**](ConfigurationApi.md#listFeatureFlagsApiV1FeatureFlagsGet) | **GET** /api/v1/feature-flags | List Feature Flags |
| [**listFeatureFlagsApiV1FeatureFlagsGetWithHttpInfo**](ConfigurationApi.md#listFeatureFlagsApiV1FeatureFlagsGetWithHttpInfo) | **GET** /api/v1/feature-flags | List Feature Flags |
| [**putFeatureFlagApiV1FeatureFlagsKeyPut**](ConfigurationApi.md#putFeatureFlagApiV1FeatureFlagsKeyPut) | **PUT** /api/v1/feature-flags/{key} | Put Feature Flag |
| [**putFeatureFlagApiV1FeatureFlagsKeyPutWithHttpInfo**](ConfigurationApi.md#putFeatureFlagApiV1FeatureFlagsKeyPutWithHttpInfo) | **PUT** /api/v1/feature-flags/{key} | Put Feature Flag |
| [**reloadConfigurationApiV1ConfigurationReloadPost**](ConfigurationApi.md#reloadConfigurationApiV1ConfigurationReloadPost) | **POST** /api/v1/configuration/reload | Reload Configuration |
| [**reloadConfigurationApiV1ConfigurationReloadPostWithHttpInfo**](ConfigurationApi.md#reloadConfigurationApiV1ConfigurationReloadPostWithHttpInfo) | **POST** /api/v1/configuration/reload | Reload Configuration |



## evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet

> FeatureFlagDecision evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet(key, namespace, _default, authorization, xAmeshCSRF, xAmeshTenant)

Evaluate Feature Flag

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ConfigurationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ConfigurationApi apiInstance = new ConfigurationApi(defaultClient);
        String key = "key_example"; // String |
        String namespace = "namespace_example"; // String |
        Boolean _default = false; // Boolean |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            FeatureFlagDecision result = apiInstance.evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet(key, namespace, _default, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ConfigurationApi#evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet");
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
| **key** | **String**|  | |
| **namespace** | **String**|  | [optional] |
| **_default** | **Boolean**|  | [optional] [default to false] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**FeatureFlagDecision**](FeatureFlagDecision.md)


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

## evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGetWithHttpInfo

> ApiResponse<FeatureFlagDecision> evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGetWithHttpInfo(key, namespace, _default, authorization, xAmeshCSRF, xAmeshTenant)

Evaluate Feature Flag

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ConfigurationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ConfigurationApi apiInstance = new ConfigurationApi(defaultClient);
        String key = "key_example"; // String |
        String namespace = "namespace_example"; // String |
        Boolean _default = false; // Boolean |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<FeatureFlagDecision> response = apiInstance.evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGetWithHttpInfo(key, namespace, _default, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ConfigurationApi#evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet");
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
| **key** | **String**|  | |
| **namespace** | **String**|  | [optional] |
| **_default** | **Boolean**|  | [optional] [default to false] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**FeatureFlagDecision**](FeatureFlagDecision.md)>


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


## getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet

> ConfigurationDiagnosticBundle getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Get Configuration Diagnostics

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ConfigurationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ConfigurationApi apiInstance = new ConfigurationApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ConfigurationDiagnosticBundle result = apiInstance.getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ConfigurationApi#getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet");
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
| **namespace** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**ConfigurationDiagnosticBundle**](ConfigurationDiagnosticBundle.md)


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

## getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGetWithHttpInfo

> ApiResponse<ConfigurationDiagnosticBundle> getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Get Configuration Diagnostics

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ConfigurationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ConfigurationApi apiInstance = new ConfigurationApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ConfigurationDiagnosticBundle> response = apiInstance.getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ConfigurationApi#getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet");
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
| **namespace** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**ConfigurationDiagnosticBundle**](ConfigurationDiagnosticBundle.md)>


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


## getEffectiveConfigurationApiV1ConfigurationGet

> ConfigurationSnapshot getEffectiveConfigurationApiV1ConfigurationGet(authorization, xAmeshCSRF)

Get Effective Configuration

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ConfigurationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ConfigurationApi apiInstance = new ConfigurationApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ConfigurationSnapshot result = apiInstance.getEffectiveConfigurationApiV1ConfigurationGet(authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ConfigurationApi#getEffectiveConfigurationApiV1ConfigurationGet");
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

[**ConfigurationSnapshot**](ConfigurationSnapshot.md)


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

## getEffectiveConfigurationApiV1ConfigurationGetWithHttpInfo

> ApiResponse<ConfigurationSnapshot> getEffectiveConfigurationApiV1ConfigurationGetWithHttpInfo(authorization, xAmeshCSRF)

Get Effective Configuration

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ConfigurationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ConfigurationApi apiInstance = new ConfigurationApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<ConfigurationSnapshot> response = apiInstance.getEffectiveConfigurationApiV1ConfigurationGetWithHttpInfo(authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ConfigurationApi#getEffectiveConfigurationApiV1ConfigurationGet");
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

ApiResponse<[**ConfigurationSnapshot**](ConfigurationSnapshot.md)>


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


## listFeatureFlagsApiV1FeatureFlagsGet

> List<FeatureFlag> listFeatureFlagsApiV1FeatureFlagsGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

List Feature Flags

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ConfigurationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ConfigurationApi apiInstance = new ConfigurationApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<FeatureFlag> result = apiInstance.listFeatureFlagsApiV1FeatureFlagsGet(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ConfigurationApi#listFeatureFlagsApiV1FeatureFlagsGet");
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
| **namespace** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;FeatureFlag&gt;**](FeatureFlag.md)


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

## listFeatureFlagsApiV1FeatureFlagsGetWithHttpInfo

> ApiResponse<List<FeatureFlag>> listFeatureFlagsApiV1FeatureFlagsGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant)

List Feature Flags

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ConfigurationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ConfigurationApi apiInstance = new ConfigurationApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<FeatureFlag>> response = apiInstance.listFeatureFlagsApiV1FeatureFlagsGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ConfigurationApi#listFeatureFlagsApiV1FeatureFlagsGet");
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
| **namespace** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;FeatureFlag&gt;**](FeatureFlag.md)>


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


## putFeatureFlagApiV1FeatureFlagsKeyPut

> FeatureFlag putFeatureFlagApiV1FeatureFlagsKeyPut(key, featureFlagUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant)

Put Feature Flag

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ConfigurationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ConfigurationApi apiInstance = new ConfigurationApi(defaultClient);
        String key = "key_example"; // String |
        FeatureFlagUpsertRequest featureFlagUpsertRequest = new FeatureFlagUpsertRequest(); // FeatureFlagUpsertRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            FeatureFlag result = apiInstance.putFeatureFlagApiV1FeatureFlagsKeyPut(key, featureFlagUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ConfigurationApi#putFeatureFlagApiV1FeatureFlagsKeyPut");
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
| **key** | **String**|  | |
| **featureFlagUpsertRequest** | [**FeatureFlagUpsertRequest**](FeatureFlagUpsertRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**FeatureFlag**](FeatureFlag.md)


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

## putFeatureFlagApiV1FeatureFlagsKeyPutWithHttpInfo

> ApiResponse<FeatureFlag> putFeatureFlagApiV1FeatureFlagsKeyPutWithHttpInfo(key, featureFlagUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant)

Put Feature Flag

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ConfigurationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ConfigurationApi apiInstance = new ConfigurationApi(defaultClient);
        String key = "key_example"; // String |
        FeatureFlagUpsertRequest featureFlagUpsertRequest = new FeatureFlagUpsertRequest(); // FeatureFlagUpsertRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<FeatureFlag> response = apiInstance.putFeatureFlagApiV1FeatureFlagsKeyPutWithHttpInfo(key, featureFlagUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ConfigurationApi#putFeatureFlagApiV1FeatureFlagsKeyPut");
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
| **key** | **String**|  | |
| **featureFlagUpsertRequest** | [**FeatureFlagUpsertRequest**](FeatureFlagUpsertRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**FeatureFlag**](FeatureFlag.md)>


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


## reloadConfigurationApiV1ConfigurationReloadPost

> ConfigurationSnapshot reloadConfigurationApiV1ConfigurationReloadPost(authorization, xAmeshCSRF)

Reload Configuration

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ConfigurationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ConfigurationApi apiInstance = new ConfigurationApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ConfigurationSnapshot result = apiInstance.reloadConfigurationApiV1ConfigurationReloadPost(authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ConfigurationApi#reloadConfigurationApiV1ConfigurationReloadPost");
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

[**ConfigurationSnapshot**](ConfigurationSnapshot.md)


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

## reloadConfigurationApiV1ConfigurationReloadPostWithHttpInfo

> ApiResponse<ConfigurationSnapshot> reloadConfigurationApiV1ConfigurationReloadPostWithHttpInfo(authorization, xAmeshCSRF)

Reload Configuration

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ConfigurationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ConfigurationApi apiInstance = new ConfigurationApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<ConfigurationSnapshot> response = apiInstance.reloadConfigurationApiV1ConfigurationReloadPostWithHttpInfo(authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ConfigurationApi#reloadConfigurationApiV1ConfigurationReloadPost");
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

ApiResponse<[**ConfigurationSnapshot**](ConfigurationSnapshot.md)>


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
