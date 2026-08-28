# ReleasesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost**](ReleasesApi.md#applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost) | **POST** /api/v1/releases/policies/{policy_id}/apply | Apply Policy |
| [**applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPostWithHttpInfo**](ReleasesApi.md#applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPostWithHttpInfo) | **POST** /api/v1/releases/policies/{policy_id}/apply | Apply Policy |
| [**createPolicyApiV1ReleasesPoliciesPost**](ReleasesApi.md#createPolicyApiV1ReleasesPoliciesPost) | **POST** /api/v1/releases/policies | Create Policy |
| [**createPolicyApiV1ReleasesPoliciesPostWithHttpInfo**](ReleasesApi.md#createPolicyApiV1ReleasesPoliciesPostWithHttpInfo) | **POST** /api/v1/releases/policies | Create Policy |
| [**killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost**](ReleasesApi.md#killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost) | **POST** /api/v1/releases/{target_kind}/{target_key}/kill-switch | Kill Switch |
| [**killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPostWithHttpInfo**](ReleasesApi.md#killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPostWithHttpInfo) | **POST** /api/v1/releases/{target_kind}/{target_key}/kill-switch | Kill Switch |
| [**previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost**](ReleasesApi.md#previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost) | **POST** /api/v1/releases/policies/{policy_id}/preview | Preview Policy |
| [**previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPostWithHttpInfo**](ReleasesApi.md#previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPostWithHttpInfo) | **POST** /api/v1/releases/policies/{policy_id}/preview | Preview Policy |
| [**recordEvidenceApiV1ReleasesEvidencePost**](ReleasesApi.md#recordEvidenceApiV1ReleasesEvidencePost) | **POST** /api/v1/releases/evidence | Record Evidence |
| [**recordEvidenceApiV1ReleasesEvidencePostWithHttpInfo**](ReleasesApi.md#recordEvidenceApiV1ReleasesEvidencePostWithHttpInfo) | **POST** /api/v1/releases/evidence | Record Evidence |
| [**rollbackApiV1ReleasesTargetKindTargetKeyRollbackPost**](ReleasesApi.md#rollbackApiV1ReleasesTargetKindTargetKeyRollbackPost) | **POST** /api/v1/releases/{target_kind}/{target_key}/rollback | Rollback |
| [**rollbackApiV1ReleasesTargetKindTargetKeyRollbackPostWithHttpInfo**](ReleasesApi.md#rollbackApiV1ReleasesTargetKindTargetKeyRollbackPostWithHttpInfo) | **POST** /api/v1/releases/{target_kind}/{target_key}/rollback | Rollback |
| [**targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet**](ReleasesApi.md#targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet) | **GET** /api/v1/releases/{target_kind}/{target_key}/history | Target History |
| [**targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGetWithHttpInfo**](ReleasesApi.md#targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGetWithHttpInfo) | **GET** /api/v1/releases/{target_kind}/{target_key}/history | Target History |
| [**targetStateApiV1ReleasesTargetKindTargetKeyGet**](ReleasesApi.md#targetStateApiV1ReleasesTargetKindTargetKeyGet) | **GET** /api/v1/releases/{target_kind}/{target_key} | Target State |
| [**targetStateApiV1ReleasesTargetKindTargetKeyGetWithHttpInfo**](ReleasesApi.md#targetStateApiV1ReleasesTargetKindTargetKeyGetWithHttpInfo) | **GET** /api/v1/releases/{target_kind}/{target_key} | Target State |



## applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost

> Object applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost(policyId, promotionApplyRequest, xAmeshTenant, authorization, xAmeshCSRF)

Apply Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ReleasesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ReleasesApi apiInstance = new ReleasesApi(defaultClient);
        UUID policyId = UUID.randomUUID(); // UUID |
        PromotionApplyRequest promotionApplyRequest = new PromotionApplyRequest(); // PromotionApplyRequest |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            Object result = apiInstance.applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost(policyId, promotionApplyRequest, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ReleasesApi#applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost");
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
| **policyId** | **UUID**|  | |
| **promotionApplyRequest** | **PromotionApplyRequest**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

**Object**


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

## applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPostWithHttpInfo

> ApiResponse<Object> applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPostWithHttpInfo(policyId, promotionApplyRequest, xAmeshTenant, authorization, xAmeshCSRF)

Apply Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ReleasesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ReleasesApi apiInstance = new ReleasesApi(defaultClient);
        UUID policyId = UUID.randomUUID(); // UUID |
        PromotionApplyRequest promotionApplyRequest = new PromotionApplyRequest(); // PromotionApplyRequest |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<Object> response = apiInstance.applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPostWithHttpInfo(policyId, promotionApplyRequest, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ReleasesApi#applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost");
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
| **policyId** | **UUID**|  | |
| **promotionApplyRequest** | **PromotionApplyRequest**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<**Object**>


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


## createPolicyApiV1ReleasesPoliciesPost

> PromotionPolicyOutput createPolicyApiV1ReleasesPoliciesPost(promotionPolicyInput, xAmeshTenant, authorization, xAmeshCSRF)

Create Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ReleasesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ReleasesApi apiInstance = new ReleasesApi(defaultClient);
        PromotionPolicyInput promotionPolicyInput = new PromotionPolicyInput(); // PromotionPolicyInput |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            PromotionPolicyOutput result = apiInstance.createPolicyApiV1ReleasesPoliciesPost(promotionPolicyInput, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ReleasesApi#createPolicyApiV1ReleasesPoliciesPost");
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
| **promotionPolicyInput** | **PromotionPolicyInput**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

**PromotionPolicyOutput**


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

## createPolicyApiV1ReleasesPoliciesPostWithHttpInfo

> ApiResponse<PromotionPolicyOutput> createPolicyApiV1ReleasesPoliciesPostWithHttpInfo(promotionPolicyInput, xAmeshTenant, authorization, xAmeshCSRF)

Create Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ReleasesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ReleasesApi apiInstance = new ReleasesApi(defaultClient);
        PromotionPolicyInput promotionPolicyInput = new PromotionPolicyInput(); // PromotionPolicyInput |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<PromotionPolicyOutput> response = apiInstance.createPolicyApiV1ReleasesPoliciesPostWithHttpInfo(promotionPolicyInput, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ReleasesApi#createPolicyApiV1ReleasesPoliciesPost");
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
| **promotionPolicyInput** | **PromotionPolicyInput**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<**PromotionPolicyOutput**>


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


## killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost

> Object killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost(targetKind, targetKey, promotionKillSwitchRequest, xAmeshTenant, authorization, xAmeshCSRF)

Kill Switch

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ReleasesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ReleasesApi apiInstance = new ReleasesApi(defaultClient);
        PromotionTargetKind targetKind = PromotionTargetKind.fromValue("WORKFLOW"); // PromotionTargetKind |
        String targetKey = "targetKey_example"; // String |
        PromotionKillSwitchRequest promotionKillSwitchRequest = new PromotionKillSwitchRequest(); // PromotionKillSwitchRequest |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            Object result = apiInstance.killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost(targetKind, targetKey, promotionKillSwitchRequest, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ReleasesApi#killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost");
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
| **targetKind** | **PromotionTargetKind**|  | [enum: WORKFLOW, AGENT] |
| **targetKey** | **String**|  | |
| **promotionKillSwitchRequest** | **PromotionKillSwitchRequest**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

**Object**


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

## killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPostWithHttpInfo

> ApiResponse<Object> killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPostWithHttpInfo(targetKind, targetKey, promotionKillSwitchRequest, xAmeshTenant, authorization, xAmeshCSRF)

Kill Switch

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ReleasesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ReleasesApi apiInstance = new ReleasesApi(defaultClient);
        PromotionTargetKind targetKind = PromotionTargetKind.fromValue("WORKFLOW"); // PromotionTargetKind |
        String targetKey = "targetKey_example"; // String |
        PromotionKillSwitchRequest promotionKillSwitchRequest = new PromotionKillSwitchRequest(); // PromotionKillSwitchRequest |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<Object> response = apiInstance.killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPostWithHttpInfo(targetKind, targetKey, promotionKillSwitchRequest, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ReleasesApi#killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost");
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
| **targetKind** | **PromotionTargetKind**|  | [enum: WORKFLOW, AGENT] |
| **targetKey** | **String**|  | |
| **promotionKillSwitchRequest** | **PromotionKillSwitchRequest**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<**Object**>


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


## previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost

> Object previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost(policyId, xAmeshTenant, authorization, xAmeshCSRF, promotionPreviewRequest)

Preview Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ReleasesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ReleasesApi apiInstance = new ReleasesApi(defaultClient);
        UUID policyId = UUID.randomUUID(); // UUID |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        PromotionPreviewRequest promotionPreviewRequest = new PromotionPreviewRequest(); // PromotionPreviewRequest |
        try {
            Object result = apiInstance.previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost(policyId, xAmeshTenant, authorization, xAmeshCSRF, promotionPreviewRequest);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ReleasesApi#previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost");
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
| **policyId** | **UUID**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **promotionPreviewRequest** | **PromotionPreviewRequest**|  | [optional] |

### Return type

**Object**


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

## previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPostWithHttpInfo

> ApiResponse<Object> previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPostWithHttpInfo(policyId, xAmeshTenant, authorization, xAmeshCSRF, promotionPreviewRequest)

Preview Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ReleasesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ReleasesApi apiInstance = new ReleasesApi(defaultClient);
        UUID policyId = UUID.randomUUID(); // UUID |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        PromotionPreviewRequest promotionPreviewRequest = new PromotionPreviewRequest(); // PromotionPreviewRequest |
        try {
            ApiResponse<Object> response = apiInstance.previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPostWithHttpInfo(policyId, xAmeshTenant, authorization, xAmeshCSRF, promotionPreviewRequest);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ReleasesApi#previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost");
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
| **policyId** | **UUID**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **promotionPreviewRequest** | **PromotionPreviewRequest**|  | [optional] |

### Return type

ApiResponse<**Object**>


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


## recordEvidenceApiV1ReleasesEvidencePost

> EvidenceArtifact recordEvidenceApiV1ReleasesEvidencePost(evidenceArtifact, xAmeshTenant, authorization, xAmeshCSRF)

Record Evidence

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ReleasesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ReleasesApi apiInstance = new ReleasesApi(defaultClient);
        EvidenceArtifact evidenceArtifact = new EvidenceArtifact(); // EvidenceArtifact |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            EvidenceArtifact result = apiInstance.recordEvidenceApiV1ReleasesEvidencePost(evidenceArtifact, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ReleasesApi#recordEvidenceApiV1ReleasesEvidencePost");
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
| **evidenceArtifact** | **EvidenceArtifact**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

**EvidenceArtifact**


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

## recordEvidenceApiV1ReleasesEvidencePostWithHttpInfo

> ApiResponse<EvidenceArtifact> recordEvidenceApiV1ReleasesEvidencePostWithHttpInfo(evidenceArtifact, xAmeshTenant, authorization, xAmeshCSRF)

Record Evidence

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ReleasesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ReleasesApi apiInstance = new ReleasesApi(defaultClient);
        EvidenceArtifact evidenceArtifact = new EvidenceArtifact(); // EvidenceArtifact |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<EvidenceArtifact> response = apiInstance.recordEvidenceApiV1ReleasesEvidencePostWithHttpInfo(evidenceArtifact, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ReleasesApi#recordEvidenceApiV1ReleasesEvidencePost");
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
| **evidenceArtifact** | **EvidenceArtifact**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<**EvidenceArtifact**>


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


## rollbackApiV1ReleasesTargetKindTargetKeyRollbackPost

> Object rollbackApiV1ReleasesTargetKindTargetKeyRollbackPost(targetKind, targetKey, promotionRollbackRequest, xAmeshTenant, authorization, xAmeshCSRF)

Rollback

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ReleasesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ReleasesApi apiInstance = new ReleasesApi(defaultClient);
        PromotionTargetKind targetKind = PromotionTargetKind.fromValue("WORKFLOW"); // PromotionTargetKind |
        String targetKey = "targetKey_example"; // String |
        PromotionRollbackRequest promotionRollbackRequest = new PromotionRollbackRequest(); // PromotionRollbackRequest |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            Object result = apiInstance.rollbackApiV1ReleasesTargetKindTargetKeyRollbackPost(targetKind, targetKey, promotionRollbackRequest, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ReleasesApi#rollbackApiV1ReleasesTargetKindTargetKeyRollbackPost");
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
| **targetKind** | **PromotionTargetKind**|  | [enum: WORKFLOW, AGENT] |
| **targetKey** | **String**|  | |
| **promotionRollbackRequest** | **PromotionRollbackRequest**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

**Object**


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

## rollbackApiV1ReleasesTargetKindTargetKeyRollbackPostWithHttpInfo

> ApiResponse<Object> rollbackApiV1ReleasesTargetKindTargetKeyRollbackPostWithHttpInfo(targetKind, targetKey, promotionRollbackRequest, xAmeshTenant, authorization, xAmeshCSRF)

Rollback

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ReleasesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ReleasesApi apiInstance = new ReleasesApi(defaultClient);
        PromotionTargetKind targetKind = PromotionTargetKind.fromValue("WORKFLOW"); // PromotionTargetKind |
        String targetKey = "targetKey_example"; // String |
        PromotionRollbackRequest promotionRollbackRequest = new PromotionRollbackRequest(); // PromotionRollbackRequest |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<Object> response = apiInstance.rollbackApiV1ReleasesTargetKindTargetKeyRollbackPostWithHttpInfo(targetKind, targetKey, promotionRollbackRequest, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ReleasesApi#rollbackApiV1ReleasesTargetKindTargetKeyRollbackPost");
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
| **targetKind** | **PromotionTargetKind**|  | [enum: WORKFLOW, AGENT] |
| **targetKey** | **String**|  | |
| **promotionRollbackRequest** | **PromotionRollbackRequest**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<**Object**>


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


## targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet

> Object targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet(targetKind, targetKey, xAmeshTenant, authorization, xAmeshCSRF)

Target History

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ReleasesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ReleasesApi apiInstance = new ReleasesApi(defaultClient);
        PromotionTargetKind targetKind = PromotionTargetKind.fromValue("WORKFLOW"); // PromotionTargetKind |
        String targetKey = "targetKey_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            Object result = apiInstance.targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet(targetKind, targetKey, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ReleasesApi#targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet");
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
| **targetKind** | **PromotionTargetKind**|  | [enum: WORKFLOW, AGENT] |
| **targetKey** | **String**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

**Object**


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

## targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGetWithHttpInfo

> ApiResponse<Object> targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGetWithHttpInfo(targetKind, targetKey, xAmeshTenant, authorization, xAmeshCSRF)

Target History

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ReleasesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ReleasesApi apiInstance = new ReleasesApi(defaultClient);
        PromotionTargetKind targetKind = PromotionTargetKind.fromValue("WORKFLOW"); // PromotionTargetKind |
        String targetKey = "targetKey_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<Object> response = apiInstance.targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGetWithHttpInfo(targetKind, targetKey, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ReleasesApi#targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet");
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
| **targetKind** | **PromotionTargetKind**|  | [enum: WORKFLOW, AGENT] |
| **targetKey** | **String**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<**Object**>


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


## targetStateApiV1ReleasesTargetKindTargetKeyGet

> Object targetStateApiV1ReleasesTargetKindTargetKeyGet(targetKind, targetKey, xAmeshTenant, authorization, xAmeshCSRF)

Target State

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ReleasesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ReleasesApi apiInstance = new ReleasesApi(defaultClient);
        PromotionTargetKind targetKind = PromotionTargetKind.fromValue("WORKFLOW"); // PromotionTargetKind |
        String targetKey = "targetKey_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            Object result = apiInstance.targetStateApiV1ReleasesTargetKindTargetKeyGet(targetKind, targetKey, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ReleasesApi#targetStateApiV1ReleasesTargetKindTargetKeyGet");
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
| **targetKind** | **PromotionTargetKind**|  | [enum: WORKFLOW, AGENT] |
| **targetKey** | **String**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

**Object**


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

## targetStateApiV1ReleasesTargetKindTargetKeyGetWithHttpInfo

> ApiResponse<Object> targetStateApiV1ReleasesTargetKindTargetKeyGetWithHttpInfo(targetKind, targetKey, xAmeshTenant, authorization, xAmeshCSRF)

Target State

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ReleasesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ReleasesApi apiInstance = new ReleasesApi(defaultClient);
        PromotionTargetKind targetKind = PromotionTargetKind.fromValue("WORKFLOW"); // PromotionTargetKind |
        String targetKey = "targetKey_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<Object> response = apiInstance.targetStateApiV1ReleasesTargetKindTargetKeyGetWithHttpInfo(targetKind, targetKey, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ReleasesApi#targetStateApiV1ReleasesTargetKindTargetKeyGet");
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
| **targetKind** | **PromotionTargetKind**|  | [enum: WORKFLOW, AGENT] |
| **targetKey** | **String**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<**Object**>


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
