# @amesh/client@0.2.0

A TypeScript SDK client for the localhost API.

## Usage

First, install the SDK from npm.

```bash
npm install @amesh/client --save
```

Next, try it out.


```ts
import {
  Configuration,
  AdministrationApi,
} from '@amesh/client';
import type { ApplyAdministrationControlApiV1AdminControlsKeyPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AdministrationApi();

  const body = {
    // AdministrationControlKey
    key: ...,
    // AdministrationApplyRequest
    administrationApplyRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ApplyAdministrationControlApiV1AdminControlsKeyPutRequest;

  try {
    const data = await api.applyAdministrationControlApiV1AdminControlsKeyPut(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```


## Documentation

### API Endpoints

All URIs are relative to *http://localhost*

| Class | Method | HTTP request | Description
| ----- | ------ | ------------ | -------------
*AdministrationApi* | [**applyAdministrationControlApiV1AdminControlsKeyPut**](docs/AdministrationApi.md#applyadministrationcontrolapiv1admincontrolskeyput) | **PUT** /api/v1/admin/controls/{key} | Apply Administration Control
*AdministrationApi* | [**listAdministrationAuditApiV1AdminAuditGet**](docs/AdministrationApi.md#listadministrationauditapiv1adminauditget) | **GET** /api/v1/admin/audit | List Administration Audit
*AdministrationApi* | [**listAdministrationControlsApiV1AdminControlsGet**](docs/AdministrationApi.md#listadministrationcontrolsapiv1admincontrolsget) | **GET** /api/v1/admin/controls | List Administration Controls
*AdministrationApi* | [**previewAdministrationControlApiV1AdminControlsPreviewPost**](docs/AdministrationApi.md#previewadministrationcontrolapiv1admincontrolspreviewpost) | **POST** /api/v1/admin/controls/preview | Preview Administration Control
*AuthenticationApi* | [**changeLocalPasswordApiV1AuthPasswordPost**](docs/AuthenticationApi.md#changelocalpasswordapiv1authpasswordpost) | **POST** /api/v1/auth/password | Change Local Password
*AuthenticationApi* | [**listAuthenticationProvidersApiV1AuthProvidersGet**](docs/AuthenticationApi.md#listauthenticationprovidersapiv1authprovidersget) | **GET** /api/v1/auth/providers | List Authentication Providers
*AuthenticationApi* | [**loginApiV1AuthLoginPost**](docs/AuthenticationApi.md#loginapiv1authloginpost) | **POST** /api/v1/auth/login | Login
*AuthenticationApi* | [**logoutAllApiV1AuthLogoutAllPost**](docs/AuthenticationApi.md#logoutallapiv1authlogoutallpost) | **POST** /api/v1/auth/logout-all | Logout All
*AuthenticationApi* | [**logoutApiV1AuthLogoutPost**](docs/AuthenticationApi.md#logoutapiv1authlogoutpost) | **POST** /api/v1/auth/logout | Logout
*AuthenticationApi* | [**revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete**](docs/AuthenticationApi.md#revokeprincipalsessionsapiv1adminprincipalsprincipalidsessionsdelete) | **DELETE** /api/v1/admin/principals/{principal_id}/sessions | Revoke Principal Sessions
*AuthenticationApi* | [**setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut**](docs/AuthenticationApi.md#setlocalpasswordapiv1adminprincipalsprincipalidlocalpasswordput) | **PUT** /api/v1/admin/principals/{principal_id}/local-password | Set Local Password
*AuthorizationApi* | [**addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut**](docs/AuthorizationApi.md#addgroupmemberapiv1admingroupsgroupidmembersmemberidput) | **PUT** /api/v1/admin/groups/{group_id}/members/{member_id} | Add Group Member
*AuthorizationApi* | [**createPrincipalApiV1AdminPrincipalsPost**](docs/AuthorizationApi.md#createprincipalapiv1adminprincipalspost) | **POST** /api/v1/admin/principals | Create Principal
*AuthorizationApi* | [**createRoleBindingApiV1AdminBindingsPost**](docs/AuthorizationApi.md#createrolebindingapiv1adminbindingspost) | **POST** /api/v1/admin/bindings | Create Role Binding
*AuthorizationApi* | [**deleteRoleBindingApiV1AdminBindingsBindingIdDelete**](docs/AuthorizationApi.md#deleterolebindingapiv1adminbindingsbindingiddelete) | **DELETE** /api/v1/admin/bindings/{binding_id} | Delete Role Binding
*AuthorizationApi* | [**explainAuthorizationApiV1AuthorizationExplainPost**](docs/AuthorizationApi.md#explainauthorizationapiv1authorizationexplainpost) | **POST** /api/v1/authorization/explain | Explain Authorization
*AuthorizationApi* | [**listPrincipalsApiV1AdminPrincipalsGet**](docs/AuthorizationApi.md#listprincipalsapiv1adminprincipalsget) | **GET** /api/v1/admin/principals | List Principals
*AuthorizationApi* | [**listRoleBindingsApiV1AdminBindingsGet**](docs/AuthorizationApi.md#listrolebindingsapiv1adminbindingsget) | **GET** /api/v1/admin/bindings | List Role Bindings
*AuthorizationApi* | [**listRolesApiV1AdminRolesGet**](docs/AuthorizationApi.md#listrolesapiv1adminrolesget) | **GET** /api/v1/admin/roles | List Roles
*AuthorizationApi* | [**removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete**](docs/AuthorizationApi.md#removegroupmemberapiv1admingroupsgroupidmembersmemberiddelete) | **DELETE** /api/v1/admin/groups/{group_id}/members/{member_id} | Remove Group Member
*AuthorizationApi* | [**setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut**](docs/AuthorizationApi.md#setnamespaceauthorizationboundaryapiv1admintenantstenantidnamespacesnamespaceauthorizationboundaryput) | **PUT** /api/v1/admin/tenants/{tenant_id}/namespaces/{namespace}/authorization-boundary | Set Namespace Authorization Boundary
*AuthorizationApi* | [**upsertRoleApiV1AdminRolesRoleNamePut**](docs/AuthorizationApi.md#upsertroleapiv1adminrolesrolenameput) | **PUT** /api/v1/admin/roles/{role_name} | Upsert Role
*BackfillsApi* | [**cancelBackfillApiV1BackfillsBackfillIdCancelPost**](docs/BackfillsApi.md#cancelbackfillapiv1backfillsbackfillidcancelpost) | **POST** /api/v1/backfills/{backfill_id}/cancel | Cancel Backfill
*BackfillsApi* | [**createBackfillApiV1BackfillsPost**](docs/BackfillsApi.md#createbackfillapiv1backfillspost) | **POST** /api/v1/backfills | Create Backfill
*BackfillsApi* | [**getBackfillApiV1BackfillsBackfillIdGet**](docs/BackfillsApi.md#getbackfillapiv1backfillsbackfillidget) | **GET** /api/v1/backfills/{backfill_id} | Get Backfill
*BackfillsApi* | [**listBackfillsApiV1BackfillsGet**](docs/BackfillsApi.md#listbackfillsapiv1backfillsget) | **GET** /api/v1/backfills | List Backfills
*BackfillsApi* | [**pauseBackfillApiV1BackfillsBackfillIdPausePost**](docs/BackfillsApi.md#pausebackfillapiv1backfillsbackfillidpausepost) | **POST** /api/v1/backfills/{backfill_id}/pause | Pause Backfill
*BackfillsApi* | [**previewBackfillApiV1BackfillsPreviewPost**](docs/BackfillsApi.md#previewbackfillapiv1backfillspreviewpost) | **POST** /api/v1/backfills/preview | Preview Backfill
*BackfillsApi* | [**resumeBackfillApiV1BackfillsBackfillIdResumePost**](docs/BackfillsApi.md#resumebackfillapiv1backfillsbackfillidresumepost) | **POST** /api/v1/backfills/{backfill_id}/resume | Resume Backfill
*BlueprintsApi* | [**getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet**](docs/BlueprintsApi.md#getblueprintversionapiv1blueprintsblueprintidversionget) | **GET** /api/v1/blueprints/{blueprint_id}/{version} | Get Blueprint Version
*BlueprintsApi* | [**getBlueprintsApiV1BlueprintsGet**](docs/BlueprintsApi.md#getblueprintsapiv1blueprintsget) | **GET** /api/v1/blueprints | Get Blueprints
*BlueprintsApi* | [**instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost**](docs/BlueprintsApi.md#instantiateblueprintdraftapiv1blueprintsblueprintidversioninstantiatepost) | **POST** /api/v1/blueprints/{blueprint_id}/{version}/instantiate | Instantiate Blueprint Draft
*BlueprintsApi* | [**simulatePlaygroundApiV1PlaygroundSimulatePost**](docs/BlueprintsApi.md#simulateplaygroundapiv1playgroundsimulatepost) | **POST** /api/v1/playground/simulate | Simulate Playground
*ChecksApi* | [**getCheckComplianceApiV1CheckComplianceGet**](docs/ChecksApi.md#getcheckcomplianceapiv1checkcomplianceget) | **GET** /api/v1/check-compliance | Get Check Compliance
*ChecksApi* | [**listCheckEvaluationsApiV1CheckEvaluationsGet**](docs/ChecksApi.md#listcheckevaluationsapiv1checkevaluationsget) | **GET** /api/v1/check-evaluations | List Check Evaluations
*ChecksApi* | [**listCheckPoliciesApiV1CheckPoliciesGet**](docs/ChecksApi.md#listcheckpoliciesapiv1checkpoliciesget) | **GET** /api/v1/check-policies | List Check Policies
*ChecksApi* | [**upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut**](docs/ChecksApi.md#upsertcheckpolicyapiv1checkpoliciesnamespacepolicykeyput) | **PUT** /api/v1/check-policies/{namespace}/{policy_key} | Upsert Check Policy
*ConfigurationApi* | [**evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet**](docs/ConfigurationApi.md#evaluatefeatureflagapiv1featureflagskeyevaluateget) | **GET** /api/v1/feature-flags/{key}/evaluate | Evaluate Feature Flag
*ConfigurationApi* | [**getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet**](docs/ConfigurationApi.md#getconfigurationdiagnosticsapiv1configurationdiagnosticsget) | **GET** /api/v1/configuration/diagnostics | Get Configuration Diagnostics
*ConfigurationApi* | [**getEffectiveConfigurationApiV1ConfigurationGet**](docs/ConfigurationApi.md#geteffectiveconfigurationapiv1configurationget) | **GET** /api/v1/configuration | Get Effective Configuration
*ConfigurationApi* | [**listFeatureFlagsApiV1FeatureFlagsGet**](docs/ConfigurationApi.md#listfeatureflagsapiv1featureflagsget) | **GET** /api/v1/feature-flags | List Feature Flags
*ConfigurationApi* | [**putFeatureFlagApiV1FeatureFlagsKeyPut**](docs/ConfigurationApi.md#putfeatureflagapiv1featureflagskeyput) | **PUT** /api/v1/feature-flags/{key} | Put Feature Flag
*ConfigurationApi* | [**reloadConfigurationApiV1ConfigurationReloadPost**](docs/ConfigurationApi.md#reloadconfigurationapiv1configurationreloadpost) | **POST** /api/v1/configuration/reload | Reload Configuration
*CredentialsApi* | [**exchangeWorkloadCredentialApiV1CredentialsExchangePost**](docs/CredentialsApi.md#exchangeworkloadcredentialapiv1credentialsexchangepost) | **POST** /api/v1/credentials/exchange | Exchange Workload Credential
*CredentialsApi* | [**issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost**](docs/CredentialsApi.md#issuecredentialapiv1adminprincipalsprincipalidcredentialspost) | **POST** /api/v1/admin/principals/{principal_id}/credentials | Issue Credential
*CredentialsApi* | [**listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet**](docs/CredentialsApi.md#listcredentialsapiv1adminprincipalsprincipalidcredentialsget) | **GET** /api/v1/admin/principals/{principal_id}/credentials | List Credentials
*CredentialsApi* | [**revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete**](docs/CredentialsApi.md#revokeallcredentialsapiv1adminprincipalsprincipalidcredentialsdelete) | **DELETE** /api/v1/admin/principals/{principal_id}/credentials | Revoke All Credentials
*CredentialsApi* | [**revokeCredentialApiV1AdminCredentialsCredentialIdDelete**](docs/CredentialsApi.md#revokecredentialapiv1admincredentialscredentialiddelete) | **DELETE** /api/v1/admin/credentials/{credential_id} | Revoke Credential
*CredentialsApi* | [**rotateCredentialApiV1AdminCredentialsCredentialIdRotatePost**](docs/CredentialsApi.md#rotatecredentialapiv1admincredentialscredentialidrotatepost) | **POST** /api/v1/admin/credentials/{credential_id}/rotate | Rotate Credential
*DashboardsApi* | [**deleteDashboardApiV1DashboardsDashboardIdDelete**](docs/DashboardsApi.md#deletedashboardapiv1dashboardsdashboardiddelete) | **DELETE** /api/v1/dashboards/{dashboard_id} | Delete Dashboard
*DashboardsApi* | [**executeDashboardQueryApiV1DashboardQueriesPost**](docs/DashboardsApi.md#executedashboardqueryapiv1dashboardqueriespost) | **POST** /api/v1/dashboard-queries | Execute Dashboard Query
*DashboardsApi* | [**exportDashboardApiV1DashboardsDashboardIdExportGet**](docs/DashboardsApi.md#exportdashboardapiv1dashboardsdashboardidexportget) | **GET** /api/v1/dashboards/{dashboard_id}/export | Export Dashboard
*DashboardsApi* | [**getDashboardApiV1DashboardsDashboardIdGet**](docs/DashboardsApi.md#getdashboardapiv1dashboardsdashboardidget) | **GET** /api/v1/dashboards/{dashboard_id} | Get Dashboard
*DashboardsApi* | [**listDashboardsApiV1DashboardsGet**](docs/DashboardsApi.md#listdashboardsapiv1dashboardsget) | **GET** /api/v1/dashboards | List Dashboards
*DashboardsApi* | [**putDashboardApiV1DashboardsDashboardIdPut**](docs/DashboardsApi.md#putdashboardapiv1dashboardsdashboardidput) | **PUT** /api/v1/dashboards/{dashboard_id} | Put Dashboard
*DashboardsApi* | [**renderDashboardApiV1DashboardsDashboardIdRenderPost**](docs/DashboardsApi.md#renderdashboardapiv1dashboardsdashboardidrenderpost) | **POST** /api/v1/dashboards/{dashboard_id}/render | Render Dashboard
*ExecutionsApi* | [**applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost**](docs/ExecutionsApi.md#applyexecutioncontrolapiv1executionsexecutionidinterventionspost) | **POST** /api/v1/executions/{execution_id}/interventions | Apply Execution Control
*ExecutionsApi* | [**createExecutionApiV1ExecutionsPost**](docs/ExecutionsApi.md#createexecutionapiv1executionspost) | **POST** /api/v1/executions | Create Execution
*ExecutionsApi* | [**createExecutionsBulkApiV1ExecutionsBulkPost**](docs/ExecutionsApi.md#createexecutionsbulkapiv1executionsbulkpost) | **POST** /api/v1/executions/bulk | Create Executions Bulk
*ExecutionsApi* | [**downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet**](docs/ExecutionsApi.md#downloadexecutionfileapiv1executionsexecutionidfilesartifactidget) | **GET** /api/v1/executions/{execution_id}/files/{artifact_id} | Download Execution File
*ExecutionsApi* | [**getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet**](docs/ExecutionsApi.md#getexecutionadmissionapiv1executionsexecutionidadmissionget) | **GET** /api/v1/executions/{execution_id}/admission | Get Execution Admission
*ExecutionsApi* | [**getExecutionApiV1ExecutionsExecutionIdGet**](docs/ExecutionsApi.md#getexecutionapiv1executionsexecutionidget) | **GET** /api/v1/executions/{execution_id} | Get Execution
*ExecutionsApi* | [**getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet**](docs/ExecutionsApi.md#getexecutionevidenceapiv1executionsexecutionidevidenceget) | **GET** /api/v1/executions/{execution_id}/evidence | Get Execution Evidence
*ExecutionsApi* | [**getExecutionGraphApiV1ExecutionsExecutionIdGraphGet**](docs/ExecutionsApi.md#getexecutiongraphapiv1executionsexecutionidgraphget) | **GET** /api/v1/executions/{execution_id}/graph | Get Execution Graph
*ExecutionsApi* | [**getExecutionLogsApiV1ExecutionsExecutionIdLogsGet**](docs/ExecutionsApi.md#getexecutionlogsapiv1executionsexecutionidlogsget) | **GET** /api/v1/executions/{execution_id}/logs | Get Execution Logs
*ExecutionsApi* | [**getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet**](docs/ExecutionsApi.md#getexecutionparentsubflowapiv1executionsexecutionidparentsubflowget) | **GET** /api/v1/executions/{execution_id}/parent-subflow | Get Execution Parent Subflow
*ExecutionsApi* | [**getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet**](docs/ExecutionsApi.md#gettaskadmissionapiv1taskrunstaskrunidadmissionget) | **GET** /api/v1/task-runs/{task_run_id}/admission | Get Task Admission
*ExecutionsApi* | [**listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet**](docs/ExecutionsApi.md#listexecutioncontrolhistoryapiv1executionsexecutionidinterventionsget) | **GET** /api/v1/executions/{execution_id}/interventions | List Execution Control History
*ExecutionsApi* | [**listExecutionFilesApiV1ExecutionsExecutionIdFilesGet**](docs/ExecutionsApi.md#listexecutionfilesapiv1executionsexecutionidfilesget) | **GET** /api/v1/executions/{execution_id}/files | List Execution Files
*ExecutionsApi* | [**listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet**](docs/ExecutionsApi.md#listexecutionsubflowsapiv1executionsexecutionidsubflowsget) | **GET** /api/v1/executions/{execution_id}/subflows | List Execution Subflows
*ExecutionsApi* | [**listExecutionsApiV1ExecutionsGet**](docs/ExecutionsApi.md#listexecutionsapiv1executionsget) | **GET** /api/v1/executions | List Executions
*ExecutionsApi* | [**previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost**](docs/ExecutionsApi.md#previewexecutioncontrolapiv1executionsexecutionidinterventionspreviewpost) | **POST** /api/v1/executions/{execution_id}/interventions/preview | Preview Execution Control
*ExecutionsApi* | [**reduceExecutionEventsApiV1ExecutionsReducePost**](docs/ExecutionsApi.md#reduceexecutioneventsapiv1executionsreducepost) | **POST** /api/v1/executions/reduce | Reduce Execution Events
*ExecutionsApi* | [**resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost**](docs/ExecutionsApi.md#resumetaskrunapiv1executionsexecutionidtaskrunstaskrunidresumepost) | **POST** /api/v1/executions/{execution_id}/task-runs/{task_run_id}/resume | Resume Task Run
*ExecutionsApi* | [**streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet**](docs/ExecutionsApi.md#streamexecutionevidenceapiv1executionsexecutionidevidencestreamget) | **GET** /api/v1/executions/{execution_id}/evidence/stream | Stream Execution Evidence
*ExecutionsApi* | [**streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet**](docs/ExecutionsApi.md#streamexecutionlogsapiv1executionsexecutionidlogsstreamget) | **GET** /api/v1/executions/{execution_id}/logs/stream | Stream Execution Logs
*FlowsApi* | [**applyFlowApiV1FlowsPut**](docs/FlowsApi.md#applyflowapiv1flowsput) | **PUT** /api/v1/flows | Apply Flow
*FlowsApi* | [**deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete**](docs/FlowsApi.md#deleteflowrevisionapiv1flowsnamespaceflowidrevisionsrevisiondelete) | **DELETE** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision} | Delete Flow Revision
*FlowsApi* | [**diffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPost**](docs/FlowsApi.md#diffflowdraftapiv1flowsnamespaceflowidrevisionsrevisiondiffdraftpost) | **POST** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/diff-draft | Diff Flow Draft
*FlowsApi* | [**diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet**](docs/FlowsApi.md#diffflowrevisionsapiv1flowsnamespaceflowidrevisionsdiffget) | **GET** /api/v1/flows/{namespace}/{flow_id}/revisions/diff | Diff Flow Revisions
*FlowsApi* | [**exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet**](docs/FlowsApi.md#exportflowdocumentapiv1flowsnamespaceflowiddocumentget) | **GET** /api/v1/flows/{namespace}/{flow_id}/document | Export Flow Document
*FlowsApi* | [**formatFlowApiV1FlowsFormatPost**](docs/FlowsApi.md#formatflowapiv1flowsformatpost) | **POST** /api/v1/flows/format | Format Flow
*FlowsApi* | [**getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet**](docs/FlowsApi.md#getflowdatacontractapiv1flowsnamespaceflowiddatacontractget) | **GET** /api/v1/flows/{namespace}/{flow_id}/data-contract | Get Flow Data Contract
*FlowsApi* | [**getFlowEditorSchemaApiV1FlowsEditorSchemaGet**](docs/FlowsApi.md#getfloweditorschemaapiv1flowseditorschemaget) | **GET** /api/v1/flows/editor/schema | Get Flow Editor Schema
*FlowsApi* | [**getFlowGraphApiV1FlowsNamespaceFlowIdGraphGet**](docs/FlowsApi.md#getflowgraphapiv1flowsnamespaceflowidgraphget) | **GET** /api/v1/flows/{namespace}/{flow_id}/graph | Get Flow Graph
*FlowsApi* | [**getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet**](docs/FlowsApi.md#getflowmetadataapiv1flowsnamespaceflowidmetadataget) | **GET** /api/v1/flows/{namespace}/{flow_id}/metadata | Get Flow Metadata
*FlowsApi* | [**listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet**](docs/FlowsApi.md#listflowrevisionsapiv1flowsnamespaceflowidrevisionsget) | **GET** /api/v1/flows/{namespace}/{flow_id}/revisions | List Flow Revisions
*FlowsApi* | [**listFlowsApiV1FlowsGet**](docs/FlowsApi.md#listflowsapiv1flowsget) | **GET** /api/v1/flows | List Flows
*FlowsApi* | [**previewFlowExpressionApiV1FlowsExpressionsPreviewPost**](docs/FlowsApi.md#previewflowexpressionapiv1flowsexpressionspreviewpost) | **POST** /api/v1/flows/expressions/preview | Preview Flow Expression
*FlowsApi* | [**promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut**](docs/FlowsApi.md#promoteflowrevisionapiv1flowsnamespaceflowidrevisionsrevisionlifecycleput) | **PUT** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/lifecycle | Promote Flow Revision
*FlowsApi* | [**restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost**](docs/FlowsApi.md#restoreflowrevisionapiv1flowsnamespaceflowidrevisionsrevisionrestorepost) | **POST** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/restore | Restore Flow Revision
*FlowsApi* | [**validateFlowApiV1FlowsValidatePost**](docs/FlowsApi.md#validateflowapiv1flowsvalidatepost) | **POST** /api/v1/flows/validate | Validate Flow
*NamespaceResourcesApi* | [**deleteNamespaceFileApiV1NamespacesNamespaceFilesPathDelete**](docs/NamespaceResourcesApi.md#deletenamespacefileapiv1namespacesnamespacefilespathdelete) | **DELETE** /api/v1/namespaces/{namespace}/files/{path} | Delete Namespace File
*NamespaceResourcesApi* | [**deleteNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyDelete**](docs/NamespaceResourcesApi.md#deletenamespacekeyvalueapiv1namespacesnamespacekeyvalueskeydelete) | **DELETE** /api/v1/namespaces/{namespace}/key-values/{key} | Delete Namespace Key Value
*NamespaceResourcesApi* | [**deleteNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyDelete**](docs/NamespaceResourcesApi.md#deletenamespacesecretbindingapiv1namespacesnamespacesecretbindingskeydelete) | **DELETE** /api/v1/namespaces/{namespace}/secret-bindings/{key} | Delete Namespace Secret Binding
*NamespaceResourcesApi* | [**downloadNamespaceFileApiV1NamespacesNamespaceFilesPathGet**](docs/NamespaceResourcesApi.md#downloadnamespacefileapiv1namespacesnamespacefilespathget) | **GET** /api/v1/namespaces/{namespace}/files/{path} | Download Namespace File
*NamespaceResourcesApi* | [**exportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundleGet**](docs/NamespaceResourcesApi.md#exportnamespaceresourcebundleapiv1namespacesnamespaceresourcebundleget) | **GET** /api/v1/namespaces/{namespace}/resource-bundle | Export Namespace Resource Bundle
*NamespaceResourcesApi* | [**getNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyGet**](docs/NamespaceResourcesApi.md#getnamespacekeyvalueapiv1namespacesnamespacekeyvalueskeyget) | **GET** /api/v1/namespaces/{namespace}/key-values/{key} | Get Namespace Key Value
*NamespaceResourcesApi* | [**importNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundlePost**](docs/NamespaceResourcesApi.md#importnamespaceresourcebundleapiv1namespacesnamespaceresourcebundlepost) | **POST** /api/v1/namespaces/{namespace}/resource-bundle | Import Namespace Resource Bundle
*NamespaceResourcesApi* | [**listNamespaceFileVersionsApiV1NamespacesNamespaceFilesPathVersionsGet**](docs/NamespaceResourcesApi.md#listnamespacefileversionsapiv1namespacesnamespacefilespathversionsget) | **GET** /api/v1/namespaces/{namespace}/files/{path}/versions | List Namespace File Versions
*NamespaceResourcesApi* | [**listNamespaceFilesApiV1NamespacesNamespaceFilesGet**](docs/NamespaceResourcesApi.md#listnamespacefilesapiv1namespacesnamespacefilesget) | **GET** /api/v1/namespaces/{namespace}/files | List Namespace Files
*NamespaceResourcesApi* | [**listNamespaceKeyValueChangesApiV1NamespacesNamespaceKeyValuesChangesGet**](docs/NamespaceResourcesApi.md#listnamespacekeyvaluechangesapiv1namespacesnamespacekeyvalueschangesget) | **GET** /api/v1/namespaces/{namespace}/key-values/changes | List Namespace Key Value Changes
*NamespaceResourcesApi* | [**listNamespaceKeyValuesApiV1NamespacesNamespaceKeyValuesGet**](docs/NamespaceResourcesApi.md#listnamespacekeyvaluesapiv1namespacesnamespacekeyvaluesget) | **GET** /api/v1/namespaces/{namespace}/key-values | List Namespace Key Values
*NamespaceResourcesApi* | [**listNamespaceSecretBindingsApiV1NamespacesNamespaceSecretBindingsGet**](docs/NamespaceResourcesApi.md#listnamespacesecretbindingsapiv1namespacesnamespacesecretbindingsget) | **GET** /api/v1/namespaces/{namespace}/secret-bindings | List Namespace Secret Bindings
*NamespaceResourcesApi* | [**moveNamespaceFileApiV1NamespacesNamespaceFilesPathMovePost**](docs/NamespaceResourcesApi.md#movenamespacefileapiv1namespacesnamespacefilespathmovepost) | **POST** /api/v1/namespaces/{namespace}/files/{path}/move | Move Namespace File
*NamespaceResourcesApi* | [**putNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyPut**](docs/NamespaceResourcesApi.md#putnamespacekeyvalueapiv1namespacesnamespacekeyvalueskeyput) | **PUT** /api/v1/namespaces/{namespace}/key-values/{key} | Put Namespace Key Value
*NamespaceResourcesApi* | [**putNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyPut**](docs/NamespaceResourcesApi.md#putnamespacesecretbindingapiv1namespacesnamespacesecretbindingskeyput) | **PUT** /api/v1/namespaces/{namespace}/secret-bindings/{key} | Put Namespace Secret Binding
*NamespaceResourcesApi* | [**uploadNamespaceFileApiV1NamespacesNamespaceFilesPathPut**](docs/NamespaceResourcesApi.md#uploadnamespacefileapiv1namespacesnamespacefilespathput) | **PUT** /api/v1/namespaces/{namespace}/files/{path} | Upload Namespace File
*NamespacesApi* | [**getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet**](docs/NamespacesApi.md#getnamespaceworkflowmetadataapiv1namespacesnamespaceworkflowmetadataget) | **GET** /api/v1/namespaces/{namespace}/workflow-metadata | Get Namespace Workflow Metadata
*NamespacesApi* | [**upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut**](docs/NamespacesApi.md#upsertnamespaceworkflowmetadataapiv1namespacesnamespaceworkflowmetadataput) | **PUT** /api/v1/namespaces/{namespace}/workflow-metadata | Upsert Namespace Workflow Metadata
*OperationsApi* | [**drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost**](docs/OperationsApi.md#drainserviceinstanceapiv1operationsservicesinstanceiddrainpost) | **POST** /api/v1/operations/services/{instance_id}/drain | Drain Service Instance
*OperationsApi* | [**getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet**](docs/OperationsApi.md#getadmissiondiagnosticsapiv1admissionsdiagnosticsget) | **GET** /api/v1/admissions/diagnostics | Get Admission Diagnostics
*OperationsApi* | [**getReconciliationApiV1ReconciliationsRunIdGet**](docs/OperationsApi.md#getreconciliationapiv1reconciliationsrunidget) | **GET** /api/v1/reconciliations/{run_id} | Get Reconciliation
*OperationsApi* | [**getServiceTopologyApiV1OperationsTopologyGet**](docs/OperationsApi.md#getservicetopologyapiv1operationstopologyget) | **GET** /api/v1/operations/topology | Get Service Topology
*OperationsApi* | [**listReconciliationsApiV1ReconciliationsGet**](docs/OperationsApi.md#listreconciliationsapiv1reconciliationsget) | **GET** /api/v1/reconciliations | List Reconciliations
*OperationsApi* | [**reconcileAdmissionsApiV1AdmissionsReconcilePost**](docs/OperationsApi.md#reconcileadmissionsapiv1admissionsreconcilepost) | **POST** /api/v1/admissions/reconcile | Reconcile Admissions
*OperationsApi* | [**runReconciliationApiV1ReconciliationsPost**](docs/OperationsApi.md#runreconciliationapiv1reconciliationspost) | **POST** /api/v1/reconciliations | Run Reconciliation
*PluginsApi* | [**downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet**](docs/PluginsApi.md#downloadpluginregistrybundleapiv1pluginregistryblobsdigestget) | **GET** /api/v1/plugin-registry/blobs/{digest} | Download Plugin Registry Bundle
*PluginsApi* | [**exportPluginRegistryApiV1PluginRegistryOfflineExportGet**](docs/PluginsApi.md#exportpluginregistryapiv1pluginregistryofflineexportget) | **GET** /api/v1/plugin-registry/offline-export | Export Plugin Registry
*PluginsApi* | [**getPluginRegistryIndexApiV1PluginRegistryIndexGet**](docs/PluginsApi.md#getpluginregistryindexapiv1pluginregistryindexget) | **GET** /api/v1/plugin-registry/index | Get Plugin Registry Index
*PluginsApi* | [**getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet**](docs/PluginsApi.md#getpluginregistrypackageapiv1pluginregistrypackagesnameversionget) | **GET** /api/v1/plugin-registry/packages/{name}/{version} | Get Plugin Registry Package
*PluginsApi* | [**importPluginRegistryApiV1PluginRegistryOfflineImportPost**](docs/PluginsApi.md#importpluginregistryapiv1pluginregistryofflineimportpost) | **POST** /api/v1/plugin-registry/offline-import | Import Plugin Registry
*PluginsApi* | [**installPluginBundleApiV1PluginsInstallPost**](docs/PluginsApi.md#installpluginbundleapiv1pluginsinstallpost) | **POST** /api/v1/plugins/install | Install Plugin Bundle
*PluginsApi* | [**isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet**](docs/PluginsApi.md#isolatedpluginruntimestatusapiv1pluginsisolatedruntimeget) | **GET** /api/v1/plugins/isolated-runtime | Isolated Plugin Runtime Status
*PluginsApi* | [**listPluginsApiV1PluginsGet**](docs/PluginsApi.md#listpluginsapiv1pluginsget) | **GET** /api/v1/plugins | List Plugins
*PluginsApi* | [**publishPluginRegistryPackageApiV1PluginRegistryPackagesPost**](docs/PluginsApi.md#publishpluginregistrypackageapiv1pluginregistrypackagespost) | **POST** /api/v1/plugin-registry/packages | Publish Plugin Registry Package
*PluginsApi* | [**refreshPluginsApiV1PluginsRefreshPost**](docs/PluginsApi.md#refreshpluginsapiv1pluginsrefreshpost) | **POST** /api/v1/plugins/refresh | Refresh Plugins
*PluginsApi* | [**trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet**](docs/PluginsApi.md#trustedpluginruntimestatusapiv1pluginstrustedruntimeget) | **GET** /api/v1/plugins/trusted-runtime | Trusted Plugin Runtime Status
*PluginsApi* | [**yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost**](docs/PluginsApi.md#yankpluginregistrypackageapiv1pluginregistrypackagesnameversionyankpost) | **POST** /api/v1/plugin-registry/packages/{name}/{version}/yank | Yank Plugin Registry Package
*RealtimeApi* | [**createWebhookSubscriptionApiV1WebhookSubscriptionsPost**](docs/RealtimeApi.md#createwebhooksubscriptionapiv1webhooksubscriptionspost) | **POST** /api/v1/webhook-subscriptions | Create Webhook Subscription
*RealtimeApi* | [**listRealtimeEventsApiV1RealtimeEventsGet**](docs/RealtimeApi.md#listrealtimeeventsapiv1realtimeeventsget) | **GET** /api/v1/realtime/events | List Realtime Events
*RealtimeApi* | [**listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet**](docs/RealtimeApi.md#listwebhookdeliveryhistoryapiv1webhooksubscriptionssubscriptioniddeliveriesget) | **GET** /api/v1/webhook-subscriptions/{subscription_id}/deliveries | List Webhook Delivery History
*RealtimeApi* | [**listWebhookSubscriptionsApiV1WebhookSubscriptionsGet**](docs/RealtimeApi.md#listwebhooksubscriptionsapiv1webhooksubscriptionsget) | **GET** /api/v1/webhook-subscriptions | List Webhook Subscriptions
*RealtimeApi* | [**replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost**](docs/RealtimeApi.md#replaywebhookdeliveryapiv1webhookdeliveriesdeliveryidreplaypost) | **POST** /api/v1/webhook-deliveries/{delivery_id}/replay | Replay Webhook Delivery
*RealtimeApi* | [**rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost**](docs/RealtimeApi.md#rotatewebhooksubscriptionsecretapiv1webhooksubscriptionssubscriptionidrotatesecretpost) | **POST** /api/v1/webhook-subscriptions/{subscription_id}/rotate-secret | Rotate Webhook Subscription Secret
*RealtimeApi* | [**streamRealtimeEventsApiV1RealtimeStreamGet**](docs/RealtimeApi.md#streamrealtimeeventsapiv1realtimestreamget) | **GET** /api/v1/realtime/stream | Stream Realtime Events
*RealtimeApi* | [**testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost**](docs/RealtimeApi.md#testwebhooksubscriptionapiv1webhooksubscriptionssubscriptionidtestpost) | **POST** /api/v1/webhook-subscriptions/{subscription_id}/test | Test Webhook Subscription
*SearchApi* | [**getSearchStatusApiV1SearchStatusGet**](docs/SearchApi.md#getsearchstatusapiv1searchstatusget) | **GET** /api/v1/search/status | Get Search Status
*SearchApi* | [**rebuildSearchProjectionApiV1SearchRebuildPost**](docs/SearchApi.md#rebuildsearchprojectionapiv1searchrebuildpost) | **POST** /api/v1/search/rebuild | Rebuild Search Projection
*SearchApi* | [**searchResourcesApiV1SearchPost**](docs/SearchApi.md#searchresourcesapiv1searchpost) | **POST** /api/v1/search | Search Resources
*SystemApi* | [**healthHealthGet**](docs/SystemApi.md#healthhealthget) | **GET** /health | Health
*SystemApi* | [**readyReadyGet**](docs/SystemApi.md#readyreadyget) | **GET** /ready | Ready
*TaskCacheApi* | [**listTaskCacheEntriesApiV1TaskCacheGet**](docs/TaskCacheApi.md#listtaskcacheentriesapiv1taskcacheget) | **GET** /api/v1/task-cache | List Task Cache Entries
*TaskCacheApi* | [**purgeTaskCacheEntriesApiV1TaskCachePurgePost**](docs/TaskCacheApi.md#purgetaskcacheentriesapiv1taskcachepurgepost) | **POST** /api/v1/task-cache/purge | Purge Task Cache Entries
*TenantsApi* | [**createTenantApiV1AdminTenantsPost**](docs/TenantsApi.md#createtenantapiv1admintenantspost) | **POST** /api/v1/admin/tenants | Create Tenant
*TenantsApi* | [**deleteTenantApiV1AdminTenantsTenantSlugDelete**](docs/TenantsApi.md#deletetenantapiv1admintenantstenantslugdelete) | **DELETE** /api/v1/admin/tenants/{tenant_slug} | Delete Tenant
*TenantsApi* | [**exportTenantApiV1AdminTenantsTenantSlugExportsPost**](docs/TenantsApi.md#exporttenantapiv1admintenantstenantslugexportspost) | **POST** /api/v1/admin/tenants/{tenant_slug}/exports | Export Tenant
*TenantsApi* | [**getTenantApiV1AdminTenantsTenantSlugGet**](docs/TenantsApi.md#gettenantapiv1admintenantstenantslugget) | **GET** /api/v1/admin/tenants/{tenant_slug} | Get Tenant
*TenantsApi* | [**listTenantsApiV1AdminTenantsGet**](docs/TenantsApi.md#listtenantsapiv1admintenantsget) | **GET** /api/v1/admin/tenants | List Tenants
*TenantsApi* | [**restoreTenantApiV1AdminTenantsTenantSlugRestorePost**](docs/TenantsApi.md#restoretenantapiv1admintenantstenantslugrestorepost) | **POST** /api/v1/admin/tenants/{tenant_slug}/restore | Restore Tenant
*TenantsApi* | [**suspendTenantApiV1AdminTenantsTenantSlugSuspendPost**](docs/TenantsApi.md#suspendtenantapiv1admintenantstenantslugsuspendpost) | **POST** /api/v1/admin/tenants/{tenant_slug}/suspend | Suspend Tenant
*TenantsApi* | [**updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut**](docs/TenantsApi.md#updatetenantpolicyapiv1admintenantstenantslugpolicyput) | **PUT** /api/v1/admin/tenants/{tenant_slug}/policy | Update Tenant Policy
*TriggersApi* | [**listTriggerOccurrencesApiV1TriggerOccurrencesGet**](docs/TriggersApi.md#listtriggeroccurrencesapiv1triggeroccurrencesget) | **GET** /api/v1/trigger-occurrences | List Trigger Occurrences
*TriggersApi* | [**listTriggerRuntimeStatesApiV1TriggersGet**](docs/TriggersApi.md#listtriggerruntimestatesapiv1triggersget) | **GET** /api/v1/triggers | List Trigger Runtime States
*TriggersApi* | [**pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost**](docs/TriggersApi.md#pausetriggerruntimeapiv1triggersnamespaceflowidtriggeridpausepost) | **POST** /api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/pause | Pause Trigger Runtime
*TriggersApi* | [**previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet**](docs/TriggersApi.md#previewscheduleapiv1flowsnamespaceflowidschedulestriggeridpreviewget) | **GET** /api/v1/flows/{namespace}/{flow_id}/schedules/{trigger_id}/preview | Preview Schedule
*TriggersApi* | [**replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost**](docs/TriggersApi.md#replaytriggeroccurrenceapiv1triggeroccurrencesoccurrenceidreplaypost) | **POST** /api/v1/trigger-occurrences/{occurrence_id}/replay | Replay Trigger Occurrence
*TriggersApi* | [**resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost**](docs/TriggersApi.md#resumetriggerruntimeapiv1triggersnamespaceflowidtriggeridresumepost) | **POST** /api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/resume | Resume Trigger Runtime
*TriggersApi* | [**triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost**](docs/TriggersApi.md#triggerwebhookapiv1webhooksnamespaceflowidtriggeridpost) | **POST** /api/v1/webhooks/{namespace}/{flow_id}/{trigger_id} | Trigger Webhook
*UiApi* | [**getUiSessionApiV1UiSessionGet**](docs/UiApi.md#getuisessionapiv1uisessionget) | **GET** /api/v1/ui/session | Get Ui Session
*WorkersApi* | [**drainWorkerApiV1WorkersWorkerIdDrainPost**](docs/WorkersApi.md#drainworkerapiv1workersworkeriddrainpost) | **POST** /api/v1/workers/{worker_id}/drain | Drain Worker
*WorkersApi* | [**listRunnerCapabilitiesApiV1RunnersCapabilitiesGet**](docs/WorkersApi.md#listrunnercapabilitiesapiv1runnerscapabilitiesget) | **GET** /api/v1/runners/capabilities | List Runner Capabilities
*WorkersApi* | [**listWorkersApiV1WorkersGet**](docs/WorkersApi.md#listworkersapiv1workersget) | **GET** /api/v1/workers | List Workers


### Models

- [Action](docs/Action.md)
- [AdministrationApplyRequest](docs/AdministrationApplyRequest.md)
- [AdministrationAuditEntry](docs/AdministrationAuditEntry.md)
- [AdministrationControl](docs/AdministrationControl.md)
- [AdministrationControlDraft](docs/AdministrationControlDraft.md)
- [AdministrationControlKey](docs/AdministrationControlKey.md)
- [AdministrationImpactPreview](docs/AdministrationImpactPreview.md)
- [AdmissionDecision](docs/AdmissionDecision.md)
- [AdmissionDiagnostics](docs/AdmissionDiagnostics.md)
- [AdmissionOutcome](docs/AdmissionOutcome.md)
- [AdmissionResourceType](docs/AdmissionResourceType.md)
- [AdmissionScope](docs/AdmissionScope.md)
- [AuthenticationProviderDescriptor](docs/AuthenticationProviderDescriptor.md)
- [AuthenticationProviderKind](docs/AuthenticationProviderKind.md)
- [AuthorizationDecision](docs/AuthorizationDecision.md)
- [AuthorizationExplanationRequest](docs/AuthorizationExplanationRequest.md)
- [AuthorizationScopeType](docs/AuthorizationScopeType.md)
- [BackfillActionRequest](docs/BackfillActionRequest.md)
- [BackfillPreview](docs/BackfillPreview.md)
- [BackfillRecord](docs/BackfillRecord.md)
- [BackfillSelection](docs/BackfillSelection.md)
- [BackfillSelectionKind](docs/BackfillSelectionKind.md)
- [BackfillSpec](docs/BackfillSpec.md)
- [BackfillState](docs/BackfillState.md)
- [BlueprintCatalogSource](docs/BlueprintCatalogSource.md)
- [BlueprintDefinition](docs/BlueprintDefinition.md)
- [BlueprintDraftResponse](docs/BlueprintDraftResponse.md)
- [BlueprintInstantiationRequest](docs/BlueprintInstantiationRequest.md)
- [BlueprintParameter](docs/BlueprintParameter.md)
- [BlueprintParameterKind](docs/BlueprintParameterKind.md)
- [BlueprintProvenance](docs/BlueprintProvenance.md)
- [BlueprintSummary](docs/BlueprintSummary.md)
- [BulkExecutionItemResult](docs/BulkExecutionItemResult.md)
- [BulkExecutionRequest](docs/BulkExecutionRequest.md)
- [ChangeLocalPasswordRequest](docs/ChangeLocalPasswordRequest.md)
- [CheckActionDefinition](docs/CheckActionDefinition.md)
- [CheckComplianceSummary](docs/CheckComplianceSummary.md)
- [CheckDefinition](docs/CheckDefinition.md)
- [CheckEvaluation](docs/CheckEvaluation.md)
- [CheckEvaluationPoint](docs/CheckEvaluationPoint.md)
- [CheckOutcome](docs/CheckOutcome.md)
- [CheckPolicySource](docs/CheckPolicySource.md)
- [CheckPolicyUpsertRequest](docs/CheckPolicyUpsertRequest.md)
- [ConfigurationDiagnosticBundle](docs/ConfigurationDiagnosticBundle.md)
- [ConfigurationEntry](docs/ConfigurationEntry.md)
- [ConfigurationSnapshot](docs/ConfigurationSnapshot.md)
- [CreateExecutionRequest](docs/CreateExecutionRequest.md)
- [CreateTenantRequest](docs/CreateTenantRequest.md)
- [CredentialKind](docs/CredentialKind.md)
- [CredentialMetadata](docs/CredentialMetadata.md)
- [CredentialStatus](docs/CredentialStatus.md)
- [CronOccurrence](docs/CronOccurrence.md)
- [DashboardAggregation](docs/DashboardAggregation.md)
- [DashboardDataSource](docs/DashboardDataSource.md)
- [DashboardDefinition](docs/DashboardDefinition.md)
- [DashboardDefinitionSource](docs/DashboardDefinitionSource.md)
- [DashboardFilters](docs/DashboardFilters.md)
- [DashboardMeasure](docs/DashboardMeasure.md)
- [DashboardQuery](docs/DashboardQuery.md)
- [DashboardQueryResult](docs/DashboardQueryResult.md)
- [DashboardRender](docs/DashboardRender.md)
- [DashboardSpec](docs/DashboardSpec.md)
- [DashboardVisibility](docs/DashboardVisibility.md)
- [DashboardVisualization](docs/DashboardVisualization.md)
- [DashboardWidget](docs/DashboardWidget.md)
- [DashboardWidgetResult](docs/DashboardWidgetResult.md)
- [ExchangeCredentialRequest](docs/ExchangeCredentialRequest.md)
- [ExecutionArtifact](docs/ExecutionArtifact.md)
- [ExecutionDetail](docs/ExecutionDetail.md)
- [ExecutionEvent](docs/ExecutionEvent.md)
- [ExecutionEventType](docs/ExecutionEventType.md)
- [ExecutionEvidenceEvent](docs/ExecutionEvidenceEvent.md)
- [ExecutionEvidenceKind](docs/ExecutionEvidenceKind.md)
- [ExecutionEvidencePage](docs/ExecutionEvidencePage.md)
- [ExecutionInterventionAction](docs/ExecutionInterventionAction.md)
- [ExecutionInterventionPreview](docs/ExecutionInterventionPreview.md)
- [ExecutionInterventionPreviewRequest](docs/ExecutionInterventionPreviewRequest.md)
- [ExecutionInterventionRecord](docs/ExecutionInterventionRecord.md)
- [ExecutionInterventionRequest](docs/ExecutionInterventionRequest.md)
- [ExecutionSnapshot](docs/ExecutionSnapshot.md)
- [ExecutionState](docs/ExecutionState.md)
- [ExpressionPreviewRequest](docs/ExpressionPreviewRequest.md)
- [ExpressionPreviewResponse](docs/ExpressionPreviewResponse.md)
- [ExtensionType](docs/ExtensionType.md)
- [FailoverStatus](docs/FailoverStatus.md)
- [FailureCategory](docs/FailureCategory.md)
- [FeatureFlag](docs/FeatureFlag.md)
- [FeatureFlagDecision](docs/FeatureFlagDecision.md)
- [FeatureFlagScope](docs/FeatureFlagScope.md)
- [FeatureFlagUpsertRequest](docs/FeatureFlagUpsertRequest.md)
- [FlowDataContract](docs/FlowDataContract.md)
- [FlowDocumentExport](docs/FlowDocumentExport.md)
- [FlowEditorSchemaResponse](docs/FlowEditorSchemaResponse.md)
- [FlowFormatResponse](docs/FlowFormatResponse.md)
- [FlowGraph](docs/FlowGraph.md)
- [FlowGraphEdge](docs/FlowGraphEdge.md)
- [FlowGraphNode](docs/FlowGraphNode.md)
- [FlowLifecycle](docs/FlowLifecycle.md)
- [FlowMetadataResponse](docs/FlowMetadataResponse.md)
- [FlowRevisionDiff](docs/FlowRevisionDiff.md)
- [FlowRevisionLifecycleRequest](docs/FlowRevisionLifecycleRequest.md)
- [FlowRevisionRecord](docs/FlowRevisionRecord.md)
- [FlowRevisionRestoreRequest](docs/FlowRevisionRestoreRequest.md)
- [FlowValidationResult](docs/FlowValidationResult.md)
- [Gte](docs/Gte.md)
- [HTTPValidationError](docs/HTTPValidationError.md)
- [HealthResponse](docs/HealthResponse.md)
- [IsolatedPluginRuntimeSnapshot](docs/IsolatedPluginRuntimeSnapshot.md)
- [IsolatedPluginRuntimeStatus](docs/IsolatedPluginRuntimeStatus.md)
- [IsolatedPluginState](docs/IsolatedPluginState.md)
- [IssueCredentialRequest](docs/IssueCredentialRequest.md)
- [IssuedCredentialResponse](docs/IssuedCredentialResponse.md)
- [KeyValueChange](docs/KeyValueChange.md)
- [KeyValueEntry](docs/KeyValueEntry.md)
- [KeyValueExport](docs/KeyValueExport.md)
- [KeyValueType](docs/KeyValueType.md)
- [KeyValueWrite](docs/KeyValueWrite.md)
- [LabelNormalization](docs/LabelNormalization.md)
- [LocationInner](docs/LocationInner.md)
- [LogLevel](docs/LogLevel.md)
- [LogSourceStream](docs/LogSourceStream.md)
- [LoginRequest](docs/LoginRequest.md)
- [LoginResponse](docs/LoginResponse.md)
- [Lte](docs/Lte.md)
- [MetricKind](docs/MetricKind.md)
- [NamespaceAuthorizationBoundary](docs/NamespaceAuthorizationBoundary.md)
- [NamespaceCheckPolicy](docs/NamespaceCheckPolicy.md)
- [NamespaceFile](docs/NamespaceFile.md)
- [NamespaceFileExport](docs/NamespaceFileExport.md)
- [NamespaceFileMoveRequest](docs/NamespaceFileMoveRequest.md)
- [NamespaceFileVersion](docs/NamespaceFileVersion.md)
- [NamespaceResourceBundle](docs/NamespaceResourceBundle.md)
- [NamespaceResourceImportResult](docs/NamespaceResourceImportResult.md)
- [NamespaceWorkflowMetadata](docs/NamespaceWorkflowMetadata.md)
- [NamespaceWorkflowMetadataUpdate](docs/NamespaceWorkflowMetadataUpdate.md)
- [NamespaceWorkflowMetadataView](docs/NamespaceWorkflowMetadataView.md)
- [Permission](docs/Permission.md)
- [PermissionAction](docs/PermissionAction.md)
- [PermissionEffect](docs/PermissionEffect.md)
- [PersistedExecution](docs/PersistedExecution.md)
- [PersistedFlow](docs/PersistedFlow.md)
- [PersistedSubflow](docs/PersistedSubflow.md)
- [PersistedTaskRun](docs/PersistedTaskRun.md)
- [PersistedTaskRunSummary](docs/PersistedTaskRunSummary.md)
- [PlaygroundSafety](docs/PlaygroundSafety.md)
- [PlaygroundSimulationRequest](docs/PlaygroundSimulationRequest.md)
- [PlaygroundSimulationResponse](docs/PlaygroundSimulationResponse.md)
- [PlaygroundStep](docs/PlaygroundStep.md)
- [PluginCapabilities](docs/PluginCapabilities.md)
- [PluginCatalogSnapshot](docs/PluginCatalogSnapshot.md)
- [PluginCertificationStatus](docs/PluginCertificationStatus.md)
- [PluginCompatibility](docs/PluginCompatibility.md)
- [PluginDefaultDefinition](docs/PluginDefaultDefinition.md)
- [PluginDependency](docs/PluginDependency.md)
- [PluginDeprecation](docs/PluginDeprecation.md)
- [PluginDocumentation](docs/PluginDocumentation.md)
- [PluginEntryPoint](docs/PluginEntryPoint.md)
- [PluginFilesystemAccess](docs/PluginFilesystemAccess.md)
- [PluginLifecycleStatus](docs/PluginLifecycleStatus.md)
- [PluginManifest](docs/PluginManifest.md)
- [PluginMarketplaceSignals](docs/PluginMarketplaceSignals.md)
- [PluginNetworkAccess](docs/PluginNetworkAccess.md)
- [PluginPackageRecord](docs/PluginPackageRecord.md)
- [PluginRegistryAttachment](docs/PluginRegistryAttachment.md)
- [PluginRegistryAttachmentKind](docs/PluginRegistryAttachmentKind.md)
- [PluginRegistryIndex](docs/PluginRegistryIndex.md)
- [PluginRegistryMetadata](docs/PluginRegistryMetadata.md)
- [PluginRegistryPackage](docs/PluginRegistryPackage.md)
- [PluginRegistryPublishAttachment](docs/PluginRegistryPublishAttachment.md)
- [PluginRegistryPublishRequest](docs/PluginRegistryPublishRequest.md)
- [PluginRegistrySignature](docs/PluginRegistrySignature.md)
- [PluginRegistryYankRequest](docs/PluginRegistryYankRequest.md)
- [PluginSecurityStatus](docs/PluginSecurityStatus.md)
- [PluginSourceKind](docs/PluginSourceKind.md)
- [PluginTransport](docs/PluginTransport.md)
- [PrincipalDefinition](docs/PrincipalDefinition.md)
- [PrincipalType](docs/PrincipalType.md)
- [ProblemDetail](docs/ProblemDetail.md)
- [ProvisionedWebhookSubscription](docs/ProvisionedWebhookSubscription.md)
- [ReadinessResponse](docs/ReadinessResponse.md)
- [RealtimeEvent](docs/RealtimeEvent.md)
- [RealtimeEventPage](docs/RealtimeEventPage.md)
- [RealtimeFilter](docs/RealtimeFilter.md)
- [RealtimeSeverity](docs/RealtimeSeverity.md)
- [ReconciliationDisposition](docs/ReconciliationDisposition.md)
- [ReconciliationFinding](docs/ReconciliationFinding.md)
- [ReconciliationInvariant](docs/ReconciliationInvariant.md)
- [ReconciliationMode](docs/ReconciliationMode.md)
- [ReconciliationRequest](docs/ReconciliationRequest.md)
- [ReconciliationRun](docs/ReconciliationRun.md)
- [ReconciliationRunState](docs/ReconciliationRunState.md)
- [ReconciliationTargetType](docs/ReconciliationTargetType.md)
- [ReduceExecutionRequest](docs/ReduceExecutionRequest.md)
- [ReduceExecutionResponse](docs/ReduceExecutionResponse.md)
- [ResourceLifecycle](docs/ResourceLifecycle.md)
- [ResourceMetadata](docs/ResourceMetadata.md)
- [ResumeTaskRequest](docs/ResumeTaskRequest.md)
- [RevokedCredentialsResponse](docs/RevokedCredentialsResponse.md)
- [RevokedSessionsResponse](docs/RevokedSessionsResponse.md)
- [RoleBinding](docs/RoleBinding.md)
- [RoleDefinition](docs/RoleDefinition.md)
- [RotateCredentialRequest](docs/RotateCredentialRequest.md)
- [RunnerCapabilities](docs/RunnerCapabilities.md)
- [RunnerId](docs/RunnerId.md)
- [RunnerMode](docs/RunnerMode.md)
- [RunnerNetworkAccess](docs/RunnerNetworkAccess.md)
- [SchedulePreview](docs/SchedulePreview.md)
- [SearchDocument](docs/SearchDocument.md)
- [SearchDocumentType](docs/SearchDocumentType.md)
- [SearchProjectionCondition](docs/SearchProjectionCondition.md)
- [SearchProjectionStatus](docs/SearchProjectionStatus.md)
- [SearchRange](docs/SearchRange.md)
- [SearchRangeField](docs/SearchRangeField.md)
- [SearchRebuildRequest](docs/SearchRebuildRequest.md)
- [SearchRequest](docs/SearchRequest.md)
- [SearchResponse](docs/SearchResponse.md)
- [SearchSortDirection](docs/SearchSortDirection.md)
- [SearchSortField](docs/SearchSortField.md)
- [SecretBinding](docs/SecretBinding.md)
- [SecretBindingExport](docs/SecretBindingExport.md)
- [SecretBindingWrite](docs/SecretBindingWrite.md)
- [ServiceCompatibility](docs/ServiceCompatibility.md)
- [ServiceDrainRequest](docs/ServiceDrainRequest.md)
- [ServiceInstance](docs/ServiceInstance.md)
- [ServiceLiveness](docs/ServiceLiveness.md)
- [ServiceRole](docs/ServiceRole.md)
- [ServiceRoleStatus](docs/ServiceRoleStatus.md)
- [ServiceState](docs/ServiceState.md)
- [ServiceTopology](docs/ServiceTopology.md)
- [SetLocalPasswordRequest](docs/SetLocalPasswordRequest.md)
- [SourcePosition](docs/SourcePosition.md)
- [SourceRange](docs/SourceRange.md)
- [SubflowMode](docs/SubflowMode.md)
- [SubflowPropagation](docs/SubflowPropagation.md)
- [TaskArtifactRecord](docs/TaskArtifactRecord.md)
- [TaskCacheEntry](docs/TaskCacheEntry.md)
- [TaskCacheMode](docs/TaskCacheMode.md)
- [TaskCachePurgeRequest](docs/TaskCachePurgeRequest.md)
- [TaskCachePurgeResult](docs/TaskCachePurgeResult.md)
- [TaskCompletion](docs/TaskCompletion.md)
- [TaskExitMetadata](docs/TaskExitMetadata.md)
- [TaskLog](docs/TaskLog.md)
- [TaskLogRecord](docs/TaskLogRecord.md)
- [TaskMetricRecord](docs/TaskMetricRecord.md)
- [TaskRunLifecyclePhase](docs/TaskRunLifecyclePhase.md)
- [TaskRunState](docs/TaskRunState.md)
- [TenantDefinition](docs/TenantDefinition.md)
- [TenantExport](docs/TenantExport.md)
- [TenantPolicy](docs/TenantPolicy.md)
- [TenantStatus](docs/TenantStatus.md)
- [TimeRangeSelection](docs/TimeRangeSelection.md)
- [TriggerActionRequest](docs/TriggerActionRequest.md)
- [TriggerOccurrence](docs/TriggerOccurrence.md)
- [TriggerOccurrenceState](docs/TriggerOccurrenceState.md)
- [TriggerRuntimeState](docs/TriggerRuntimeState.md)
- [TrustedCircuitState](docs/TrustedCircuitState.md)
- [TrustedPluginRuntimeSnapshot](docs/TrustedPluginRuntimeSnapshot.md)
- [TrustedPluginRuntimeStatus](docs/TrustedPluginRuntimeStatus.md)
- [TrustedPluginState](docs/TrustedPluginState.md)
- [UiSessionResponse](docs/UiSessionResponse.md)
- [ValidationError](docs/ValidationError.md)
- [ValidationIssue](docs/ValidationIssue.md)
- [Value](docs/Value.md)
- [Value1](docs/Value1.md)
- [WebhookDelivery](docs/WebhookDelivery.md)
- [WebhookDeliveryAttempt](docs/WebhookDeliveryAttempt.md)
- [WebhookDeliveryHistory](docs/WebhookDeliveryHistory.md)
- [WebhookDeliveryKind](docs/WebhookDeliveryKind.md)
- [WebhookDeliveryStatus](docs/WebhookDeliveryStatus.md)
- [WebhookSubscription](docs/WebhookSubscription.md)
- [WebhookSubscriptionCreate](docs/WebhookSubscriptionCreate.md)
- [WorkerCompatibility](docs/WorkerCompatibility.md)
- [WorkerInventory](docs/WorkerInventory.md)
- [WorkerLiveness](docs/WorkerLiveness.md)
- [WorkerStatus](docs/WorkerStatus.md)
- [WorkflowMetadataPolicy](docs/WorkflowMetadataPolicy.md)

### Authorization

Endpoints do not require authorization.


## About

This TypeScript SDK client supports the [Fetch API](https://fetch.spec.whatwg.org/)
and is automatically generated by the
[OpenAPI Generator](https://openapi-generator.tech) project:

- API version: `0.2.0`
- Package version: `0.2.0`
- Generator version: `7.24.0`
- Build package: `org.openapitools.codegen.languages.TypeScriptFetchClientCodegen`

The generated npm module supports the following:

- Environments
  * Node.js
  * Webpack
  * Browserify
- Language levels
  * ES5 - you must have a Promises/A+ library installed
  * ES6
- Module systems
  * CommonJS
  * ES6 module system


## Development

### Building

To build the TypeScript source code, you need to have Node.js and npm installed.
After cloning the repository, navigate to the project directory and run:

```bash
npm install
npm run build
```

### Publishing

Once you've built the package, you can publish it to npm:

```bash
npm publish
```

## License

[]()
