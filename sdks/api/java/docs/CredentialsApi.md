# CredentialsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**exchangeWorkloadCredentialApiV1CredentialsExchangePost**](CredentialsApi.md#exchangeWorkloadCredentialApiV1CredentialsExchangePost) | **POST** /api/v1/credentials/exchange | Exchange Workload Credential |
| [**exchangeWorkloadCredentialApiV1CredentialsExchangePostWithHttpInfo**](CredentialsApi.md#exchangeWorkloadCredentialApiV1CredentialsExchangePostWithHttpInfo) | **POST** /api/v1/credentials/exchange | Exchange Workload Credential |
| [**issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost**](CredentialsApi.md#issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost) | **POST** /api/v1/admin/principals/{principal_id}/credentials | Issue Credential |
| [**issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPostWithHttpInfo**](CredentialsApi.md#issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPostWithHttpInfo) | **POST** /api/v1/admin/principals/{principal_id}/credentials | Issue Credential |
| [**listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet**](CredentialsApi.md#listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet) | **GET** /api/v1/admin/principals/{principal_id}/credentials | List Credentials |
| [**listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGetWithHttpInfo**](CredentialsApi.md#listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGetWithHttpInfo) | **GET** /api/v1/admin/principals/{principal_id}/credentials | List Credentials |
| [**revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete**](CredentialsApi.md#revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete) | **DELETE** /api/v1/admin/principals/{principal_id}/credentials | Revoke All Credentials |
| [**revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDeleteWithHttpInfo**](CredentialsApi.md#revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDeleteWithHttpInfo) | **DELETE** /api/v1/admin/principals/{principal_id}/credentials | Revoke All Credentials |
| [**revokeCredentialApiV1AdminCredentialsCredentialIdDelete**](CredentialsApi.md#revokeCredentialApiV1AdminCredentialsCredentialIdDelete) | **DELETE** /api/v1/admin/credentials/{credential_id} | Revoke Credential |
| [**revokeCredentialApiV1AdminCredentialsCredentialIdDeleteWithHttpInfo**](CredentialsApi.md#revokeCredentialApiV1AdminCredentialsCredentialIdDeleteWithHttpInfo) | **DELETE** /api/v1/admin/credentials/{credential_id} | Revoke Credential |
| [**rotateCredentialApiV1AdminCredentialsCredentialIdRotatePost**](CredentialsApi.md#rotateCredentialApiV1AdminCredentialsCredentialIdRotatePost) | **POST** /api/v1/admin/credentials/{credential_id}/rotate | Rotate Credential |
| [**rotateCredentialApiV1AdminCredentialsCredentialIdRotatePostWithHttpInfo**](CredentialsApi.md#rotateCredentialApiV1AdminCredentialsCredentialIdRotatePostWithHttpInfo) | **POST** /api/v1/admin/credentials/{credential_id}/rotate | Rotate Credential |



## exchangeWorkloadCredentialApiV1CredentialsExchangePost

> IssuedCredentialResponse exchangeWorkloadCredentialApiV1CredentialsExchangePost(exchangeCredentialRequest, authorization, xAmeshCSRF)

Exchange Workload Credential

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CredentialsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CredentialsApi apiInstance = new CredentialsApi(defaultClient);
        ExchangeCredentialRequest exchangeCredentialRequest = new ExchangeCredentialRequest(); // ExchangeCredentialRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            IssuedCredentialResponse result = apiInstance.exchangeWorkloadCredentialApiV1CredentialsExchangePost(exchangeCredentialRequest, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling CredentialsApi#exchangeWorkloadCredentialApiV1CredentialsExchangePost");
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
| **exchangeCredentialRequest** | [**ExchangeCredentialRequest**](ExchangeCredentialRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**IssuedCredentialResponse**](IssuedCredentialResponse.md)


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

## exchangeWorkloadCredentialApiV1CredentialsExchangePostWithHttpInfo

> ApiResponse<IssuedCredentialResponse> exchangeWorkloadCredentialApiV1CredentialsExchangePostWithHttpInfo(exchangeCredentialRequest, authorization, xAmeshCSRF)

Exchange Workload Credential

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CredentialsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CredentialsApi apiInstance = new CredentialsApi(defaultClient);
        ExchangeCredentialRequest exchangeCredentialRequest = new ExchangeCredentialRequest(); // ExchangeCredentialRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<IssuedCredentialResponse> response = apiInstance.exchangeWorkloadCredentialApiV1CredentialsExchangePostWithHttpInfo(exchangeCredentialRequest, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling CredentialsApi#exchangeWorkloadCredentialApiV1CredentialsExchangePost");
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
| **exchangeCredentialRequest** | [**ExchangeCredentialRequest**](ExchangeCredentialRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**IssuedCredentialResponse**](IssuedCredentialResponse.md)>


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


## issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost

> IssuedCredentialResponse issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost(principalId, issueCredentialRequest, authorization, xAmeshCSRF)

Issue Credential

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CredentialsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CredentialsApi apiInstance = new CredentialsApi(defaultClient);
        UUID principalId = UUID.randomUUID(); // UUID |
        IssueCredentialRequest issueCredentialRequest = new IssueCredentialRequest(); // IssueCredentialRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            IssuedCredentialResponse result = apiInstance.issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost(principalId, issueCredentialRequest, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling CredentialsApi#issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost");
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
| **principalId** | **UUID**|  | |
| **issueCredentialRequest** | [**IssueCredentialRequest**](IssueCredentialRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**IssuedCredentialResponse**](IssuedCredentialResponse.md)


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

## issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPostWithHttpInfo

> ApiResponse<IssuedCredentialResponse> issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPostWithHttpInfo(principalId, issueCredentialRequest, authorization, xAmeshCSRF)

Issue Credential

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CredentialsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CredentialsApi apiInstance = new CredentialsApi(defaultClient);
        UUID principalId = UUID.randomUUID(); // UUID |
        IssueCredentialRequest issueCredentialRequest = new IssueCredentialRequest(); // IssueCredentialRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<IssuedCredentialResponse> response = apiInstance.issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPostWithHttpInfo(principalId, issueCredentialRequest, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling CredentialsApi#issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost");
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
| **principalId** | **UUID**|  | |
| **issueCredentialRequest** | [**IssueCredentialRequest**](IssueCredentialRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**IssuedCredentialResponse**](IssuedCredentialResponse.md)>


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


## listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet

> List<CredentialMetadata> listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet(principalId, cursor, limit, filter, sort, fields, authorization, xAmeshCSRF)

List Credentials

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CredentialsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CredentialsApi apiInstance = new CredentialsApi(defaultClient);
        UUID principalId = UUID.randomUUID(); // UUID |
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 56; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            List<CredentialMetadata> result = apiInstance.listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet(principalId, cursor, limit, filter, sort, fields, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling CredentialsApi#listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet");
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
| **principalId** | **UUID**|  | |
| **cursor** | **String**| Opaque cursor from the prior page | [optional] |
| **limit** | **Integer**|  | [optional] |
| **filter** | [**List&lt;String&gt;**](String.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**List&lt;CredentialMetadata&gt;**](CredentialMetadata.md)


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

## listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGetWithHttpInfo

> ApiResponse<List<CredentialMetadata>> listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGetWithHttpInfo(principalId, cursor, limit, filter, sort, fields, authorization, xAmeshCSRF)

List Credentials

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CredentialsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CredentialsApi apiInstance = new CredentialsApi(defaultClient);
        UUID principalId = UUID.randomUUID(); // UUID |
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 56; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<List<CredentialMetadata>> response = apiInstance.listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGetWithHttpInfo(principalId, cursor, limit, filter, sort, fields, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling CredentialsApi#listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet");
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
| **principalId** | **UUID**|  | |
| **cursor** | **String**| Opaque cursor from the prior page | [optional] |
| **limit** | **Integer**|  | [optional] |
| **filter** | [**List&lt;String&gt;**](String.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;CredentialMetadata&gt;**](CredentialMetadata.md)>


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


## revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete

> RevokedCredentialsResponse revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete(principalId, authorization, xAmeshCSRF)

Revoke All Credentials

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CredentialsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CredentialsApi apiInstance = new CredentialsApi(defaultClient);
        UUID principalId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            RevokedCredentialsResponse result = apiInstance.revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete(principalId, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling CredentialsApi#revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete");
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
| **principalId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**RevokedCredentialsResponse**](RevokedCredentialsResponse.md)


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

## revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDeleteWithHttpInfo

> ApiResponse<RevokedCredentialsResponse> revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDeleteWithHttpInfo(principalId, authorization, xAmeshCSRF)

Revoke All Credentials

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CredentialsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CredentialsApi apiInstance = new CredentialsApi(defaultClient);
        UUID principalId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<RevokedCredentialsResponse> response = apiInstance.revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDeleteWithHttpInfo(principalId, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling CredentialsApi#revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete");
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
| **principalId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**RevokedCredentialsResponse**](RevokedCredentialsResponse.md)>


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


## revokeCredentialApiV1AdminCredentialsCredentialIdDelete

> RevokedCredentialsResponse revokeCredentialApiV1AdminCredentialsCredentialIdDelete(credentialId, authorization, xAmeshCSRF)

Revoke Credential

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CredentialsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CredentialsApi apiInstance = new CredentialsApi(defaultClient);
        UUID credentialId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            RevokedCredentialsResponse result = apiInstance.revokeCredentialApiV1AdminCredentialsCredentialIdDelete(credentialId, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling CredentialsApi#revokeCredentialApiV1AdminCredentialsCredentialIdDelete");
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
| **credentialId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**RevokedCredentialsResponse**](RevokedCredentialsResponse.md)


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

## revokeCredentialApiV1AdminCredentialsCredentialIdDeleteWithHttpInfo

> ApiResponse<RevokedCredentialsResponse> revokeCredentialApiV1AdminCredentialsCredentialIdDeleteWithHttpInfo(credentialId, authorization, xAmeshCSRF)

Revoke Credential

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CredentialsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CredentialsApi apiInstance = new CredentialsApi(defaultClient);
        UUID credentialId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<RevokedCredentialsResponse> response = apiInstance.revokeCredentialApiV1AdminCredentialsCredentialIdDeleteWithHttpInfo(credentialId, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling CredentialsApi#revokeCredentialApiV1AdminCredentialsCredentialIdDelete");
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
| **credentialId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**RevokedCredentialsResponse**](RevokedCredentialsResponse.md)>


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


## rotateCredentialApiV1AdminCredentialsCredentialIdRotatePost

> IssuedCredentialResponse rotateCredentialApiV1AdminCredentialsCredentialIdRotatePost(credentialId, rotateCredentialRequest, authorization, xAmeshCSRF)

Rotate Credential

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CredentialsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CredentialsApi apiInstance = new CredentialsApi(defaultClient);
        UUID credentialId = UUID.randomUUID(); // UUID |
        RotateCredentialRequest rotateCredentialRequest = new RotateCredentialRequest(); // RotateCredentialRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            IssuedCredentialResponse result = apiInstance.rotateCredentialApiV1AdminCredentialsCredentialIdRotatePost(credentialId, rotateCredentialRequest, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling CredentialsApi#rotateCredentialApiV1AdminCredentialsCredentialIdRotatePost");
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
| **credentialId** | **UUID**|  | |
| **rotateCredentialRequest** | [**RotateCredentialRequest**](RotateCredentialRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**IssuedCredentialResponse**](IssuedCredentialResponse.md)


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

## rotateCredentialApiV1AdminCredentialsCredentialIdRotatePostWithHttpInfo

> ApiResponse<IssuedCredentialResponse> rotateCredentialApiV1AdminCredentialsCredentialIdRotatePostWithHttpInfo(credentialId, rotateCredentialRequest, authorization, xAmeshCSRF)

Rotate Credential

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CredentialsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CredentialsApi apiInstance = new CredentialsApi(defaultClient);
        UUID credentialId = UUID.randomUUID(); // UUID |
        RotateCredentialRequest rotateCredentialRequest = new RotateCredentialRequest(); // RotateCredentialRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<IssuedCredentialResponse> response = apiInstance.rotateCredentialApiV1AdminCredentialsCredentialIdRotatePostWithHttpInfo(credentialId, rotateCredentialRequest, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling CredentialsApi#rotateCredentialApiV1AdminCredentialsCredentialIdRotatePost");
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
| **credentialId** | **UUID**|  | |
| **rotateCredentialRequest** | [**RotateCredentialRequest**](RotateCredentialRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**IssuedCredentialResponse**](IssuedCredentialResponse.md)>


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
