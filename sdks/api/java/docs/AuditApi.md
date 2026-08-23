# AuditApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createAuditLegalHoldApiV1AuditLegalHoldsPost**](AuditApi.md#createAuditLegalHoldApiV1AuditLegalHoldsPost) | **POST** /api/v1/audit-legal-holds | Create Audit Legal Hold |
| [**createAuditLegalHoldApiV1AuditLegalHoldsPostWithHttpInfo**](AuditApi.md#createAuditLegalHoldApiV1AuditLegalHoldsPostWithHttpInfo) | **POST** /api/v1/audit-legal-holds | Create Audit Legal Hold |
| [**createComplianceEvidenceApiV1ComplianceEvidencePost**](AuditApi.md#createComplianceEvidenceApiV1ComplianceEvidencePost) | **POST** /api/v1/compliance-evidence | Create Compliance Evidence |
| [**createComplianceEvidenceApiV1ComplianceEvidencePostWithHttpInfo**](AuditApi.md#createComplianceEvidenceApiV1ComplianceEvidencePostWithHttpInfo) | **POST** /api/v1/compliance-evidence | Create Compliance Evidence |
| [**createObjectAuditExportApiV1AuditExportsPost**](AuditApi.md#createObjectAuditExportApiV1AuditExportsPost) | **POST** /api/v1/audit-exports | Create Object Audit Export |
| [**createObjectAuditExportApiV1AuditExportsPostWithHttpInfo**](AuditApi.md#createObjectAuditExportApiV1AuditExportsPostWithHttpInfo) | **POST** /api/v1/audit-exports | Create Object Audit Export |
| [**createObjectCompliancePackageApiV1CompliancePackagesPost**](AuditApi.md#createObjectCompliancePackageApiV1CompliancePackagesPost) | **POST** /api/v1/compliance-packages | Create Object Compliance Package |
| [**createObjectCompliancePackageApiV1CompliancePackagesPostWithHttpInfo**](AuditApi.md#createObjectCompliancePackageApiV1CompliancePackagesPostWithHttpInfo) | **POST** /api/v1/compliance-packages | Create Object Compliance Package |
| [**downloadAuditExportApiV1AuditEventsExportGet**](AuditApi.md#downloadAuditExportApiV1AuditEventsExportGet) | **GET** /api/v1/audit-events/export | Download Audit Export |
| [**downloadAuditExportApiV1AuditEventsExportGetWithHttpInfo**](AuditApi.md#downloadAuditExportApiV1AuditEventsExportGetWithHttpInfo) | **GET** /api/v1/audit-events/export | Download Audit Export |
| [**downloadCompliancePackageApiV1CompliancePackagesExportGet**](AuditApi.md#downloadCompliancePackageApiV1CompliancePackagesExportGet) | **GET** /api/v1/compliance-packages/export | Download Compliance Package |
| [**downloadCompliancePackageApiV1CompliancePackagesExportGetWithHttpInfo**](AuditApi.md#downloadCompliancePackageApiV1CompliancePackagesExportGetWithHttpInfo) | **GET** /api/v1/compliance-packages/export | Download Compliance Package |
| [**getAuditPolicyApiV1AuditPolicyGet**](AuditApi.md#getAuditPolicyApiV1AuditPolicyGet) | **GET** /api/v1/audit-policy | Get Audit Policy |
| [**getAuditPolicyApiV1AuditPolicyGetWithHttpInfo**](AuditApi.md#getAuditPolicyApiV1AuditPolicyGetWithHttpInfo) | **GET** /api/v1/audit-policy | Get Audit Policy |
| [**listAuditEventsApiV1AuditEventsGet**](AuditApi.md#listAuditEventsApiV1AuditEventsGet) | **GET** /api/v1/audit-events | List Audit Events |
| [**listAuditEventsApiV1AuditEventsGetWithHttpInfo**](AuditApi.md#listAuditEventsApiV1AuditEventsGetWithHttpInfo) | **GET** /api/v1/audit-events | List Audit Events |
| [**listAuditLegalHoldsApiV1AuditLegalHoldsGet**](AuditApi.md#listAuditLegalHoldsApiV1AuditLegalHoldsGet) | **GET** /api/v1/audit-legal-holds | List Audit Legal Holds |
| [**listAuditLegalHoldsApiV1AuditLegalHoldsGetWithHttpInfo**](AuditApi.md#listAuditLegalHoldsApiV1AuditLegalHoldsGetWithHttpInfo) | **GET** /api/v1/audit-legal-holds | List Audit Legal Holds |
| [**listComplianceEvidenceApiV1ComplianceEvidenceGet**](AuditApi.md#listComplianceEvidenceApiV1ComplianceEvidenceGet) | **GET** /api/v1/compliance-evidence | List Compliance Evidence |
| [**listComplianceEvidenceApiV1ComplianceEvidenceGetWithHttpInfo**](AuditApi.md#listComplianceEvidenceApiV1ComplianceEvidenceGetWithHttpInfo) | **GET** /api/v1/compliance-evidence | List Compliance Evidence |
| [**purgeAuditRetentionApiV1AuditRetentionPurgePost**](AuditApi.md#purgeAuditRetentionApiV1AuditRetentionPurgePost) | **POST** /api/v1/audit-retention/purge | Purge Audit Retention |
| [**purgeAuditRetentionApiV1AuditRetentionPurgePostWithHttpInfo**](AuditApi.md#purgeAuditRetentionApiV1AuditRetentionPurgePostWithHttpInfo) | **POST** /api/v1/audit-retention/purge | Purge Audit Retention |
| [**releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete**](AuditApi.md#releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete) | **DELETE** /api/v1/audit-legal-holds/{hold_id} | Release Audit Legal Hold |
| [**releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDeleteWithHttpInfo**](AuditApi.md#releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDeleteWithHttpInfo) | **DELETE** /api/v1/audit-legal-holds/{hold_id} | Release Audit Legal Hold |
| [**updateAuditPolicyApiV1AuditPolicyPut**](AuditApi.md#updateAuditPolicyApiV1AuditPolicyPut) | **PUT** /api/v1/audit-policy | Update Audit Policy |
| [**updateAuditPolicyApiV1AuditPolicyPutWithHttpInfo**](AuditApi.md#updateAuditPolicyApiV1AuditPolicyPutWithHttpInfo) | **PUT** /api/v1/audit-policy | Update Audit Policy |
| [**verifyAuditIntegrityApiV1AuditEventsIntegrityGet**](AuditApi.md#verifyAuditIntegrityApiV1AuditEventsIntegrityGet) | **GET** /api/v1/audit-events/integrity | Verify Audit Integrity |
| [**verifyAuditIntegrityApiV1AuditEventsIntegrityGetWithHttpInfo**](AuditApi.md#verifyAuditIntegrityApiV1AuditEventsIntegrityGetWithHttpInfo) | **GET** /api/v1/audit-events/integrity | Verify Audit Integrity |



## createAuditLegalHoldApiV1AuditLegalHoldsPost

> AuditLegalHold createAuditLegalHoldApiV1AuditLegalHoldsPost(auditLegalHoldCreate, authorization, xAmeshCSRF, xAmeshTenant)

Create Audit Legal Hold

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        AuditLegalHoldCreate auditLegalHoldCreate = new AuditLegalHoldCreate(); // AuditLegalHoldCreate |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AuditLegalHold result = apiInstance.createAuditLegalHoldApiV1AuditLegalHoldsPost(auditLegalHoldCreate, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#createAuditLegalHoldApiV1AuditLegalHoldsPost");
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
| **auditLegalHoldCreate** | [**AuditLegalHoldCreate**](AuditLegalHoldCreate.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**AuditLegalHold**](AuditLegalHold.md)


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

## createAuditLegalHoldApiV1AuditLegalHoldsPostWithHttpInfo

> ApiResponse<AuditLegalHold> createAuditLegalHoldApiV1AuditLegalHoldsPostWithHttpInfo(auditLegalHoldCreate, authorization, xAmeshCSRF, xAmeshTenant)

Create Audit Legal Hold

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        AuditLegalHoldCreate auditLegalHoldCreate = new AuditLegalHoldCreate(); // AuditLegalHoldCreate |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AuditLegalHold> response = apiInstance.createAuditLegalHoldApiV1AuditLegalHoldsPostWithHttpInfo(auditLegalHoldCreate, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#createAuditLegalHoldApiV1AuditLegalHoldsPost");
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
| **auditLegalHoldCreate** | [**AuditLegalHoldCreate**](AuditLegalHoldCreate.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**AuditLegalHold**](AuditLegalHold.md)>


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


## createComplianceEvidenceApiV1ComplianceEvidencePost

> ComplianceEvidenceRecord createComplianceEvidenceApiV1ComplianceEvidencePost(complianceEvidenceCreate, authorization, xAmeshCSRF, xAmeshTenant)

Create Compliance Evidence

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        ComplianceEvidenceCreate complianceEvidenceCreate = new ComplianceEvidenceCreate(); // ComplianceEvidenceCreate |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ComplianceEvidenceRecord result = apiInstance.createComplianceEvidenceApiV1ComplianceEvidencePost(complianceEvidenceCreate, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#createComplianceEvidenceApiV1ComplianceEvidencePost");
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
| **complianceEvidenceCreate** | [**ComplianceEvidenceCreate**](ComplianceEvidenceCreate.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**ComplianceEvidenceRecord**](ComplianceEvidenceRecord.md)


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

## createComplianceEvidenceApiV1ComplianceEvidencePostWithHttpInfo

> ApiResponse<ComplianceEvidenceRecord> createComplianceEvidenceApiV1ComplianceEvidencePostWithHttpInfo(complianceEvidenceCreate, authorization, xAmeshCSRF, xAmeshTenant)

Create Compliance Evidence

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        ComplianceEvidenceCreate complianceEvidenceCreate = new ComplianceEvidenceCreate(); // ComplianceEvidenceCreate |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ComplianceEvidenceRecord> response = apiInstance.createComplianceEvidenceApiV1ComplianceEvidencePostWithHttpInfo(complianceEvidenceCreate, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#createComplianceEvidenceApiV1ComplianceEvidencePost");
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
| **complianceEvidenceCreate** | [**ComplianceEvidenceCreate**](ComplianceEvidenceCreate.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**ComplianceEvidenceRecord**](ComplianceEvidenceRecord.md)>


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


## createObjectAuditExportApiV1AuditExportsPost

> AuditExportReceipt createObjectAuditExportApiV1AuditExportsPost(auditExportRequest, authorization, xAmeshCSRF, xAmeshTenant)

Create Object Audit Export

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        AuditExportRequest auditExportRequest = new AuditExportRequest(); // AuditExportRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AuditExportReceipt result = apiInstance.createObjectAuditExportApiV1AuditExportsPost(auditExportRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#createObjectAuditExportApiV1AuditExportsPost");
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
| **auditExportRequest** | [**AuditExportRequest**](AuditExportRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**AuditExportReceipt**](AuditExportReceipt.md)


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

## createObjectAuditExportApiV1AuditExportsPostWithHttpInfo

> ApiResponse<AuditExportReceipt> createObjectAuditExportApiV1AuditExportsPostWithHttpInfo(auditExportRequest, authorization, xAmeshCSRF, xAmeshTenant)

Create Object Audit Export

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        AuditExportRequest auditExportRequest = new AuditExportRequest(); // AuditExportRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AuditExportReceipt> response = apiInstance.createObjectAuditExportApiV1AuditExportsPostWithHttpInfo(auditExportRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#createObjectAuditExportApiV1AuditExportsPost");
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
| **auditExportRequest** | [**AuditExportRequest**](AuditExportRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**AuditExportReceipt**](AuditExportReceipt.md)>


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


## createObjectCompliancePackageApiV1CompliancePackagesPost

> AuditExportReceipt createObjectCompliancePackageApiV1CompliancePackagesPost(compliancePackageRequest, authorization, xAmeshCSRF, xAmeshTenant)

Create Object Compliance Package

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        CompliancePackageRequest compliancePackageRequest = new CompliancePackageRequest(); // CompliancePackageRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AuditExportReceipt result = apiInstance.createObjectCompliancePackageApiV1CompliancePackagesPost(compliancePackageRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#createObjectCompliancePackageApiV1CompliancePackagesPost");
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
| **compliancePackageRequest** | [**CompliancePackageRequest**](CompliancePackageRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**AuditExportReceipt**](AuditExportReceipt.md)


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

## createObjectCompliancePackageApiV1CompliancePackagesPostWithHttpInfo

> ApiResponse<AuditExportReceipt> createObjectCompliancePackageApiV1CompliancePackagesPostWithHttpInfo(compliancePackageRequest, authorization, xAmeshCSRF, xAmeshTenant)

Create Object Compliance Package

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        CompliancePackageRequest compliancePackageRequest = new CompliancePackageRequest(); // CompliancePackageRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AuditExportReceipt> response = apiInstance.createObjectCompliancePackageApiV1CompliancePackagesPostWithHttpInfo(compliancePackageRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#createObjectCompliancePackageApiV1CompliancePackagesPost");
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
| **compliancePackageRequest** | [**CompliancePackageRequest**](CompliancePackageRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**AuditExportReceipt**](AuditExportReceipt.md)>


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


## downloadAuditExportApiV1AuditEventsExportGet

> Object downloadAuditExportApiV1AuditEventsExportGet(format, limit, action, resourceType, outcome, occurredFrom, occurredTo, authorization, xAmeshCSRF, xAmeshTenant)

Download Audit Export

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        AuditExportFormat format = AuditExportFormat.fromValue("JSON"); // AuditExportFormat |
        Integer limit = 10000; // Integer |
        String action = "action_example"; // String |
        String resourceType = "resourceType_example"; // String |
        String outcome = "outcome_example"; // String |
        OffsetDateTime occurredFrom = OffsetDateTime.now(); // OffsetDateTime |
        OffsetDateTime occurredTo = OffsetDateTime.now(); // OffsetDateTime |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            Object result = apiInstance.downloadAuditExportApiV1AuditEventsExportGet(format, limit, action, resourceType, outcome, occurredFrom, occurredTo, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#downloadAuditExportApiV1AuditEventsExportGet");
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
| **format** | [**AuditExportFormat**](.md)|  | [optional] [default to NDJSON] [enum: JSON, NDJSON] |
| **limit** | **Integer**|  | [optional] [default to 10000] |
| **action** | **String**|  | [optional] |
| **resourceType** | **String**|  | [optional] |
| **outcome** | **String**|  | [optional] |
| **occurredFrom** | **OffsetDateTime**|  | [optional] |
| **occurredTo** | **OffsetDateTime**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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

## downloadAuditExportApiV1AuditEventsExportGetWithHttpInfo

> ApiResponse<Object> downloadAuditExportApiV1AuditEventsExportGetWithHttpInfo(format, limit, action, resourceType, outcome, occurredFrom, occurredTo, authorization, xAmeshCSRF, xAmeshTenant)

Download Audit Export

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        AuditExportFormat format = AuditExportFormat.fromValue("JSON"); // AuditExportFormat |
        Integer limit = 10000; // Integer |
        String action = "action_example"; // String |
        String resourceType = "resourceType_example"; // String |
        String outcome = "outcome_example"; // String |
        OffsetDateTime occurredFrom = OffsetDateTime.now(); // OffsetDateTime |
        OffsetDateTime occurredTo = OffsetDateTime.now(); // OffsetDateTime |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Object> response = apiInstance.downloadAuditExportApiV1AuditEventsExportGetWithHttpInfo(format, limit, action, resourceType, outcome, occurredFrom, occurredTo, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#downloadAuditExportApiV1AuditEventsExportGet");
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
| **format** | [**AuditExportFormat**](.md)|  | [optional] [default to NDJSON] [enum: JSON, NDJSON] |
| **limit** | **Integer**|  | [optional] [default to 10000] |
| **action** | **String**|  | [optional] |
| **resourceType** | **String**|  | [optional] |
| **outcome** | **String**|  | [optional] |
| **occurredFrom** | **OffsetDateTime**|  | [optional] |
| **occurredTo** | **OffsetDateTime**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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


## downloadCompliancePackageApiV1CompliancePackagesExportGet

> Object downloadCompliancePackageApiV1CompliancePackagesExportGet(occurredFrom, occurredTo, maxAuditEvents, authorization, xAmeshCSRF, xAmeshTenant)

Download Compliance Package

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        OffsetDateTime occurredFrom = OffsetDateTime.now(); // OffsetDateTime |
        OffsetDateTime occurredTo = OffsetDateTime.now(); // OffsetDateTime |
        Integer maxAuditEvents = 10000; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            Object result = apiInstance.downloadCompliancePackageApiV1CompliancePackagesExportGet(occurredFrom, occurredTo, maxAuditEvents, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#downloadCompliancePackageApiV1CompliancePackagesExportGet");
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
| **occurredFrom** | **OffsetDateTime**|  | [optional] |
| **occurredTo** | **OffsetDateTime**|  | [optional] |
| **maxAuditEvents** | **Integer**|  | [optional] [default to 10000] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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

## downloadCompliancePackageApiV1CompliancePackagesExportGetWithHttpInfo

> ApiResponse<Object> downloadCompliancePackageApiV1CompliancePackagesExportGetWithHttpInfo(occurredFrom, occurredTo, maxAuditEvents, authorization, xAmeshCSRF, xAmeshTenant)

Download Compliance Package

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        OffsetDateTime occurredFrom = OffsetDateTime.now(); // OffsetDateTime |
        OffsetDateTime occurredTo = OffsetDateTime.now(); // OffsetDateTime |
        Integer maxAuditEvents = 10000; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Object> response = apiInstance.downloadCompliancePackageApiV1CompliancePackagesExportGetWithHttpInfo(occurredFrom, occurredTo, maxAuditEvents, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#downloadCompliancePackageApiV1CompliancePackagesExportGet");
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
| **occurredFrom** | **OffsetDateTime**|  | [optional] |
| **occurredTo** | **OffsetDateTime**|  | [optional] |
| **maxAuditEvents** | **Integer**|  | [optional] [default to 10000] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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


## getAuditPolicyApiV1AuditPolicyGet

> AuditRetentionPolicy getAuditPolicyApiV1AuditPolicyGet(authorization, xAmeshCSRF, xAmeshTenant)

Get Audit Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AuditRetentionPolicy result = apiInstance.getAuditPolicyApiV1AuditPolicyGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#getAuditPolicyApiV1AuditPolicyGet");
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

[**AuditRetentionPolicy**](AuditRetentionPolicy.md)


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

## getAuditPolicyApiV1AuditPolicyGetWithHttpInfo

> ApiResponse<AuditRetentionPolicy> getAuditPolicyApiV1AuditPolicyGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

Get Audit Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AuditRetentionPolicy> response = apiInstance.getAuditPolicyApiV1AuditPolicyGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#getAuditPolicyApiV1AuditPolicyGet");
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

ApiResponse<[**AuditRetentionPolicy**](AuditRetentionPolicy.md)>


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


## listAuditEventsApiV1AuditEventsGet

> AuditEventPage listAuditEventsApiV1AuditEventsGet(cursor, limit, action, resourceType, outcome, occurredFrom, occurredTo, authorization, xAmeshCSRF, xAmeshTenant)

List Audit Events

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        Integer cursor = 56; // Integer |
        Integer limit = 100; // Integer |
        String action = "action_example"; // String |
        String resourceType = "resourceType_example"; // String |
        String outcome = "outcome_example"; // String |
        OffsetDateTime occurredFrom = OffsetDateTime.now(); // OffsetDateTime |
        OffsetDateTime occurredTo = OffsetDateTime.now(); // OffsetDateTime |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AuditEventPage result = apiInstance.listAuditEventsApiV1AuditEventsGet(cursor, limit, action, resourceType, outcome, occurredFrom, occurredTo, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#listAuditEventsApiV1AuditEventsGet");
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
| **cursor** | **Integer**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **action** | **String**|  | [optional] |
| **resourceType** | **String**|  | [optional] |
| **outcome** | **String**|  | [optional] |
| **occurredFrom** | **OffsetDateTime**|  | [optional] |
| **occurredTo** | **OffsetDateTime**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**AuditEventPage**](AuditEventPage.md)


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

## listAuditEventsApiV1AuditEventsGetWithHttpInfo

> ApiResponse<AuditEventPage> listAuditEventsApiV1AuditEventsGetWithHttpInfo(cursor, limit, action, resourceType, outcome, occurredFrom, occurredTo, authorization, xAmeshCSRF, xAmeshTenant)

List Audit Events

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        Integer cursor = 56; // Integer |
        Integer limit = 100; // Integer |
        String action = "action_example"; // String |
        String resourceType = "resourceType_example"; // String |
        String outcome = "outcome_example"; // String |
        OffsetDateTime occurredFrom = OffsetDateTime.now(); // OffsetDateTime |
        OffsetDateTime occurredTo = OffsetDateTime.now(); // OffsetDateTime |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AuditEventPage> response = apiInstance.listAuditEventsApiV1AuditEventsGetWithHttpInfo(cursor, limit, action, resourceType, outcome, occurredFrom, occurredTo, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#listAuditEventsApiV1AuditEventsGet");
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
| **cursor** | **Integer**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **action** | **String**|  | [optional] |
| **resourceType** | **String**|  | [optional] |
| **outcome** | **String**|  | [optional] |
| **occurredFrom** | **OffsetDateTime**|  | [optional] |
| **occurredTo** | **OffsetDateTime**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**AuditEventPage**](AuditEventPage.md)>


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


## listAuditLegalHoldsApiV1AuditLegalHoldsGet

> List<AuditLegalHold> listAuditLegalHoldsApiV1AuditLegalHoldsGet(authorization, xAmeshCSRF, xAmeshTenant)

List Audit Legal Holds

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<AuditLegalHold> result = apiInstance.listAuditLegalHoldsApiV1AuditLegalHoldsGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#listAuditLegalHoldsApiV1AuditLegalHoldsGet");
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

[**List&lt;AuditLegalHold&gt;**](AuditLegalHold.md)


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

## listAuditLegalHoldsApiV1AuditLegalHoldsGetWithHttpInfo

> ApiResponse<List<AuditLegalHold>> listAuditLegalHoldsApiV1AuditLegalHoldsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

List Audit Legal Holds

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<AuditLegalHold>> response = apiInstance.listAuditLegalHoldsApiV1AuditLegalHoldsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#listAuditLegalHoldsApiV1AuditLegalHoldsGet");
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

ApiResponse<[**List&lt;AuditLegalHold&gt;**](AuditLegalHold.md)>


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


## listComplianceEvidenceApiV1ComplianceEvidenceGet

> List<ComplianceEvidenceRecord> listComplianceEvidenceApiV1ComplianceEvidenceGet(authorization, xAmeshCSRF, xAmeshTenant)

List Compliance Evidence

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<ComplianceEvidenceRecord> result = apiInstance.listComplianceEvidenceApiV1ComplianceEvidenceGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#listComplianceEvidenceApiV1ComplianceEvidenceGet");
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

[**List&lt;ComplianceEvidenceRecord&gt;**](ComplianceEvidenceRecord.md)


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

## listComplianceEvidenceApiV1ComplianceEvidenceGetWithHttpInfo

> ApiResponse<List<ComplianceEvidenceRecord>> listComplianceEvidenceApiV1ComplianceEvidenceGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

List Compliance Evidence

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<ComplianceEvidenceRecord>> response = apiInstance.listComplianceEvidenceApiV1ComplianceEvidenceGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#listComplianceEvidenceApiV1ComplianceEvidenceGet");
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

ApiResponse<[**List&lt;ComplianceEvidenceRecord&gt;**](ComplianceEvidenceRecord.md)>


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


## purgeAuditRetentionApiV1AuditRetentionPurgePost

> AuditRetentionResult purgeAuditRetentionApiV1AuditRetentionPurgePost(authorization, xAmeshCSRF, xAmeshTenant)

Purge Audit Retention

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AuditRetentionResult result = apiInstance.purgeAuditRetentionApiV1AuditRetentionPurgePost(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#purgeAuditRetentionApiV1AuditRetentionPurgePost");
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

[**AuditRetentionResult**](AuditRetentionResult.md)


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

## purgeAuditRetentionApiV1AuditRetentionPurgePostWithHttpInfo

> ApiResponse<AuditRetentionResult> purgeAuditRetentionApiV1AuditRetentionPurgePostWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

Purge Audit Retention

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AuditRetentionResult> response = apiInstance.purgeAuditRetentionApiV1AuditRetentionPurgePostWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#purgeAuditRetentionApiV1AuditRetentionPurgePost");
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

ApiResponse<[**AuditRetentionResult**](AuditRetentionResult.md)>


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


## releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete

> AuditLegalHold releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete(holdId, authorization, xAmeshCSRF, xAmeshTenant)

Release Audit Legal Hold

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        UUID holdId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AuditLegalHold result = apiInstance.releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete(holdId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete");
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
| **holdId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**AuditLegalHold**](AuditLegalHold.md)


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

## releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDeleteWithHttpInfo

> ApiResponse<AuditLegalHold> releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDeleteWithHttpInfo(holdId, authorization, xAmeshCSRF, xAmeshTenant)

Release Audit Legal Hold

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        UUID holdId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AuditLegalHold> response = apiInstance.releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDeleteWithHttpInfo(holdId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete");
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
| **holdId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**AuditLegalHold**](AuditLegalHold.md)>


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


## updateAuditPolicyApiV1AuditPolicyPut

> AuditRetentionPolicy updateAuditPolicyApiV1AuditPolicyPut(auditRetentionPolicyUpdate, authorization, xAmeshCSRF, xAmeshTenant)

Update Audit Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        AuditRetentionPolicyUpdate auditRetentionPolicyUpdate = new AuditRetentionPolicyUpdate(); // AuditRetentionPolicyUpdate |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AuditRetentionPolicy result = apiInstance.updateAuditPolicyApiV1AuditPolicyPut(auditRetentionPolicyUpdate, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#updateAuditPolicyApiV1AuditPolicyPut");
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
| **auditRetentionPolicyUpdate** | [**AuditRetentionPolicyUpdate**](AuditRetentionPolicyUpdate.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**AuditRetentionPolicy**](AuditRetentionPolicy.md)


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

## updateAuditPolicyApiV1AuditPolicyPutWithHttpInfo

> ApiResponse<AuditRetentionPolicy> updateAuditPolicyApiV1AuditPolicyPutWithHttpInfo(auditRetentionPolicyUpdate, authorization, xAmeshCSRF, xAmeshTenant)

Update Audit Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        AuditRetentionPolicyUpdate auditRetentionPolicyUpdate = new AuditRetentionPolicyUpdate(); // AuditRetentionPolicyUpdate |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AuditRetentionPolicy> response = apiInstance.updateAuditPolicyApiV1AuditPolicyPutWithHttpInfo(auditRetentionPolicyUpdate, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#updateAuditPolicyApiV1AuditPolicyPut");
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
| **auditRetentionPolicyUpdate** | [**AuditRetentionPolicyUpdate**](AuditRetentionPolicyUpdate.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**AuditRetentionPolicy**](AuditRetentionPolicy.md)>


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


## verifyAuditIntegrityApiV1AuditEventsIntegrityGet

> AuditIntegrityReport verifyAuditIntegrityApiV1AuditEventsIntegrityGet(authorization, xAmeshCSRF, xAmeshTenant)

Verify Audit Integrity

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AuditIntegrityReport result = apiInstance.verifyAuditIntegrityApiV1AuditEventsIntegrityGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#verifyAuditIntegrityApiV1AuditEventsIntegrityGet");
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

[**AuditIntegrityReport**](AuditIntegrityReport.md)


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

## verifyAuditIntegrityApiV1AuditEventsIntegrityGetWithHttpInfo

> ApiResponse<AuditIntegrityReport> verifyAuditIntegrityApiV1AuditEventsIntegrityGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

Verify Audit Integrity

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuditApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuditApi apiInstance = new AuditApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AuditIntegrityReport> response = apiInstance.verifyAuditIntegrityApiV1AuditEventsIntegrityGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuditApi#verifyAuditIntegrityApiV1AuditEventsIntegrityGet");
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

ApiResponse<[**AuditIntegrityReport**](AuditIntegrityReport.md)>


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
