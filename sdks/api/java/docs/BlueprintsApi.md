# BlueprintsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet**](BlueprintsApi.md#getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet) | **GET** /api/v1/blueprints/{blueprint_id}/{version} | Get Blueprint Version |
| [**getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGetWithHttpInfo**](BlueprintsApi.md#getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGetWithHttpInfo) | **GET** /api/v1/blueprints/{blueprint_id}/{version} | Get Blueprint Version |
| [**getBlueprintsApiV1BlueprintsGet**](BlueprintsApi.md#getBlueprintsApiV1BlueprintsGet) | **GET** /api/v1/blueprints | Get Blueprints |
| [**getBlueprintsApiV1BlueprintsGetWithHttpInfo**](BlueprintsApi.md#getBlueprintsApiV1BlueprintsGetWithHttpInfo) | **GET** /api/v1/blueprints | Get Blueprints |
| [**instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost**](BlueprintsApi.md#instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost) | **POST** /api/v1/blueprints/{blueprint_id}/{version}/instantiate | Instantiate Blueprint Draft |
| [**instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePostWithHttpInfo**](BlueprintsApi.md#instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePostWithHttpInfo) | **POST** /api/v1/blueprints/{blueprint_id}/{version}/instantiate | Instantiate Blueprint Draft |
| [**simulatePlaygroundApiV1PlaygroundSimulatePost**](BlueprintsApi.md#simulatePlaygroundApiV1PlaygroundSimulatePost) | **POST** /api/v1/playground/simulate | Simulate Playground |
| [**simulatePlaygroundApiV1PlaygroundSimulatePostWithHttpInfo**](BlueprintsApi.md#simulatePlaygroundApiV1PlaygroundSimulatePostWithHttpInfo) | **POST** /api/v1/playground/simulate | Simulate Playground |



## getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet

> BlueprintDefinition getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet(blueprintId, version, authorization, xAmeshCSRF, xAmeshTenant)

Get Blueprint Version

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BlueprintsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BlueprintsApi apiInstance = new BlueprintsApi(defaultClient);
        String blueprintId = "blueprintId_example"; // String |
        String version = "version_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            BlueprintDefinition result = apiInstance.getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet(blueprintId, version, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling BlueprintsApi#getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet");
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
| **blueprintId** | **String**|  | |
| **version** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**BlueprintDefinition**](BlueprintDefinition.md)


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

## getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGetWithHttpInfo

> ApiResponse<BlueprintDefinition> getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGetWithHttpInfo(blueprintId, version, authorization, xAmeshCSRF, xAmeshTenant)

Get Blueprint Version

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BlueprintsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BlueprintsApi apiInstance = new BlueprintsApi(defaultClient);
        String blueprintId = "blueprintId_example"; // String |
        String version = "version_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<BlueprintDefinition> response = apiInstance.getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGetWithHttpInfo(blueprintId, version, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling BlueprintsApi#getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet");
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
| **blueprintId** | **String**|  | |
| **version** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**BlueprintDefinition**](BlueprintDefinition.md)>


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


## getBlueprintsApiV1BlueprintsGet

> List<BlueprintSummary> getBlueprintsApiV1BlueprintsGet(q, source, authorization, xAmeshCSRF, xAmeshTenant)

Get Blueprints

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BlueprintsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BlueprintsApi apiInstance = new BlueprintsApi(defaultClient);
        String q = "q_example"; // String |
        BlueprintCatalogSource source = BlueprintCatalogSource.fromValue("BUILTIN"); // BlueprintCatalogSource |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<BlueprintSummary> result = apiInstance.getBlueprintsApiV1BlueprintsGet(q, source, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling BlueprintsApi#getBlueprintsApiV1BlueprintsGet");
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
| **q** | **String**|  | [optional] |
| **source** | [**BlueprintCatalogSource**](.md)|  | [optional] [enum: BUILTIN, ORGANIZATION, COMMUNITY] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;BlueprintSummary&gt;**](BlueprintSummary.md)


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

## getBlueprintsApiV1BlueprintsGetWithHttpInfo

> ApiResponse<List<BlueprintSummary>> getBlueprintsApiV1BlueprintsGetWithHttpInfo(q, source, authorization, xAmeshCSRF, xAmeshTenant)

Get Blueprints

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BlueprintsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BlueprintsApi apiInstance = new BlueprintsApi(defaultClient);
        String q = "q_example"; // String |
        BlueprintCatalogSource source = BlueprintCatalogSource.fromValue("BUILTIN"); // BlueprintCatalogSource |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<BlueprintSummary>> response = apiInstance.getBlueprintsApiV1BlueprintsGetWithHttpInfo(q, source, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling BlueprintsApi#getBlueprintsApiV1BlueprintsGet");
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
| **q** | **String**|  | [optional] |
| **source** | [**BlueprintCatalogSource**](.md)|  | [optional] [enum: BUILTIN, ORGANIZATION, COMMUNITY] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;BlueprintSummary&gt;**](BlueprintSummary.md)>


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


## instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost

> BlueprintDraftResponse instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost(blueprintId, version, blueprintInstantiationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Instantiate Blueprint Draft

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BlueprintsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BlueprintsApi apiInstance = new BlueprintsApi(defaultClient);
        String blueprintId = "blueprintId_example"; // String |
        String version = "version_example"; // String |
        BlueprintInstantiationRequest blueprintInstantiationRequest = new BlueprintInstantiationRequest(); // BlueprintInstantiationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            BlueprintDraftResponse result = apiInstance.instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost(blueprintId, version, blueprintInstantiationRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling BlueprintsApi#instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost");
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
| **blueprintId** | **String**|  | |
| **version** | **String**|  | |
| **blueprintInstantiationRequest** | [**BlueprintInstantiationRequest**](BlueprintInstantiationRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**BlueprintDraftResponse**](BlueprintDraftResponse.md)


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

## instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePostWithHttpInfo

> ApiResponse<BlueprintDraftResponse> instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePostWithHttpInfo(blueprintId, version, blueprintInstantiationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Instantiate Blueprint Draft

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BlueprintsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BlueprintsApi apiInstance = new BlueprintsApi(defaultClient);
        String blueprintId = "blueprintId_example"; // String |
        String version = "version_example"; // String |
        BlueprintInstantiationRequest blueprintInstantiationRequest = new BlueprintInstantiationRequest(); // BlueprintInstantiationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<BlueprintDraftResponse> response = apiInstance.instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePostWithHttpInfo(blueprintId, version, blueprintInstantiationRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling BlueprintsApi#instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost");
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
| **blueprintId** | **String**|  | |
| **version** | **String**|  | |
| **blueprintInstantiationRequest** | [**BlueprintInstantiationRequest**](BlueprintInstantiationRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**BlueprintDraftResponse**](BlueprintDraftResponse.md)>


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


## simulatePlaygroundApiV1PlaygroundSimulatePost

> PlaygroundSimulationResponse simulatePlaygroundApiV1PlaygroundSimulatePost(playgroundSimulationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Simulate Playground

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BlueprintsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BlueprintsApi apiInstance = new BlueprintsApi(defaultClient);
        PlaygroundSimulationRequest playgroundSimulationRequest = new PlaygroundSimulationRequest(); // PlaygroundSimulationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PlaygroundSimulationResponse result = apiInstance.simulatePlaygroundApiV1PlaygroundSimulatePost(playgroundSimulationRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling BlueprintsApi#simulatePlaygroundApiV1PlaygroundSimulatePost");
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
| **playgroundSimulationRequest** | [**PlaygroundSimulationRequest**](PlaygroundSimulationRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**PlaygroundSimulationResponse**](PlaygroundSimulationResponse.md)


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

## simulatePlaygroundApiV1PlaygroundSimulatePostWithHttpInfo

> ApiResponse<PlaygroundSimulationResponse> simulatePlaygroundApiV1PlaygroundSimulatePostWithHttpInfo(playgroundSimulationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Simulate Playground

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BlueprintsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BlueprintsApi apiInstance = new BlueprintsApi(defaultClient);
        PlaygroundSimulationRequest playgroundSimulationRequest = new PlaygroundSimulationRequest(); // PlaygroundSimulationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PlaygroundSimulationResponse> response = apiInstance.simulatePlaygroundApiV1PlaygroundSimulatePostWithHttpInfo(playgroundSimulationRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling BlueprintsApi#simulatePlaygroundApiV1PlaygroundSimulatePost");
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
| **playgroundSimulationRequest** | [**PlaygroundSimulationRequest**](PlaygroundSimulationRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**PlaygroundSimulationResponse**](PlaygroundSimulationResponse.md)>


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
