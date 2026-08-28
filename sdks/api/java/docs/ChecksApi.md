# ChecksApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getCheckComplianceApiV1CheckComplianceGet**](ChecksApi.md#getCheckComplianceApiV1CheckComplianceGet) | **GET** /api/v1/check-compliance | Get Check Compliance |
| [**getCheckComplianceApiV1CheckComplianceGetWithHttpInfo**](ChecksApi.md#getCheckComplianceApiV1CheckComplianceGetWithHttpInfo) | **GET** /api/v1/check-compliance | Get Check Compliance |
| [**listCheckEvaluationsApiV1CheckEvaluationsGet**](ChecksApi.md#listCheckEvaluationsApiV1CheckEvaluationsGet) | **GET** /api/v1/check-evaluations | List Check Evaluations |
| [**listCheckEvaluationsApiV1CheckEvaluationsGetWithHttpInfo**](ChecksApi.md#listCheckEvaluationsApiV1CheckEvaluationsGetWithHttpInfo) | **GET** /api/v1/check-evaluations | List Check Evaluations |
| [**listCheckPoliciesApiV1CheckPoliciesGet**](ChecksApi.md#listCheckPoliciesApiV1CheckPoliciesGet) | **GET** /api/v1/check-policies | List Check Policies |
| [**listCheckPoliciesApiV1CheckPoliciesGetWithHttpInfo**](ChecksApi.md#listCheckPoliciesApiV1CheckPoliciesGetWithHttpInfo) | **GET** /api/v1/check-policies | List Check Policies |
| [**upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut**](ChecksApi.md#upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut) | **PUT** /api/v1/check-policies/{namespace}/{policy_key} | Upsert Check Policy |
| [**upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPutWithHttpInfo**](ChecksApi.md#upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPutWithHttpInfo) | **PUT** /api/v1/check-policies/{namespace}/{policy_key} | Upsert Check Policy |



## getCheckComplianceApiV1CheckComplianceGet

> List<CheckComplianceSummary> getCheckComplianceApiV1CheckComplianceGet(groupBy, fromTime, toTime, namespace, flowId, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Check Compliance

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ChecksApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ChecksApi apiInstance = new ChecksApi(defaultClient);
        String groupBy = "flow"; // String |
        OffsetDateTime fromTime = OffsetDateTime.now(); // OffsetDateTime |
        OffsetDateTime toTime = OffsetDateTime.now(); // OffsetDateTime |
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<CheckComplianceSummary> result = apiInstance.getCheckComplianceApiV1CheckComplianceGet(groupBy, fromTime, toTime, namespace, flowId, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ChecksApi#getCheckComplianceApiV1CheckComplianceGet");
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
| **groupBy** | **String**|  | [optional] [default to flow] |
| **fromTime** | **OffsetDateTime**|  | [optional] |
| **toTime** | **OffsetDateTime**|  | [optional] |
| **namespace** | **String**|  | [optional] |
| **flowId** | **String**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;CheckComplianceSummary&gt;**


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

## getCheckComplianceApiV1CheckComplianceGetWithHttpInfo

> ApiResponse<List<CheckComplianceSummary>> getCheckComplianceApiV1CheckComplianceGetWithHttpInfo(groupBy, fromTime, toTime, namespace, flowId, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Check Compliance

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ChecksApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ChecksApi apiInstance = new ChecksApi(defaultClient);
        String groupBy = "flow"; // String |
        OffsetDateTime fromTime = OffsetDateTime.now(); // OffsetDateTime |
        OffsetDateTime toTime = OffsetDateTime.now(); // OffsetDateTime |
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<CheckComplianceSummary>> response = apiInstance.getCheckComplianceApiV1CheckComplianceGetWithHttpInfo(groupBy, fromTime, toTime, namespace, flowId, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ChecksApi#getCheckComplianceApiV1CheckComplianceGet");
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
| **groupBy** | **String**|  | [optional] [default to flow] |
| **fromTime** | **OffsetDateTime**|  | [optional] |
| **toTime** | **OffsetDateTime**|  | [optional] |
| **namespace** | **String**|  | [optional] |
| **flowId** | **String**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;CheckComplianceSummary&gt;**>


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


## listCheckEvaluationsApiV1CheckEvaluationsGet

> List<CheckEvaluation> listCheckEvaluationsApiV1CheckEvaluationsGet(namespace, flowId, executionId, outcome, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Check Evaluations

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ChecksApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ChecksApi apiInstance = new ChecksApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        UUID executionId = UUID.randomUUID(); // UUID |
        CheckOutcome outcome = CheckOutcome.fromValue("PASS"); // CheckOutcome |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<CheckEvaluation> result = apiInstance.listCheckEvaluationsApiV1CheckEvaluationsGet(namespace, flowId, executionId, outcome, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ChecksApi#listCheckEvaluationsApiV1CheckEvaluationsGet");
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
| **flowId** | **String**|  | [optional] |
| **executionId** | **UUID**|  | [optional] |
| **outcome** | **CheckOutcome**|  | [optional] [enum: PASS, WARN, FAIL, ERROR] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;CheckEvaluation&gt;**


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

## listCheckEvaluationsApiV1CheckEvaluationsGetWithHttpInfo

> ApiResponse<List<CheckEvaluation>> listCheckEvaluationsApiV1CheckEvaluationsGetWithHttpInfo(namespace, flowId, executionId, outcome, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Check Evaluations

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ChecksApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ChecksApi apiInstance = new ChecksApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        UUID executionId = UUID.randomUUID(); // UUID |
        CheckOutcome outcome = CheckOutcome.fromValue("PASS"); // CheckOutcome |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<CheckEvaluation>> response = apiInstance.listCheckEvaluationsApiV1CheckEvaluationsGetWithHttpInfo(namespace, flowId, executionId, outcome, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ChecksApi#listCheckEvaluationsApiV1CheckEvaluationsGet");
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
| **flowId** | **String**|  | [optional] |
| **executionId** | **UUID**|  | [optional] |
| **outcome** | **CheckOutcome**|  | [optional] [enum: PASS, WARN, FAIL, ERROR] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;CheckEvaluation&gt;**>


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


## listCheckPoliciesApiV1CheckPoliciesGet

> List<NamespaceCheckPolicy> listCheckPoliciesApiV1CheckPoliciesGet(namespace, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Check Policies

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ChecksApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ChecksApi apiInstance = new ChecksApi(defaultClient);
        String namespace = "namespace_example"; // String |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<NamespaceCheckPolicy> result = apiInstance.listCheckPoliciesApiV1CheckPoliciesGet(namespace, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ChecksApi#listCheckPoliciesApiV1CheckPoliciesGet");
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
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;NamespaceCheckPolicy&gt;**


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

## listCheckPoliciesApiV1CheckPoliciesGetWithHttpInfo

> ApiResponse<List<NamespaceCheckPolicy>> listCheckPoliciesApiV1CheckPoliciesGetWithHttpInfo(namespace, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Check Policies

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ChecksApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ChecksApi apiInstance = new ChecksApi(defaultClient);
        String namespace = "namespace_example"; // String |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<NamespaceCheckPolicy>> response = apiInstance.listCheckPoliciesApiV1CheckPoliciesGetWithHttpInfo(namespace, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ChecksApi#listCheckPoliciesApiV1CheckPoliciesGet");
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
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;NamespaceCheckPolicy&gt;**>


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


## upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut

> NamespaceCheckPolicy upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut(namespace, policyKey, checkPolicyUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant)

Upsert Check Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ChecksApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ChecksApi apiInstance = new ChecksApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String policyKey = "policyKey_example"; // String |
        CheckPolicyUpsertRequest checkPolicyUpsertRequest = new CheckPolicyUpsertRequest(); // CheckPolicyUpsertRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            NamespaceCheckPolicy result = apiInstance.upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut(namespace, policyKey, checkPolicyUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ChecksApi#upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut");
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
| **namespace** | **String**|  | |
| **policyKey** | **String**|  | |
| **checkPolicyUpsertRequest** | **CheckPolicyUpsertRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**NamespaceCheckPolicy**


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

## upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPutWithHttpInfo

> ApiResponse<NamespaceCheckPolicy> upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPutWithHttpInfo(namespace, policyKey, checkPolicyUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant)

Upsert Check Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ChecksApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ChecksApi apiInstance = new ChecksApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String policyKey = "policyKey_example"; // String |
        CheckPolicyUpsertRequest checkPolicyUpsertRequest = new CheckPolicyUpsertRequest(); // CheckPolicyUpsertRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<NamespaceCheckPolicy> response = apiInstance.upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPutWithHttpInfo(namespace, policyKey, checkPolicyUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ChecksApi#upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut");
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
| **namespace** | **String**|  | |
| **policyKey** | **String**|  | |
| **checkPolicyUpsertRequest** | **CheckPolicyUpsertRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**NamespaceCheckPolicy**>


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
