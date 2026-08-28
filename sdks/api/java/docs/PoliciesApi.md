# PoliciesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createAdmissionPolicyApiV1PoliciesPost**](PoliciesApi.md#createAdmissionPolicyApiV1PoliciesPost) | **POST** /api/v1/policies | Create Admission Policy |
| [**createAdmissionPolicyApiV1PoliciesPostWithHttpInfo**](PoliciesApi.md#createAdmissionPolicyApiV1PoliciesPostWithHttpInfo) | **POST** /api/v1/policies | Create Admission Policy |
| [**evaluateAdmissionPoliciesApiV1PoliciesEvaluatePost**](PoliciesApi.md#evaluateAdmissionPoliciesApiV1PoliciesEvaluatePost) | **POST** /api/v1/policies/evaluate | Evaluate Admission Policies |
| [**evaluateAdmissionPoliciesApiV1PoliciesEvaluatePostWithHttpInfo**](PoliciesApi.md#evaluateAdmissionPoliciesApiV1PoliciesEvaluatePostWithHttpInfo) | **POST** /api/v1/policies/evaluate | Evaluate Admission Policies |
| [**getAdmissionPolicyApiV1PoliciesPolicyKeyGet**](PoliciesApi.md#getAdmissionPolicyApiV1PoliciesPolicyKeyGet) | **GET** /api/v1/policies/{policy_key} | Get Admission Policy |
| [**getAdmissionPolicyApiV1PoliciesPolicyKeyGetWithHttpInfo**](PoliciesApi.md#getAdmissionPolicyApiV1PoliciesPolicyKeyGetWithHttpInfo) | **GET** /api/v1/policies/{policy_key} | Get Admission Policy |
| [**listAdmissionPoliciesApiV1PoliciesGet**](PoliciesApi.md#listAdmissionPoliciesApiV1PoliciesGet) | **GET** /api/v1/policies | List Admission Policies |
| [**listAdmissionPoliciesApiV1PoliciesGetWithHttpInfo**](PoliciesApi.md#listAdmissionPoliciesApiV1PoliciesGetWithHttpInfo) | **GET** /api/v1/policies | List Admission Policies |
| [**listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet**](PoliciesApi.md#listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet) | **GET** /api/v1/policies/decisions | List Admission Policy Decisions |
| [**listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGetWithHttpInfo**](PoliciesApi.md#listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGetWithHttpInfo) | **GET** /api/v1/policies/decisions | List Admission Policy Decisions |
| [**testAdmissionPolicyApiV1PoliciesPolicyKeyTestPost**](PoliciesApi.md#testAdmissionPolicyApiV1PoliciesPolicyKeyTestPost) | **POST** /api/v1/policies/{policy_key}/test | Test Admission Policy |
| [**testAdmissionPolicyApiV1PoliciesPolicyKeyTestPostWithHttpInfo**](PoliciesApi.md#testAdmissionPolicyApiV1PoliciesPolicyKeyTestPostWithHttpInfo) | **POST** /api/v1/policies/{policy_key}/test | Test Admission Policy |
| [**updateAdmissionPolicyApiV1PoliciesPolicyKeyPut**](PoliciesApi.md#updateAdmissionPolicyApiV1PoliciesPolicyKeyPut) | **PUT** /api/v1/policies/{policy_key} | Update Admission Policy |
| [**updateAdmissionPolicyApiV1PoliciesPolicyKeyPutWithHttpInfo**](PoliciesApi.md#updateAdmissionPolicyApiV1PoliciesPolicyKeyPutWithHttpInfo) | **PUT** /api/v1/policies/{policy_key} | Update Admission Policy |
| [**validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost**](PoliciesApi.md#validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost) | **POST** /api/v1/policies/flows/validate | Validate Flow Admission Policy |
| [**validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePostWithHttpInfo**](PoliciesApi.md#validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePostWithHttpInfo) | **POST** /api/v1/policies/flows/validate | Validate Flow Admission Policy |



## createAdmissionPolicyApiV1PoliciesPost

> PolicyRevision createAdmissionPolicyApiV1PoliciesPost(policyDocument, authorization, xAmeshCSRF, xAmeshTenant)

Create Admission Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PoliciesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PoliciesApi apiInstance = new PoliciesApi(defaultClient);
        PolicyDocument policyDocument = new PolicyDocument(); // PolicyDocument |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PolicyRevision result = apiInstance.createAdmissionPolicyApiV1PoliciesPost(policyDocument, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PoliciesApi#createAdmissionPolicyApiV1PoliciesPost");
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
| **policyDocument** | **PolicyDocument**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**PolicyRevision**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## createAdmissionPolicyApiV1PoliciesPostWithHttpInfo

> ApiResponse<PolicyRevision> createAdmissionPolicyApiV1PoliciesPostWithHttpInfo(policyDocument, authorization, xAmeshCSRF, xAmeshTenant)

Create Admission Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PoliciesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PoliciesApi apiInstance = new PoliciesApi(defaultClient);
        PolicyDocument policyDocument = new PolicyDocument(); // PolicyDocument |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PolicyRevision> response = apiInstance.createAdmissionPolicyApiV1PoliciesPostWithHttpInfo(policyDocument, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PoliciesApi#createAdmissionPolicyApiV1PoliciesPost");
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
| **policyDocument** | **PolicyDocument**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**PolicyRevision**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## evaluateAdmissionPoliciesApiV1PoliciesEvaluatePost

> PolicyDecision evaluateAdmissionPoliciesApiV1PoliciesEvaluatePost(policyEvaluationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Evaluate Admission Policies

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PoliciesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PoliciesApi apiInstance = new PoliciesApi(defaultClient);
        PolicyEvaluationRequest policyEvaluationRequest = new PolicyEvaluationRequest(); // PolicyEvaluationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PolicyDecision result = apiInstance.evaluateAdmissionPoliciesApiV1PoliciesEvaluatePost(policyEvaluationRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PoliciesApi#evaluateAdmissionPoliciesApiV1PoliciesEvaluatePost");
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
| **policyEvaluationRequest** | **PolicyEvaluationRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**PolicyDecision**


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

## evaluateAdmissionPoliciesApiV1PoliciesEvaluatePostWithHttpInfo

> ApiResponse<PolicyDecision> evaluateAdmissionPoliciesApiV1PoliciesEvaluatePostWithHttpInfo(policyEvaluationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Evaluate Admission Policies

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PoliciesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PoliciesApi apiInstance = new PoliciesApi(defaultClient);
        PolicyEvaluationRequest policyEvaluationRequest = new PolicyEvaluationRequest(); // PolicyEvaluationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PolicyDecision> response = apiInstance.evaluateAdmissionPoliciesApiV1PoliciesEvaluatePostWithHttpInfo(policyEvaluationRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PoliciesApi#evaluateAdmissionPoliciesApiV1PoliciesEvaluatePost");
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
| **policyEvaluationRequest** | **PolicyEvaluationRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**PolicyDecision**>


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


## getAdmissionPolicyApiV1PoliciesPolicyKeyGet

> PolicyRevision getAdmissionPolicyApiV1PoliciesPolicyKeyGet(policyKey, revision, authorization, xAmeshCSRF, xAmeshTenant)

Get Admission Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PoliciesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PoliciesApi apiInstance = new PoliciesApi(defaultClient);
        String policyKey = "policyKey_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PolicyRevision result = apiInstance.getAdmissionPolicyApiV1PoliciesPolicyKeyGet(policyKey, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PoliciesApi#getAdmissionPolicyApiV1PoliciesPolicyKeyGet");
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
| **policyKey** | **String**|  | |
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**PolicyRevision**


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

## getAdmissionPolicyApiV1PoliciesPolicyKeyGetWithHttpInfo

> ApiResponse<PolicyRevision> getAdmissionPolicyApiV1PoliciesPolicyKeyGetWithHttpInfo(policyKey, revision, authorization, xAmeshCSRF, xAmeshTenant)

Get Admission Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PoliciesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PoliciesApi apiInstance = new PoliciesApi(defaultClient);
        String policyKey = "policyKey_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PolicyRevision> response = apiInstance.getAdmissionPolicyApiV1PoliciesPolicyKeyGetWithHttpInfo(policyKey, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PoliciesApi#getAdmissionPolicyApiV1PoliciesPolicyKeyGet");
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
| **policyKey** | **String**|  | |
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**PolicyRevision**>


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


## listAdmissionPoliciesApiV1PoliciesGet

> List<PolicyRevision> listAdmissionPoliciesApiV1PoliciesGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

List Admission Policies

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PoliciesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PoliciesApi apiInstance = new PoliciesApi(defaultClient);
        String namespace = "default"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<PolicyRevision> result = apiInstance.listAdmissionPoliciesApiV1PoliciesGet(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PoliciesApi#listAdmissionPoliciesApiV1PoliciesGet");
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
| **namespace** | **String**|  | [optional] [default to default] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;PolicyRevision&gt;**


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

## listAdmissionPoliciesApiV1PoliciesGetWithHttpInfo

> ApiResponse<List<PolicyRevision>> listAdmissionPoliciesApiV1PoliciesGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant)

List Admission Policies

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PoliciesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PoliciesApi apiInstance = new PoliciesApi(defaultClient);
        String namespace = "default"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<PolicyRevision>> response = apiInstance.listAdmissionPoliciesApiV1PoliciesGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PoliciesApi#listAdmissionPoliciesApiV1PoliciesGet");
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
| **namespace** | **String**|  | [optional] [default to default] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;PolicyRevision&gt;**>


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


## listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet

> List<PolicyDecision> listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Admission Policy Decisions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PoliciesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PoliciesApi apiInstance = new PoliciesApi(defaultClient);
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<PolicyDecision> result = apiInstance.listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet(limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PoliciesApi#listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet");
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
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;PolicyDecision&gt;**


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

## listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGetWithHttpInfo

> ApiResponse<List<PolicyDecision>> listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGetWithHttpInfo(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Admission Policy Decisions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PoliciesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PoliciesApi apiInstance = new PoliciesApi(defaultClient);
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<PolicyDecision>> response = apiInstance.listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGetWithHttpInfo(limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PoliciesApi#listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet");
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
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;PolicyDecision&gt;**>


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


## testAdmissionPolicyApiV1PoliciesPolicyKeyTestPost

> PolicyFixtureResult testAdmissionPolicyApiV1PoliciesPolicyKeyTestPost(policyKey, policyFixture, revision, authorization, xAmeshCSRF, xAmeshTenant)

Test Admission Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PoliciesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PoliciesApi apiInstance = new PoliciesApi(defaultClient);
        String policyKey = "policyKey_example"; // String |
        PolicyFixture policyFixture = new PolicyFixture(); // PolicyFixture |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PolicyFixtureResult result = apiInstance.testAdmissionPolicyApiV1PoliciesPolicyKeyTestPost(policyKey, policyFixture, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PoliciesApi#testAdmissionPolicyApiV1PoliciesPolicyKeyTestPost");
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
| **policyKey** | **String**|  | |
| **policyFixture** | **PolicyFixture**|  | |
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**PolicyFixtureResult**


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

## testAdmissionPolicyApiV1PoliciesPolicyKeyTestPostWithHttpInfo

> ApiResponse<PolicyFixtureResult> testAdmissionPolicyApiV1PoliciesPolicyKeyTestPostWithHttpInfo(policyKey, policyFixture, revision, authorization, xAmeshCSRF, xAmeshTenant)

Test Admission Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PoliciesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PoliciesApi apiInstance = new PoliciesApi(defaultClient);
        String policyKey = "policyKey_example"; // String |
        PolicyFixture policyFixture = new PolicyFixture(); // PolicyFixture |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PolicyFixtureResult> response = apiInstance.testAdmissionPolicyApiV1PoliciesPolicyKeyTestPostWithHttpInfo(policyKey, policyFixture, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PoliciesApi#testAdmissionPolicyApiV1PoliciesPolicyKeyTestPost");
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
| **policyKey** | **String**|  | |
| **policyFixture** | **PolicyFixture**|  | |
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**PolicyFixtureResult**>


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


## updateAdmissionPolicyApiV1PoliciesPolicyKeyPut

> PolicyRevision updateAdmissionPolicyApiV1PoliciesPolicyKeyPut(policyKey, policyDocument, authorization, xAmeshCSRF, xAmeshTenant)

Update Admission Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PoliciesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PoliciesApi apiInstance = new PoliciesApi(defaultClient);
        String policyKey = "policyKey_example"; // String |
        PolicyDocument policyDocument = new PolicyDocument(); // PolicyDocument |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PolicyRevision result = apiInstance.updateAdmissionPolicyApiV1PoliciesPolicyKeyPut(policyKey, policyDocument, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PoliciesApi#updateAdmissionPolicyApiV1PoliciesPolicyKeyPut");
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
| **policyKey** | **String**|  | |
| **policyDocument** | **PolicyDocument**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**PolicyRevision**


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

## updateAdmissionPolicyApiV1PoliciesPolicyKeyPutWithHttpInfo

> ApiResponse<PolicyRevision> updateAdmissionPolicyApiV1PoliciesPolicyKeyPutWithHttpInfo(policyKey, policyDocument, authorization, xAmeshCSRF, xAmeshTenant)

Update Admission Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PoliciesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PoliciesApi apiInstance = new PoliciesApi(defaultClient);
        String policyKey = "policyKey_example"; // String |
        PolicyDocument policyDocument = new PolicyDocument(); // PolicyDocument |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PolicyRevision> response = apiInstance.updateAdmissionPolicyApiV1PoliciesPolicyKeyPutWithHttpInfo(policyKey, policyDocument, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PoliciesApi#updateAdmissionPolicyApiV1PoliciesPolicyKeyPut");
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
| **policyKey** | **String**|  | |
| **policyDocument** | **PolicyDocument**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**PolicyRevision**>


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


## validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost

> PolicyDecision validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost(authorization, xAmeshCSRF, xAmeshTenant)

Validate Flow Admission Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PoliciesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PoliciesApi apiInstance = new PoliciesApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PolicyDecision result = apiInstance.validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PoliciesApi#validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost");
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
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**PolicyDecision**


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

## validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePostWithHttpInfo

> ApiResponse<PolicyDecision> validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePostWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

Validate Flow Admission Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PoliciesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PoliciesApi apiInstance = new PoliciesApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PolicyDecision> response = apiInstance.validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePostWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PoliciesApi#validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost");
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
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**PolicyDecision**>


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
