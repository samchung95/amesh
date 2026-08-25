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
*AgentsApi* | [**compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet**](docs/AgentsApi.md#compareagentdefinitionrevisionsapiv1namespacesnamespaceagentdefinitionskeycompareget) | **GET** /api/v1/namespaces/{namespace}/agent/definitions/{key}/compare | Compare Agent Definition Revisions
*AgentsApi* | [**createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost**](docs/AgentsApi.md#createagentmcpconnectionrevisionapiv1namespacesnamespaceagentmcpconnectionspost) | **POST** /api/v1/namespaces/{namespace}/agent/mcp-connections | Create Agent Mcp Connection Revision
*AgentsApi* | [**createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost**](docs/AgentsApi.md#createagentresourcerevisionapiv1namespacesnamespaceagentresourcespost) | **POST** /api/v1/namespaces/{namespace}/agent/resources | Create Agent Resource Revision
*AgentsApi* | [**deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDelete**](docs/AgentsApi.md#deleteagentmemoryentryapiv1namespacesnamespaceagentmemoryentryiddelete) | **DELETE** /api/v1/namespaces/{namespace}/agent/memory/{entry_id} | Delete Agent Memory Entry
*AgentsApi* | [**diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet**](docs/AgentsApi.md#diagnosemodelpolicymigrationapiv1namespacesnamespaceagentmodelpolicieskeymigrationget) | **GET** /api/v1/namespaces/{namespace}/agent/model-policies/{key}/migration | Diagnose Model Policy Migration
*AgentsApi* | [**discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost**](docs/AgentsApi.md#discoveragentmcpconnectionapiv1namespacesnamespaceagentmcpconnectionsdiscoverpost) | **POST** /api/v1/namespaces/{namespace}/agent/mcp-connections/discover | Discover Agent Mcp Connection
*AgentsApi* | [**getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet**](docs/AgentsApi.md#getagentmcpconnectionapiv1namespacesnamespaceagentmcpconnectionskeyget) | **GET** /api/v1/namespaces/{namespace}/agent/mcp-connections/{key} | Get Agent Mcp Connection
*AgentsApi* | [**getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet**](docs/AgentsApi.md#getagentresourceapiv1namespacesnamespaceagentresourceskindkeyget) | **GET** /api/v1/namespaces/{namespace}/agent/resources/{kind}/{key} | Get Agent Resource
*AgentsApi* | [**listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet**](docs/AgentsApi.md#listagentmcpconnectiontoolsapiv1namespacesnamespaceagentmcpconnectionskeytoolsget) | **GET** /api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/tools | List Agent Mcp Connection Tools
*AgentsApi* | [**listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet**](docs/AgentsApi.md#listagentmcpconnectionsapiv1namespacesnamespaceagentmcpconnectionsget) | **GET** /api/v1/namespaces/{namespace}/agent/mcp-connections | List Agent Mcp Connections
*AgentsApi* | [**listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGet**](docs/AgentsApi.md#listagentmemorymetadataapiv1namespacesnamespaceagentmemoryget) | **GET** /api/v1/namespaces/{namespace}/agent/memory | List Agent Memory Metadata
*AgentsApi* | [**listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet**](docs/AgentsApi.md#listagentresourcesapiv1namespacesnamespaceagentresourcesget) | **GET** /api/v1/namespaces/{namespace}/agent/resources | List Agent Resources
*AgentsApi* | [**previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGet**](docs/AgentsApi.md#previewagentdefinitionapiv1namespacesnamespaceagentdefinitionskeypreviewget) | **GET** /api/v1/namespaces/{namespace}/agent/definitions/{key}/preview | Preview Agent Definition
*AgentsApi* | [**previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGet**](docs/AgentsApi.md#previewagentevaluationfixtureapiv1namespacesnamespaceagentevaluationskeyfixturesfixturekeypreviewget) | **GET** /api/v1/namespaces/{namespace}/agent/evaluations/{key}/fixtures/{fixture_key}/preview | Preview Agent Evaluation Fixture
*AgentsApi* | [**previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPost**](docs/AgentsApi.md#previewagentmeshrouteapiv1namespacesnamespaceagentmeshroutespreviewpost) | **POST** /api/v1/namespaces/{namespace}/agent/mesh/routes/preview | Preview Agent Mesh Route
*AgentsApi* | [**resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost**](docs/AgentsApi.md#resolveagentdefinitionapiv1namespacesnamespaceagentdefinitionskeyresolvepost) | **POST** /api/v1/namespaces/{namespace}/agent/definitions/{key}/resolve | Resolve Agent Definition
*AppsApi* | [**getWorkflowAppApiV1AppsNamespaceAppIdGet**](docs/AppsApi.md#getworkflowappapiv1appsnamespaceappidget) | **GET** /api/v1/apps/{namespace}/{app_id} | Get Workflow App
*AppsApi* | [**launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost**](docs/AppsApi.md#launchworkflowappapiv1appsnamespaceappidlaunchpost) | **POST** /api/v1/apps/{namespace}/{app_id}/launch | Launch Workflow App
*AppsApi* | [**listWorkflowAppsApiV1AppsGet**](docs/AppsApi.md#listworkflowappsapiv1appsget) | **GET** /api/v1/apps | List Workflow Apps
*AppsApi* | [**upsertWorkflowAppApiV1AppsNamespaceAppIdPut**](docs/AppsApi.md#upsertworkflowappapiv1appsnamespaceappidput) | **PUT** /api/v1/apps/{namespace}/{app_id} | Upsert Workflow App
*AssetsApi* | [**declareAssetLineageApiV1AssetsLineagePost**](docs/AssetsApi.md#declareassetlineageapiv1assetslineagepost) | **POST** /api/v1/assets/lineage | Declare Asset Lineage
*AssetsApi* | [**exportAssetCatalogApiV1AssetsExportOpenlineageGet**](docs/AssetsApi.md#exportassetcatalogapiv1assetsexportopenlineageget) | **GET** /api/v1/assets/export/openlineage | Export Asset Catalog
*AssetsApi* | [**getAssetCatalogEntryApiV1AssetsAssetIdGet**](docs/AssetsApi.md#getassetcatalogentryapiv1assetsassetidget) | **GET** /api/v1/assets/{asset_id} | Get Asset Catalog Entry
*AssetsApi* | [**listAssetsApiV1AssetsGet**](docs/AssetsApi.md#listassetsapiv1assetsget) | **GET** /api/v1/assets | List Assets
*AssetsApi* | [**recordAssetObservationApiV1AssetsObservationsPost**](docs/AssetsApi.md#recordassetobservationapiv1assetsobservationspost) | **POST** /api/v1/assets/observations | Record Asset Observation
*AssetsApi* | [**registerAssetApiV1AssetsPost**](docs/AssetsApi.md#registerassetapiv1assetspost) | **POST** /api/v1/assets | Register Asset
*AuditApi* | [**createAuditLegalHoldApiV1AuditLegalHoldsPost**](docs/AuditApi.md#createauditlegalholdapiv1auditlegalholdspost) | **POST** /api/v1/audit-legal-holds | Create Audit Legal Hold
*AuditApi* | [**createComplianceEvidenceApiV1ComplianceEvidencePost**](docs/AuditApi.md#createcomplianceevidenceapiv1complianceevidencepost) | **POST** /api/v1/compliance-evidence | Create Compliance Evidence
*AuditApi* | [**createObjectAuditExportApiV1AuditExportsPost**](docs/AuditApi.md#createobjectauditexportapiv1auditexportspost) | **POST** /api/v1/audit-exports | Create Object Audit Export
*AuditApi* | [**createObjectCompliancePackageApiV1CompliancePackagesPost**](docs/AuditApi.md#createobjectcompliancepackageapiv1compliancepackagespost) | **POST** /api/v1/compliance-packages | Create Object Compliance Package
*AuditApi* | [**downloadAuditExportApiV1AuditEventsExportGet**](docs/AuditApi.md#downloadauditexportapiv1auditeventsexportget) | **GET** /api/v1/audit-events/export | Download Audit Export
*AuditApi* | [**downloadCompliancePackageApiV1CompliancePackagesExportGet**](docs/AuditApi.md#downloadcompliancepackageapiv1compliancepackagesexportget) | **GET** /api/v1/compliance-packages/export | Download Compliance Package
*AuditApi* | [**getAuditPolicyApiV1AuditPolicyGet**](docs/AuditApi.md#getauditpolicyapiv1auditpolicyget) | **GET** /api/v1/audit-policy | Get Audit Policy
*AuditApi* | [**listAuditEventsApiV1AuditEventsGet**](docs/AuditApi.md#listauditeventsapiv1auditeventsget) | **GET** /api/v1/audit-events | List Audit Events
*AuditApi* | [**listAuditLegalHoldsApiV1AuditLegalHoldsGet**](docs/AuditApi.md#listauditlegalholdsapiv1auditlegalholdsget) | **GET** /api/v1/audit-legal-holds | List Audit Legal Holds
*AuditApi* | [**listComplianceEvidenceApiV1ComplianceEvidenceGet**](docs/AuditApi.md#listcomplianceevidenceapiv1complianceevidenceget) | **GET** /api/v1/compliance-evidence | List Compliance Evidence
*AuditApi* | [**purgeAuditRetentionApiV1AuditRetentionPurgePost**](docs/AuditApi.md#purgeauditretentionapiv1auditretentionpurgepost) | **POST** /api/v1/audit-retention/purge | Purge Audit Retention
*AuditApi* | [**releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete**](docs/AuditApi.md#releaseauditlegalholdapiv1auditlegalholdsholdiddelete) | **DELETE** /api/v1/audit-legal-holds/{hold_id} | Release Audit Legal Hold
*AuditApi* | [**updateAuditPolicyApiV1AuditPolicyPut**](docs/AuditApi.md#updateauditpolicyapiv1auditpolicyput) | **PUT** /api/v1/audit-policy | Update Audit Policy
*AuditApi* | [**verifyAuditIntegrityApiV1AuditEventsIntegrityGet**](docs/AuditApi.md#verifyauditintegrityapiv1auditeventsintegrityget) | **GET** /api/v1/audit-events/integrity | Verify Audit Integrity
*AuthenticationApi* | [**beginFederatedLoginApiV1AuthFederatedProviderIdStartGet**](docs/AuthenticationApi.md#beginfederatedloginapiv1authfederatedprovideridstartget) | **GET** /api/v1/auth/federated/{provider_id}/start | Begin Federated Login
*AuthenticationApi* | [**changeLocalPasswordApiV1AuthPasswordPost**](docs/AuthenticationApi.md#changelocalpasswordapiv1authpasswordpost) | **POST** /api/v1/auth/password | Change Local Password
*AuthenticationApi* | [**completeOidcLoginApiV1AuthFederatedProviderIdCallbackGet**](docs/AuthenticationApi.md#completeoidcloginapiv1authfederatedprovideridcallbackget) | **GET** /api/v1/auth/federated/{provider_id}/callback | Complete Oidc Login
*AuthenticationApi* | [**completeSamlLoginApiV1AuthFederatedProviderIdCallbackPost**](docs/AuthenticationApi.md#completesamlloginapiv1authfederatedprovideridcallbackpost) | **POST** /api/v1/auth/federated/{provider_id}/callback | Complete Saml Login
*AuthenticationApi* | [**listAuthenticationProvidersApiV1AuthProvidersGet**](docs/AuthenticationApi.md#listauthenticationprovidersapiv1authprovidersget) | **GET** /api/v1/auth/providers | List Authentication Providers
*AuthenticationApi* | [**loginApiV1AuthLoginPost**](docs/AuthenticationApi.md#loginapiv1authloginpost) | **POST** /api/v1/auth/login | Login
*AuthenticationApi* | [**logoutAllApiV1AuthLogoutAllPost**](docs/AuthenticationApi.md#logoutallapiv1authlogoutallpost) | **POST** /api/v1/auth/logout-all | Logout All
*AuthenticationApi* | [**logoutApiV1AuthLogoutPost**](docs/AuthenticationApi.md#logoutapiv1authlogoutpost) | **POST** /api/v1/auth/logout | Logout
*AuthenticationApi* | [**revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete**](docs/AuthenticationApi.md#revokeprincipalsessionsapiv1adminprincipalsprincipalidsessionsdelete) | **DELETE** /api/v1/admin/principals/{principal_id}/sessions | Revoke Principal Sessions
*AuthenticationApi* | [**samlServiceProviderMetadataApiV1AuthFederatedProviderIdSamlMetadataGet**](docs/AuthenticationApi.md#samlserviceprovidermetadataapiv1authfederatedprovideridsamlmetadataget) | **GET** /api/v1/auth/federated/{provider_id}/saml/metadata | Saml Service Provider Metadata
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
*CompatibilityApi* | [**createKestraExecutionApiV1ExecutionsNamespaceFlowIdPost**](docs/CompatibilityApi.md#createkestraexecutionapiv1executionsnamespaceflowidpost) | **POST** /api/v1/executions/{namespace}/{flow_id} | Create Kestra Execution
*CompatibilityApi* | [**getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet**](docs/CompatibilityApi.md#getkestracompatibilitymanifestapiv1compatibilitykestramanifestget) | **GET** /api/v1/compatibility/kestra/manifest | Get Kestra Compatibility Manifest
*CompatibilityApi* | [**validateKestraFlowApiV1MainFlowsValidatePost**](docs/CompatibilityApi.md#validatekestraflowapiv1mainflowsvalidatepost) | **POST** /api/v1/main/flows/validate | Validate Kestra Flow
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
*ExecutionsApi* | [**getExecutionEvidenceBundleApiV1ExecutionsExecutionIdEvidenceBundleGet**](docs/ExecutionsApi.md#getexecutionevidencebundleapiv1executionsexecutionidevidencebundleget) | **GET** /api/v1/executions/{execution_id}/evidence-bundle | Get Execution Evidence Bundle
*ExecutionsApi* | [**getExecutionGraphApiV1ExecutionsExecutionIdGraphGet**](docs/ExecutionsApi.md#getexecutiongraphapiv1executionsexecutionidgraphget) | **GET** /api/v1/executions/{execution_id}/graph | Get Execution Graph
*ExecutionsApi* | [**getExecutionLogsApiV1ExecutionsExecutionIdLogsGet**](docs/ExecutionsApi.md#getexecutionlogsapiv1executionsexecutionidlogsget) | **GET** /api/v1/executions/{execution_id}/logs | Get Execution Logs
*ExecutionsApi* | [**getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet**](docs/ExecutionsApi.md#getexecutionparentsubflowapiv1executionsexecutionidparentsubflowget) | **GET** /api/v1/executions/{execution_id}/parent-subflow | Get Execution Parent Subflow
*ExecutionsApi* | [**getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet**](docs/ExecutionsApi.md#gettaskadmissionapiv1taskrunstaskrunidadmissionget) | **GET** /api/v1/task-runs/{task_run_id}/admission | Get Task Admission
*ExecutionsApi* | [**listExecutionAgentSessionsApiV1ExecutionsExecutionIdAgentSessionsGet**](docs/ExecutionsApi.md#listexecutionagentsessionsapiv1executionsexecutionidagentsessionsget) | **GET** /api/v1/executions/{execution_id}/agent-sessions | List Execution Agent Sessions
*ExecutionsApi* | [**listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet**](docs/ExecutionsApi.md#listexecutioncontrolhistoryapiv1executionsexecutionidinterventionsget) | **GET** /api/v1/executions/{execution_id}/interventions | List Execution Control History
*ExecutionsApi* | [**listExecutionFilesApiV1ExecutionsExecutionIdFilesGet**](docs/ExecutionsApi.md#listexecutionfilesapiv1executionsexecutionidfilesget) | **GET** /api/v1/executions/{execution_id}/files | List Execution Files
*ExecutionsApi* | [**listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet**](docs/ExecutionsApi.md#listexecutionsubflowsapiv1executionsexecutionidsubflowsget) | **GET** /api/v1/executions/{execution_id}/subflows | List Execution Subflows
*ExecutionsApi* | [**listExecutionsApiV1ExecutionsGet**](docs/ExecutionsApi.md#listexecutionsapiv1executionsget) | **GET** /api/v1/executions | List Executions
*ExecutionsApi* | [**previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost**](docs/ExecutionsApi.md#previewexecutioncontrolapiv1executionsexecutionidinterventionspreviewpost) | **POST** /api/v1/executions/{execution_id}/interventions/preview | Preview Execution Control
*ExecutionsApi* | [**reduceExecutionEventsApiV1ExecutionsReducePost**](docs/ExecutionsApi.md#reduceexecutioneventsapiv1executionsreducepost) | **POST** /api/v1/executions/reduce | Reduce Execution Events
*ExecutionsApi* | [**resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost**](docs/ExecutionsApi.md#resumetaskrunapiv1executionsexecutionidtaskrunstaskrunidresumepost) | **POST** /api/v1/executions/{execution_id}/task-runs/{task_run_id}/resume | Resume Task Run
*ExecutionsApi* | [**streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet**](docs/ExecutionsApi.md#streamexecutionevidenceapiv1executionsexecutionidevidencestreamget) | **GET** /api/v1/executions/{execution_id}/evidence/stream | Stream Execution Evidence
*ExecutionsApi* | [**streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet**](docs/ExecutionsApi.md#streamexecutionlogsapiv1executionsexecutionidlogsstreamget) | **GET** /api/v1/executions/{execution_id}/logs/stream | Stream Execution Logs
*ExternalOrchestrationApi* | [**getExternalOrchestrationProfileApiV1OrchestrationProfileGet**](docs/ExternalOrchestrationApi.md#getexternalorchestrationprofileapiv1orchestrationprofileget) | **GET** /api/v1/orchestration/profile | Get External Orchestration Profile
*FlowTestsApi* | [**deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete**](docs/FlowTestsApi.md#deleteflowtestapiv1flowsnamespaceflowidteststestiddelete) | **DELETE** /api/v1/flows/{namespace}/{flow_id}/tests/{test_id} | Delete Flow Test
*FlowTestsApi* | [**getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet**](docs/FlowTestsApi.md#getflowtestgateapiv1namespacesnamespaceflowtestgateget) | **GET** /api/v1/namespaces/{namespace}/flow-test-gate | Get Flow Test Gate
*FlowTestsApi* | [**listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet**](docs/FlowTestsApi.md#listflowtestrunsapiv1flowsnamespaceflowidtestsrunsget) | **GET** /api/v1/flows/{namespace}/{flow_id}/tests/runs | List Flow Test Runs
*FlowTestsApi* | [**listFlowTestsApiV1FlowsNamespaceFlowIdTestsGet**](docs/FlowTestsApi.md#listflowtestsapiv1flowsnamespaceflowidtestsget) | **GET** /api/v1/flows/{namespace}/{flow_id}/tests | List Flow Tests
*FlowTestsApi* | [**runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost**](docs/FlowTestsApi.md#runflowtestsapiv1flowsnamespaceflowidtestsrunspost) | **POST** /api/v1/flows/{namespace}/{flow_id}/tests/runs | Run Flow Tests
*FlowTestsApi* | [**saveFlowTestApiV1FlowsNamespaceFlowIdTestsPut**](docs/FlowTestsApi.md#saveflowtestapiv1flowsnamespaceflowidtestsput) | **PUT** /api/v1/flows/{namespace}/{flow_id}/tests | Save Flow Test
*FlowTestsApi* | [**updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut**](docs/FlowTestsApi.md#updateflowtestgateapiv1namespacesnamespaceflowtestgateput) | **PUT** /api/v1/namespaces/{namespace}/flow-test-gate | Update Flow Test Gate
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
*HumanTasksApi* | [**actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost**](docs/HumanTasksApi.md#actonhumantaskapiv1humantaskshumantaskidactionspost) | **POST** /api/v1/human-tasks/{human_task_id}/actions | Act On Human Task
*HumanTasksApi* | [**listHumanTaskNotificationsApiV1HumanTaskNotificationsGet**](docs/HumanTasksApi.md#listhumantasknotificationsapiv1humantasknotificationsget) | **GET** /api/v1/human-task-notifications | List Human Task Notifications
*HumanTasksApi* | [**listHumanTasksApiV1HumanTasksGet**](docs/HumanTasksApi.md#listhumantasksapiv1humantasksget) | **GET** /api/v1/human-tasks | List Human Tasks
*LifecycleApi* | [**createLifecycleLegalHoldApiV1LifecycleLegalHoldsPost**](docs/LifecycleApi.md#createlifecyclelegalholdapiv1lifecyclelegalholdspost) | **POST** /api/v1/lifecycle/legal-holds | Create Lifecycle Legal Hold
*LifecycleApi* | [**createLifecyclePolicyApiV1LifecyclePoliciesPost**](docs/LifecycleApi.md#createlifecyclepolicyapiv1lifecyclepoliciespost) | **POST** /api/v1/lifecycle/policies | Create Lifecycle Policy
*LifecycleApi* | [**executeLifecycleJobApiV1LifecycleJobsJobIdExecutePost**](docs/LifecycleApi.md#executelifecyclejobapiv1lifecyclejobsjobidexecutepost) | **POST** /api/v1/lifecycle/jobs/{job_id}/execute | Execute Lifecycle Job
*LifecycleApi* | [**getLifecycleJobApiV1LifecycleJobsJobIdGet**](docs/LifecycleApi.md#getlifecyclejobapiv1lifecyclejobsjobidget) | **GET** /api/v1/lifecycle/jobs/{job_id} | Get Lifecycle Job
*LifecycleApi* | [**listLifecycleJobsApiV1LifecycleJobsGet**](docs/LifecycleApi.md#listlifecyclejobsapiv1lifecyclejobsget) | **GET** /api/v1/lifecycle/jobs | List Lifecycle Jobs
*LifecycleApi* | [**listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet**](docs/LifecycleApi.md#listlifecyclelegalholdsapiv1lifecyclelegalholdsget) | **GET** /api/v1/lifecycle/legal-holds | List Lifecycle Legal Holds
*LifecycleApi* | [**listLifecyclePoliciesApiV1LifecyclePoliciesGet**](docs/LifecycleApi.md#listlifecyclepoliciesapiv1lifecyclepoliciesget) | **GET** /api/v1/lifecycle/policies | List Lifecycle Policies
*LifecycleApi* | [**previewLifecyclePurgeApiV1LifecyclePreviewsPost**](docs/LifecycleApi.md#previewlifecyclepurgeapiv1lifecyclepreviewspost) | **POST** /api/v1/lifecycle/previews | Preview Lifecycle Purge
*LifecycleApi* | [**releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost**](docs/LifecycleApi.md#releaselifecyclelegalholdapiv1lifecyclelegalholdsholdidreleasepost) | **POST** /api/v1/lifecycle/legal-holds/{hold_id}/release | Release Lifecycle Legal Hold
*LifecycleApi* | [**resumeLifecycleJobApiV1LifecycleJobsJobIdResumePost**](docs/LifecycleApi.md#resumelifecyclejobapiv1lifecyclejobsjobidresumepost) | **POST** /api/v1/lifecycle/jobs/{job_id}/resume | Resume Lifecycle Job
*LifecycleApi* | [**updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut**](docs/LifecycleApi.md#updatelifecyclepolicyapiv1lifecyclepoliciespolicyidput) | **PUT** /api/v1/lifecycle/policies/{policy_id} | Update Lifecycle Policy
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
*OperationsApi* | [**activateOperationalControlApiV1OperationalControlsPost**](docs/OperationsApi.md#activateoperationalcontrolapiv1operationalcontrolspost) | **POST** /api/v1/operational-controls | Activate Operational Control
*OperationsApi* | [**changeOperationalControlApiV1OperationalControlsControlIdActionsPost**](docs/OperationsApi.md#changeoperationalcontrolapiv1operationalcontrolscontrolidactionspost) | **POST** /api/v1/operational-controls/{control_id}/actions | Change Operational Control
*OperationsApi* | [**deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDelete**](docs/OperationsApi.md#deactivateannouncementapiv1announcementsannouncementiddelete) | **DELETE** /api/v1/announcements/{announcement_id} | Deactivate Announcement
*OperationsApi* | [**drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost**](docs/OperationsApi.md#drainserviceinstanceapiv1operationsservicesinstanceiddrainpost) | **POST** /api/v1/operations/services/{instance_id}/drain | Drain Service Instance
*OperationsApi* | [**getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet**](docs/OperationsApi.md#getadmissiondiagnosticsapiv1admissionsdiagnosticsget) | **GET** /api/v1/admissions/diagnostics | Get Admission Diagnostics
*OperationsApi* | [**getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGet**](docs/OperationsApi.md#getnetworkdiagnosticsapiv1operationsnetworkdiagnosticsget) | **GET** /api/v1/operations/network-diagnostics | Get Network Diagnostics
*OperationsApi* | [**getReconciliationApiV1ReconciliationsRunIdGet**](docs/OperationsApi.md#getreconciliationapiv1reconciliationsrunidget) | **GET** /api/v1/reconciliations/{run_id} | Get Reconciliation
*OperationsApi* | [**getServiceTopologyApiV1OperationsTopologyGet**](docs/OperationsApi.md#getservicetopologyapiv1operationstopologyget) | **GET** /api/v1/operations/topology | Get Service Topology
*OperationsApi* | [**listAnnouncementsApiV1AnnouncementsGet**](docs/OperationsApi.md#listannouncementsapiv1announcementsget) | **GET** /api/v1/announcements | List Announcements
*OperationsApi* | [**listOperationalControlEventsApiV1OperationalControlEventsGet**](docs/OperationsApi.md#listoperationalcontroleventsapiv1operationalcontroleventsget) | **GET** /api/v1/operational-control-events | List Operational Control Events
*OperationsApi* | [**listOperationalControlsApiV1OperationalControlsGet**](docs/OperationsApi.md#listoperationalcontrolsapiv1operationalcontrolsget) | **GET** /api/v1/operational-controls | List Operational Controls
*OperationsApi* | [**listReconciliationsApiV1ReconciliationsGet**](docs/OperationsApi.md#listreconciliationsapiv1reconciliationsget) | **GET** /api/v1/reconciliations | List Reconciliations
*OperationsApi* | [**publishAnnouncementApiV1AnnouncementsPost**](docs/OperationsApi.md#publishannouncementapiv1announcementspost) | **POST** /api/v1/announcements | Publish Announcement
*OperationsApi* | [**reconcileAdmissionsApiV1AdmissionsReconcilePost**](docs/OperationsApi.md#reconcileadmissionsapiv1admissionsreconcilepost) | **POST** /api/v1/admissions/reconcile | Reconcile Admissions
*OperationsApi* | [**runReconciliationApiV1ReconciliationsPost**](docs/OperationsApi.md#runreconciliationapiv1reconciliationspost) | **POST** /api/v1/reconciliations | Run Reconciliation
*PluginsApi* | [**createPluginPolicyRuleApiV1PluginPolicyRulesPost**](docs/PluginsApi.md#createpluginpolicyruleapiv1pluginpolicyrulespost) | **POST** /api/v1/plugin-policy/rules | Create Plugin Policy Rule
*PluginsApi* | [**deletePluginPolicyRuleApiV1PluginPolicyRulesRuleIdDelete**](docs/PluginsApi.md#deletepluginpolicyruleapiv1pluginpolicyrulesruleiddelete) | **DELETE** /api/v1/plugin-policy/rules/{rule_id} | Delete Plugin Policy Rule
*PluginsApi* | [**downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet**](docs/PluginsApi.md#downloadpluginregistrybundleapiv1pluginregistryblobsdigestget) | **GET** /api/v1/plugin-registry/blobs/{digest} | Download Plugin Registry Bundle
*PluginsApi* | [**evaluateFlowPluginPolicyApiV1PluginPolicyEvaluatePost**](docs/PluginsApi.md#evaluateflowpluginpolicyapiv1pluginpolicyevaluatepost) | **POST** /api/v1/plugin-policy/evaluate | Evaluate Flow Plugin Policy
*PluginsApi* | [**exportPluginRegistryApiV1PluginRegistryOfflineExportGet**](docs/PluginsApi.md#exportpluginregistryapiv1pluginregistryofflineexportget) | **GET** /api/v1/plugin-registry/offline-export | Export Plugin Registry
*PluginsApi* | [**getEffectivePluginPolicyApiV1PluginPolicyEffectiveGet**](docs/PluginsApi.md#geteffectivepluginpolicyapiv1pluginpolicyeffectiveget) | **GET** /api/v1/plugin-policy/effective | Get Effective Plugin Policy
*PluginsApi* | [**getPluginPolicyRuleApiV1PluginPolicyRulesRuleIdGet**](docs/PluginsApi.md#getpluginpolicyruleapiv1pluginpolicyrulesruleidget) | **GET** /api/v1/plugin-policy/rules/{rule_id} | Get Plugin Policy Rule
*PluginsApi* | [**getPluginRegistryIndexApiV1PluginRegistryIndexGet**](docs/PluginsApi.md#getpluginregistryindexapiv1pluginregistryindexget) | **GET** /api/v1/plugin-registry/index | Get Plugin Registry Index
*PluginsApi* | [**getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet**](docs/PluginsApi.md#getpluginregistrypackageapiv1pluginregistrypackagesnameversionget) | **GET** /api/v1/plugin-registry/packages/{name}/{version} | Get Plugin Registry Package
*PluginsApi* | [**importPluginRegistryApiV1PluginRegistryOfflineImportPost**](docs/PluginsApi.md#importpluginregistryapiv1pluginregistryofflineimportpost) | **POST** /api/v1/plugin-registry/offline-import | Import Plugin Registry
*PluginsApi* | [**installPluginBundleApiV1PluginsInstallPost**](docs/PluginsApi.md#installpluginbundleapiv1pluginsinstallpost) | **POST** /api/v1/plugins/install | Install Plugin Bundle
*PluginsApi* | [**isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet**](docs/PluginsApi.md#isolatedpluginruntimestatusapiv1pluginsisolatedruntimeget) | **GET** /api/v1/plugins/isolated-runtime | Isolated Plugin Runtime Status
*PluginsApi* | [**listPluginPolicyDecisionsApiV1PluginPolicyDecisionsGet**](docs/PluginsApi.md#listpluginpolicydecisionsapiv1pluginpolicydecisionsget) | **GET** /api/v1/plugin-policy/decisions | List Plugin Policy Decisions
*PluginsApi* | [**listPluginsApiV1PluginsGet**](docs/PluginsApi.md#listpluginsapiv1pluginsget) | **GET** /api/v1/plugins | List Plugins
*PluginsApi* | [**previewPluginQuarantineApiV1PluginPolicyQuarantinesPreviewPost**](docs/PluginsApi.md#previewpluginquarantineapiv1pluginpolicyquarantinespreviewpost) | **POST** /api/v1/plugin-policy/quarantines/preview | Preview Plugin Quarantine
*PluginsApi* | [**publishPluginRegistryPackageApiV1PluginRegistryPackagesPost**](docs/PluginsApi.md#publishpluginregistrypackageapiv1pluginregistrypackagespost) | **POST** /api/v1/plugin-registry/packages | Publish Plugin Registry Package
*PluginsApi* | [**quarantinePluginVersionApiV1PluginPolicyQuarantinesPost**](docs/PluginsApi.md#quarantinepluginversionapiv1pluginpolicyquarantinespost) | **POST** /api/v1/plugin-policy/quarantines | Quarantine Plugin Version
*PluginsApi* | [**refreshPluginsApiV1PluginsRefreshPost**](docs/PluginsApi.md#refreshpluginsapiv1pluginsrefreshpost) | **POST** /api/v1/plugins/refresh | Refresh Plugins
*PluginsApi* | [**releasePluginQuarantineApiV1PluginPolicyQuarantinesQuarantineIdReleasePost**](docs/PluginsApi.md#releasepluginquarantineapiv1pluginpolicyquarantinesquarantineidreleasepost) | **POST** /api/v1/plugin-policy/quarantines/{quarantine_id}/release | Release Plugin Quarantine
*PluginsApi* | [**trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet**](docs/PluginsApi.md#trustedpluginruntimestatusapiv1pluginstrustedruntimeget) | **GET** /api/v1/plugins/trusted-runtime | Trusted Plugin Runtime Status
*PluginsApi* | [**updatePluginPolicyRuleApiV1PluginPolicyRulesRuleIdPut**](docs/PluginsApi.md#updatepluginpolicyruleapiv1pluginpolicyrulesruleidput) | **PUT** /api/v1/plugin-policy/rules/{rule_id} | Update Plugin Policy Rule
*PluginsApi* | [**yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost**](docs/PluginsApi.md#yankpluginregistrypackageapiv1pluginregistrypackagesnameversionyankpost) | **POST** /api/v1/plugin-registry/packages/{name}/{version}/yank | Yank Plugin Registry Package
*PoliciesApi* | [**createAdmissionPolicyApiV1PoliciesPost**](docs/PoliciesApi.md#createadmissionpolicyapiv1policiespost) | **POST** /api/v1/policies | Create Admission Policy
*PoliciesApi* | [**evaluateAdmissionPoliciesApiV1PoliciesEvaluatePost**](docs/PoliciesApi.md#evaluateadmissionpoliciesapiv1policiesevaluatepost) | **POST** /api/v1/policies/evaluate | Evaluate Admission Policies
*PoliciesApi* | [**getAdmissionPolicyApiV1PoliciesPolicyKeyGet**](docs/PoliciesApi.md#getadmissionpolicyapiv1policiespolicykeyget) | **GET** /api/v1/policies/{policy_key} | Get Admission Policy
*PoliciesApi* | [**listAdmissionPoliciesApiV1PoliciesGet**](docs/PoliciesApi.md#listadmissionpoliciesapiv1policiesget) | **GET** /api/v1/policies | List Admission Policies
*PoliciesApi* | [**listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet**](docs/PoliciesApi.md#listadmissionpolicydecisionsapiv1policiesdecisionsget) | **GET** /api/v1/policies/decisions | List Admission Policy Decisions
*PoliciesApi* | [**testAdmissionPolicyApiV1PoliciesPolicyKeyTestPost**](docs/PoliciesApi.md#testadmissionpolicyapiv1policiespolicykeytestpost) | **POST** /api/v1/policies/{policy_key}/test | Test Admission Policy
*PoliciesApi* | [**updateAdmissionPolicyApiV1PoliciesPolicyKeyPut**](docs/PoliciesApi.md#updateadmissionpolicyapiv1policiespolicykeyput) | **PUT** /api/v1/policies/{policy_key} | Update Admission Policy
*PoliciesApi* | [**validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost**](docs/PoliciesApi.md#validateflowadmissionpolicyapiv1policiesflowsvalidatepost) | **POST** /api/v1/policies/flows/validate | Validate Flow Admission Policy
*QualityApi* | [**getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet**](docs/QualityApi.md#getdifferentialapiv1namespacesnamespacedifferentialsidempotencykeyget) | **GET** /api/v1/namespaces/{namespace}/differentials/{idempotency_key} | Get Differential
*QualityApi* | [**runDifferentialApiV1NamespacesNamespaceDifferentialsPost**](docs/QualityApi.md#rundifferentialapiv1namespacesnamespacedifferentialspost) | **POST** /api/v1/namespaces/{namespace}/differentials | Run Differential
*RealtimeApi* | [**createWebhookSubscriptionApiV1WebhookSubscriptionsPost**](docs/RealtimeApi.md#createwebhooksubscriptionapiv1webhooksubscriptionspost) | **POST** /api/v1/webhook-subscriptions | Create Webhook Subscription
*RealtimeApi* | [**listRealtimeEventsApiV1RealtimeEventsGet**](docs/RealtimeApi.md#listrealtimeeventsapiv1realtimeeventsget) | **GET** /api/v1/realtime/events | List Realtime Events
*RealtimeApi* | [**listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet**](docs/RealtimeApi.md#listwebhookdeliveryhistoryapiv1webhooksubscriptionssubscriptioniddeliveriesget) | **GET** /api/v1/webhook-subscriptions/{subscription_id}/deliveries | List Webhook Delivery History
*RealtimeApi* | [**listWebhookSubscriptionsApiV1WebhookSubscriptionsGet**](docs/RealtimeApi.md#listwebhooksubscriptionsapiv1webhooksubscriptionsget) | **GET** /api/v1/webhook-subscriptions | List Webhook Subscriptions
*RealtimeApi* | [**replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost**](docs/RealtimeApi.md#replaywebhookdeliveryapiv1webhookdeliveriesdeliveryidreplaypost) | **POST** /api/v1/webhook-deliveries/{delivery_id}/replay | Replay Webhook Delivery
*RealtimeApi* | [**rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost**](docs/RealtimeApi.md#rotatewebhooksubscriptionsecretapiv1webhooksubscriptionssubscriptionidrotatesecretpost) | **POST** /api/v1/webhook-subscriptions/{subscription_id}/rotate-secret | Rotate Webhook Subscription Secret
*RealtimeApi* | [**streamRealtimeEventsApiV1RealtimeStreamGet**](docs/RealtimeApi.md#streamrealtimeeventsapiv1realtimestreamget) | **GET** /api/v1/realtime/stream | Stream Realtime Events
*RealtimeApi* | [**testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost**](docs/RealtimeApi.md#testwebhooksubscriptionapiv1webhooksubscriptionssubscriptionidtestpost) | **POST** /api/v1/webhook-subscriptions/{subscription_id}/test | Test Webhook Subscription
*ReleasesApi* | [**applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost**](docs/ReleasesApi.md#applypolicyapiv1releasespoliciespolicyidapplypost) | **POST** /api/v1/releases/policies/{policy_id}/apply | Apply Policy
*ReleasesApi* | [**createPolicyApiV1ReleasesPoliciesPost**](docs/ReleasesApi.md#createpolicyapiv1releasespoliciespost) | **POST** /api/v1/releases/policies | Create Policy
*ReleasesApi* | [**killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost**](docs/ReleasesApi.md#killswitchapiv1releasestargetkindtargetkeykillswitchpost) | **POST** /api/v1/releases/{target_kind}/{target_key}/kill-switch | Kill Switch
*ReleasesApi* | [**previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost**](docs/ReleasesApi.md#previewpolicyapiv1releasespoliciespolicyidpreviewpost) | **POST** /api/v1/releases/policies/{policy_id}/preview | Preview Policy
*ReleasesApi* | [**recordEvidenceApiV1ReleasesEvidencePost**](docs/ReleasesApi.md#recordevidenceapiv1releasesevidencepost) | **POST** /api/v1/releases/evidence | Record Evidence
*ReleasesApi* | [**rollbackApiV1ReleasesTargetKindTargetKeyRollbackPost**](docs/ReleasesApi.md#rollbackapiv1releasestargetkindtargetkeyrollbackpost) | **POST** /api/v1/releases/{target_kind}/{target_key}/rollback | Rollback
*ReleasesApi* | [**targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet**](docs/ReleasesApi.md#targethistoryapiv1releasestargetkindtargetkeyhistoryget) | **GET** /api/v1/releases/{target_kind}/{target_key}/history | Target History
*ReleasesApi* | [**targetStateApiV1ReleasesTargetKindTargetKeyGet**](docs/ReleasesApi.md#targetstateapiv1releasestargetkindtargetkeyget) | **GET** /api/v1/releases/{target_kind}/{target_key} | Target State
*ScimApi* | [**createScimGroupScimV2GroupsPost**](docs/ScimApi.md#createscimgroupscimv2groupspost) | **POST** /scim/v2/Groups | Create Scim Group
*ScimApi* | [**createScimUserScimV2UsersPost**](docs/ScimApi.md#createscimuserscimv2userspost) | **POST** /scim/v2/Users | Create Scim User
*ScimApi* | [**deleteScimGroupScimV2GroupsGroupIdDelete**](docs/ScimApi.md#deletescimgroupscimv2groupsgroupiddelete) | **DELETE** /scim/v2/Groups/{group_id} | Delete Scim Group
*ScimApi* | [**deleteScimUserScimV2UsersUserIdDelete**](docs/ScimApi.md#deletescimuserscimv2usersuseriddelete) | **DELETE** /scim/v2/Users/{user_id} | Delete Scim User
*ScimApi* | [**getScimGroupScimV2GroupsGroupIdGet**](docs/ScimApi.md#getscimgroupscimv2groupsgroupidget) | **GET** /scim/v2/Groups/{group_id} | Get Scim Group
*ScimApi* | [**getScimUserScimV2UsersUserIdGet**](docs/ScimApi.md#getscimuserscimv2usersuseridget) | **GET** /scim/v2/Users/{user_id} | Get Scim User
*ScimApi* | [**listScimGroupsScimV2GroupsGet**](docs/ScimApi.md#listscimgroupsscimv2groupsget) | **GET** /scim/v2/Groups | List Scim Groups
*ScimApi* | [**listScimUsersScimV2UsersGet**](docs/ScimApi.md#listscimusersscimv2usersget) | **GET** /scim/v2/Users | List Scim Users
*ScimApi* | [**patchScimGroupScimV2GroupsGroupIdPatch**](docs/ScimApi.md#patchscimgroupscimv2groupsgroupidpatch) | **PATCH** /scim/v2/Groups/{group_id} | Patch Scim Group
*ScimApi* | [**patchScimUserScimV2UsersUserIdPatch**](docs/ScimApi.md#patchscimuserscimv2usersuseridpatch) | **PATCH** /scim/v2/Users/{user_id} | Patch Scim User
*ScimApi* | [**scimServiceProviderConfigScimV2ServiceProviderConfigGet**](docs/ScimApi.md#scimserviceproviderconfigscimv2serviceproviderconfigget) | **GET** /scim/v2/ServiceProviderConfig | Scim Service Provider Config
*SearchApi* | [**controlSearchProjectionApiV1SearchControlPost**](docs/SearchApi.md#controlsearchprojectionapiv1searchcontrolpost) | **POST** /api/v1/search/control | Control Search Projection
*SearchApi* | [**getSearchStatusApiV1SearchStatusGet**](docs/SearchApi.md#getsearchstatusapiv1searchstatusget) | **GET** /api/v1/search/status | Get Search Status
*SearchApi* | [**rebuildSearchProjectionApiV1SearchRebuildPost**](docs/SearchApi.md#rebuildsearchprojectionapiv1searchrebuildpost) | **POST** /api/v1/search/rebuild | Rebuild Search Projection
*SearchApi* | [**searchResourcesApiV1SearchPost**](docs/SearchApi.md#searchresourcesapiv1searchpost) | **POST** /api/v1/search | Search Resources
*SearchApi* | [**verifySearchProjectionApiV1SearchVerifyGet**](docs/SearchApi.md#verifysearchprojectionapiv1searchverifyget) | **GET** /api/v1/search/verify | Verify Search Projection
*SimulationsApi* | [**compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost**](docs/SimulationsApi.md#compareflowsimulationsapiv1flowsnamespaceflowidsimulationscomparepost) | **POST** /api/v1/flows/{namespace}/{flow_id}/simulations/compare | Compare Flow Simulations
*SimulationsApi* | [**simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost**](docs/SimulationsApi.md#simulateflowrevisionapiv1flowsnamespaceflowidrevisionsrevisionsimulatepost) | **POST** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/simulate | Simulate Flow Revision
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
*UpgradesApi* | [**getUpgradePolicyApiV1UpgradesPolicyGet**](docs/UpgradesApi.md#getupgradepolicyapiv1upgradespolicyget) | **GET** /api/v1/upgrades/policy | Get Upgrade Policy
*UpgradesApi* | [**migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost**](docs/UpgradesApi.md#migrateupgradeconfigurationapiv1upgradesconfigurationmigratepost) | **POST** /api/v1/upgrades/configuration/migrate | Migrate Upgrade Configuration
*UpgradesApi* | [**previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet**](docs/UpgradesApi.md#previewupgradeeventupcastapiv1upgradeseventsupcastget) | **GET** /api/v1/upgrades/events/upcast | Preview Upgrade Event Upcast
*UpgradesApi* | [**runUpgradeEventUpcastApiV1UpgradesEventsUpcastPost**](docs/UpgradesApi.md#runupgradeeventupcastapiv1upgradeseventsupcastpost) | **POST** /api/v1/upgrades/events/upcast | Run Upgrade Event Upcast
*UpgradesApi* | [**runUpgradePostflightApiV1UpgradesPostflightPost**](docs/UpgradesApi.md#runupgradepostflightapiv1upgradespostflightpost) | **POST** /api/v1/upgrades/postflight | Run Upgrade Postflight
*UpgradesApi* | [**runUpgradePreflightApiV1UpgradesPreflightPost**](docs/UpgradesApi.md#runupgradepreflightapiv1upgradespreflightpost) | **POST** /api/v1/upgrades/preflight | Run Upgrade Preflight
*WorkersApi* | [**drainWorkerApiV1WorkersWorkerIdDrainPost**](docs/WorkersApi.md#drainworkerapiv1workersworkeriddrainpost) | **POST** /api/v1/workers/{worker_id}/drain | Drain Worker
*WorkersApi* | [**listRunnerCapabilitiesApiV1RunnersCapabilitiesGet**](docs/WorkersApi.md#listrunnercapabilitiesapiv1runnerscapabilitiesget) | **GET** /api/v1/runners/capabilities | List Runner Capabilities
*WorkersApi* | [**listWorkersApiV1WorkersGet**](docs/WorkersApi.md#listworkersapiv1workersget) | **GET** /api/v1/workers | List Workers


### Models

- [Absolute](docs/Absolute.md)
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
- [AgentCapabilityPin](docs/AgentCapabilityPin.md)
- [AgentDefinitionSpecInput](docs/AgentDefinitionSpecInput.md)
- [AgentDefinitionSpecOutput](docs/AgentDefinitionSpecOutput.md)
- [AgentDeterministicEvaluation](docs/AgentDeterministicEvaluation.md)
- [AgentEnvelopePreview](docs/AgentEnvelopePreview.md)
- [AgentEvaluationCheck](docs/AgentEvaluationCheck.md)
- [AgentEvaluationFixture](docs/AgentEvaluationFixture.md)
- [AgentEvaluationPolicy](docs/AgentEvaluationPolicy.md)
- [AgentEvaluationPreview](docs/AgentEvaluationPreview.md)
- [AgentEvaluationSpecInput](docs/AgentEvaluationSpecInput.md)
- [AgentEvaluationSpecOutput](docs/AgentEvaluationSpecOutput.md)
- [AgentHardLimitsInput](docs/AgentHardLimitsInput.md)
- [AgentHardLimitsOutput](docs/AgentHardLimitsOutput.md)
- [AgentJudgePolicyInput](docs/AgentJudgePolicyInput.md)
- [AgentJudgePolicyOutput](docs/AgentJudgePolicyOutput.md)
- [AgentMemoryMetadata](docs/AgentMemoryMetadata.md)
- [AgentMemoryPolicy](docs/AgentMemoryPolicy.md)
- [AgentMemoryScope](docs/AgentMemoryScope.md)
- [AgentModelContinuationRef](docs/AgentModelContinuationRef.md)
- [AgentPermissions](docs/AgentPermissions.md)
- [AgentResolutionRequest](docs/AgentResolutionRequest.md)
- [AgentResourceKind](docs/AgentResourceKind.md)
- [AgentResourceRef](docs/AgentResourceRef.md)
- [AgentResourceRevision](docs/AgentResourceRevision.md)
- [AgentRevisionComparison](docs/AgentRevisionComparison.md)
- [AgentRouteAssessment](docs/AgentRouteAssessment.md)
- [AgentRouteAvailabilitySignal](docs/AgentRouteAvailabilitySignal.md)
- [AgentRouteCandidate](docs/AgentRouteCandidate.md)
- [AgentRouteDecision](docs/AgentRouteDecision.md)
- [AgentRouteEvaluationSignal](docs/AgentRouteEvaluationSignal.md)
- [AgentRoutePolicySignal](docs/AgentRoutePolicySignal.md)
- [AgentRouteRequest](docs/AgentRouteRequest.md)
- [AgentRubricCriterionInput](docs/AgentRubricCriterionInput.md)
- [AgentRubricCriterionOutput](docs/AgentRubricCriterionOutput.md)
- [AgentSessionCheckpoint](docs/AgentSessionCheckpoint.md)
- [AgentSessionCounters](docs/AgentSessionCounters.md)
- [AgentSessionPhase](docs/AgentSessionPhase.md)
- [AgentSessionRecord](docs/AgentSessionRecord.md)
- [AgentSessionState](docs/AgentSessionState.md)
- [AgentToolRef](docs/AgentToolRef.md)
- [Announcement](docs/Announcement.md)
- [AnnouncementAudience](docs/AnnouncementAudience.md)
- [AnnouncementCreateRequest](docs/AnnouncementCreateRequest.md)
- [AnnouncementSeverity](docs/AnnouncementSeverity.md)
- [AppForm](docs/AppForm.md)
- [ApprovalRequirement](docs/ApprovalRequirement.md)
- [AssetAccessMode](docs/AssetAccessMode.md)
- [AssetCatalogEntry](docs/AssetCatalogEntry.md)
- [AssetCatalogExport](docs/AssetCatalogExport.md)
- [AssetHealth](docs/AssetHealth.md)
- [AssetLineageDeclaration](docs/AssetLineageDeclaration.md)
- [AssetLineageEdge](docs/AssetLineageEdge.md)
- [AssetMetadata](docs/AssetMetadata.md)
- [AssetObservation](docs/AssetObservation.md)
- [AssetObservationCreate](docs/AssetObservationCreate.md)
- [AssetRegistrationSource](docs/AssetRegistrationSource.md)
- [AuditArtifactKind](docs/AuditArtifactKind.md)
- [AuditEvent](docs/AuditEvent.md)
- [AuditEventPage](docs/AuditEventPage.md)
- [AuditExportDestination](docs/AuditExportDestination.md)
- [AuditExportFormat](docs/AuditExportFormat.md)
- [AuditExportReceipt](docs/AuditExportReceipt.md)
- [AuditExportRequest](docs/AuditExportRequest.md)
- [AuditIntegrityReport](docs/AuditIntegrityReport.md)
- [AuditLegalHold](docs/AuditLegalHold.md)
- [AuditLegalHoldCreate](docs/AuditLegalHoldCreate.md)
- [AuditRetentionPolicy](docs/AuditRetentionPolicy.md)
- [AuditRetentionPolicyUpdate](docs/AuditRetentionPolicyUpdate.md)
- [AuditRetentionResult](docs/AuditRetentionResult.md)
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
- [BudgetRequirementInput](docs/BudgetRequirementInput.md)
- [BudgetRequirementOutput](docs/BudgetRequirementOutput.md)
- [BulkExecutionItemResult](docs/BulkExecutionItemResult.md)
- [BulkExecutionRequest](docs/BulkExecutionRequest.md)
- [CertificateDiagnostic](docs/CertificateDiagnostic.md)
- [ChangeLocalPasswordRequest](docs/ChangeLocalPasswordRequest.md)
- [CheckActionDefinition](docs/CheckActionDefinition.md)
- [CheckComplianceSummary](docs/CheckComplianceSummary.md)
- [CheckDefinition](docs/CheckDefinition.md)
- [CheckEvaluation](docs/CheckEvaluation.md)
- [CheckEvaluationPoint](docs/CheckEvaluationPoint.md)
- [CheckOutcome](docs/CheckOutcome.md)
- [CheckPolicySource](docs/CheckPolicySource.md)
- [CheckPolicyUpsertRequest](docs/CheckPolicyUpsertRequest.md)
- [ComparisonCategory](docs/ComparisonCategory.md)
- [ComparisonDifference](docs/ComparisonDifference.md)
- [ComparisonPolicy](docs/ComparisonPolicy.md)
- [ComparisonReport](docs/ComparisonReport.md)
- [CompatibilityMapping](docs/CompatibilityMapping.md)
- [ComplianceEvidenceCategory](docs/ComplianceEvidenceCategory.md)
- [ComplianceEvidenceCreate](docs/ComplianceEvidenceCreate.md)
- [ComplianceEvidenceRecord](docs/ComplianceEvidenceRecord.md)
- [CompliancePackageRequest](docs/CompliancePackageRequest.md)
- [ConfigurationDiagnosticBundle](docs/ConfigurationDiagnosticBundle.md)
- [ConfigurationEntry](docs/ConfigurationEntry.md)
- [ConfigurationMigration](docs/ConfigurationMigration.md)
- [ConfigurationMigrationKind](docs/ConfigurationMigrationKind.md)
- [ConfigurationMigrationRequest](docs/ConfigurationMigrationRequest.md)
- [ConfigurationPin](docs/ConfigurationPin.md)
- [ConfigurationSnapshot](docs/ConfigurationSnapshot.md)
- [ConnectionDiagnostic](docs/ConnectionDiagnostic.md)
- [Correlationid](docs/Correlationid.md)
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
- [DeterminismEnvelope](docs/DeterminismEnvelope.md)
- [DeterminismNode](docs/DeterminismNode.md)
- [DeterminismPolicyPin](docs/DeterminismPolicyPin.md)
- [DifferentialSpec](docs/DifferentialSpec.md)
- [DnsDiagnostic](docs/DnsDiagnostic.md)
- [DynamicExecutionBound](docs/DynamicExecutionBound.md)
- [EffectiveCapabilityEnvelope](docs/EffectiveCapabilityEnvelope.md)
- [EffectivePluginPolicy](docs/EffectivePluginPolicy.md)
- [EvidenceArtifact](docs/EvidenceArtifact.md)
- [EvidenceBundlePageResponse](docs/EvidenceBundlePageResponse.md)
- [EvidencePresence](docs/EvidencePresence.md)
- [EvidenceRecord](docs/EvidenceRecord.md)
- [EvidenceRequirement](docs/EvidenceRequirement.md)
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
- [ExternalOperation](docs/ExternalOperation.md)
- [ExternalOrchestrationProfile](docs/ExternalOrchestrationProfile.md)
- [FailoverStatus](docs/FailoverStatus.md)
- [FailureCategory](docs/FailureCategory.md)
- [FeatureFlag](docs/FeatureFlag.md)
- [FeatureFlagDecision](docs/FeatureFlagDecision.md)
- [FeatureFlagScope](docs/FeatureFlagScope.md)
- [FeatureFlagUpsertRequest](docs/FeatureFlagUpsertRequest.md)
- [FixtureSource](docs/FixtureSource.md)
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
- [FlowTestAssertion](docs/FlowTestAssertion.md)
- [FlowTestCaseResult](docs/FlowTestCaseResult.md)
- [FlowTestCoverage](docs/FlowTestCoverage.md)
- [FlowTestDefinition](docs/FlowTestDefinition.md)
- [FlowTestDefinitionCreateRequest](docs/FlowTestDefinitionCreateRequest.md)
- [FlowTestExpectation](docs/FlowTestExpectation.md)
- [FlowTestFixture](docs/FlowTestFixture.md)
- [FlowTestFixtureSource](docs/FlowTestFixtureSource.md)
- [FlowTestOutcome](docs/FlowTestOutcome.md)
- [FlowTestQualityGate](docs/FlowTestQualityGate.md)
- [FlowTestQualityGateUpdate](docs/FlowTestQualityGateUpdate.md)
- [FlowTestRunRequest](docs/FlowTestRunRequest.md)
- [FlowTestRunResult](docs/FlowTestRunResult.md)
- [FlowTestTaskState](docs/FlowTestTaskState.md)
- [FlowValidationResult](docs/FlowValidationResult.md)
- [FormField](docs/FormField.md)
- [FormSection](docs/FormSection.md)
- [Gte](docs/Gte.md)
- [HTTPValidationError](docs/HTTPValidationError.md)
- [HealthRequirementInput](docs/HealthRequirementInput.md)
- [HealthRequirementOutput](docs/HealthRequirementOutput.md)
- [HealthResponse](docs/HealthResponse.md)
- [HumanTask](docs/HumanTask.md)
- [HumanTaskAction](docs/HumanTaskAction.md)
- [HumanTaskActionKind](docs/HumanTaskActionKind.md)
- [HumanTaskActionRequest](docs/HumanTaskActionRequest.md)
- [HumanTaskNotification](docs/HumanTaskNotification.md)
- [HumanTaskState](docs/HumanTaskState.md)
- [InstructionFragment](docs/InstructionFragment.md)
- [IsolatedPluginRuntimeSnapshot](docs/IsolatedPluginRuntimeSnapshot.md)
- [IsolatedPluginRuntimeStatus](docs/IsolatedPluginRuntimeStatus.md)
- [IsolatedPluginState](docs/IsolatedPluginState.md)
- [IssueCredentialRequest](docs/IssueCredentialRequest.md)
- [IssuedCredentialResponse](docs/IssuedCredentialResponse.md)
- [KestraExecutionRequest](docs/KestraExecutionRequest.md)
- [KestraFlowImport](docs/KestraFlowImport.md)
- [KeyValueChange](docs/KeyValueChange.md)
- [KeyValueEntry](docs/KeyValueEntry.md)
- [KeyValueExport](docs/KeyValueExport.md)
- [KeyValueType](docs/KeyValueType.md)
- [KeyValueWrite](docs/KeyValueWrite.md)
- [LabelNormalization](docs/LabelNormalization.md)
- [LifecycleExecuteRequest](docs/LifecycleExecuteRequest.md)
- [LifecycleJob](docs/LifecycleJob.md)
- [LifecycleJobState](docs/LifecycleJobState.md)
- [LifecycleLegalHold](docs/LifecycleLegalHold.md)
- [LifecycleLegalHoldDraft](docs/LifecycleLegalHoldDraft.md)
- [LifecyclePolicy](docs/LifecyclePolicy.md)
- [LifecyclePolicyDraft](docs/LifecyclePolicyDraft.md)
- [LifecyclePreviewRequest](docs/LifecyclePreviewRequest.md)
- [LifecycleResourceType](docs/LifecycleResourceType.md)
- [LifecycleScope](docs/LifecycleScope.md)
- [LifecycleTrigger](docs/LifecycleTrigger.md)
- [Lineage](docs/Lineage.md)
- [LineageEvidenceKind](docs/LineageEvidenceKind.md)
- [LocationInner](docs/LocationInner.md)
- [LogLevel](docs/LogLevel.md)
- [LogSourceStream](docs/LogSourceStream.md)
- [LoginRequest](docs/LoginRequest.md)
- [LoginResponse](docs/LoginResponse.md)
- [Lte](docs/Lte.md)
- [MappingDisposition](docs/MappingDisposition.md)
- [Maxcostusd](docs/Maxcostusd.md)
- [Maximum](docs/Maximum.md)
- [Maximum1](docs/Maximum1.md)
- [Maximumuncertainty](docs/Maximumuncertainty.md)
- [McpConnectionDiscoveryRequest](docs/McpConnectionDiscoveryRequest.md)
- [McpConnectionRevision](docs/McpConnectionRevision.md)
- [McpConnectionSpec](docs/McpConnectionSpec.md)
- [McpDiscoveryResult](docs/McpDiscoveryResult.md)
- [McpToolImpact](docs/McpToolImpact.md)
- [McpToolPin](docs/McpToolPin.md)
- [MetricKind](docs/MetricKind.md)
- [MigrationPatch](docs/MigrationPatch.md)
- [Minimum](docs/Minimum.md)
- [Minimumrubricscore](docs/Minimumrubricscore.md)
- [Minimumscore](docs/Minimumscore.md)
- [ModelFallbackMode](docs/ModelFallbackMode.md)
- [ModelPolicySpec](docs/ModelPolicySpec.md)
- [ModelProviderSpec](docs/ModelProviderSpec.md)
- [ModelRoute](docs/ModelRoute.md)
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
- [NetworkDiagnosticBundle](docs/NetworkDiagnosticBundle.md)
- [NondeterministicOperation](docs/NondeterministicOperation.md)
- [OperationalBoundary](docs/OperationalBoundary.md)
- [OperationalControl](docs/OperationalControl.md)
- [OperationalControlAcknowledgement](docs/OperationalControlAcknowledgement.md)
- [OperationalControlActionKind](docs/OperationalControlActionKind.md)
- [OperationalControlActionRequest](docs/OperationalControlActionRequest.md)
- [OperationalControlCreateRequest](docs/OperationalControlCreateRequest.md)
- [OperationalControlEvent](docs/OperationalControlEvent.md)
- [OperationalControlKind](docs/OperationalControlKind.md)
- [OperationalControlScope](docs/OperationalControlScope.md)
- [OperationalControlState](docs/OperationalControlState.md)
- [OrderedPromptRef](docs/OrderedPromptRef.md)
- [Permission](docs/Permission.md)
- [PermissionAction](docs/PermissionAction.md)
- [PermissionEffect](docs/PermissionEffect.md)
- [PersistedAsset](docs/PersistedAsset.md)
- [PersistedEventMigration](docs/PersistedEventMigration.md)
- [PersistedEventMigrationRequest](docs/PersistedEventMigrationRequest.md)
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
- [PluginPolicyDecision](docs/PluginPolicyDecision.md)
- [PluginPolicyEffect](docs/PluginPolicyEffect.md)
- [PluginPolicyImpactPreview](docs/PluginPolicyImpactPreview.md)
- [PluginPolicyRule](docs/PluginPolicyRule.md)
- [PluginPolicyRuleCreate](docs/PluginPolicyRuleCreate.md)
- [PluginPolicyRuleSource](docs/PluginPolicyRuleSource.md)
- [PluginPolicyScope](docs/PluginPolicyScope.md)
- [PluginPolicySelector](docs/PluginPolicySelector.md)
- [PluginPolicyStage](docs/PluginPolicyStage.md)
- [PluginPolicySubject](docs/PluginPolicySubject.md)
- [PluginPolicySubjectDecision](docs/PluginPolicySubjectDecision.md)
- [PluginQuarantine](docs/PluginQuarantine.md)
- [PluginQuarantineCreate](docs/PluginQuarantineCreate.md)
- [PluginQuarantineState](docs/PluginQuarantineState.md)
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
- [PolicyActorContext](docs/PolicyActorContext.md)
- [PolicyCondition](docs/PolicyCondition.md)
- [PolicyConditionEvidence](docs/PolicyConditionEvidence.md)
- [PolicyCriticality](docs/PolicyCriticality.md)
- [PolicyDecision](docs/PolicyDecision.md)
- [PolicyDocument](docs/PolicyDocument.md)
- [PolicyEvaluationRequest](docs/PolicyEvaluationRequest.md)
- [PolicyFixture](docs/PolicyFixture.md)
- [PolicyFixtureResult](docs/PolicyFixtureResult.md)
- [PolicyFlowContext](docs/PolicyFlowContext.md)
- [PolicyImageContext](docs/PolicyImageContext.md)
- [PolicyInput](docs/PolicyInput.md)
- [PolicyMutation](docs/PolicyMutation.md)
- [PolicyNamespaceContext](docs/PolicyNamespaceContext.md)
- [PolicyNetworkContext](docs/PolicyNetworkContext.md)
- [PolicyOperator](docs/PolicyOperator.md)
- [PolicyOutcome](docs/PolicyOutcome.md)
- [PolicyPin](docs/PolicyPin.md)
- [PolicyPluginContext](docs/PolicyPluginContext.md)
- [PolicyResourceContext](docs/PolicyResourceContext.md)
- [PolicyRevision](docs/PolicyRevision.md)
- [PolicyRule](docs/PolicyRule.md)
- [PolicyRuleEvidence](docs/PolicyRuleEvidence.md)
- [PolicyRunnerContext](docs/PolicyRunnerContext.md)
- [PolicyScope](docs/PolicyScope.md)
- [PolicySecretContext](docs/PolicySecretContext.md)
- [PolicyStage](docs/PolicyStage.md)
- [PolicyTenantContext](docs/PolicyTenantContext.md)
- [PrincipalDefinition](docs/PrincipalDefinition.md)
- [PrincipalType](docs/PrincipalType.md)
- [ProblemDetail](docs/ProblemDetail.md)
- [Projectedcostusd](docs/Projectedcostusd.md)
- [PromotionApplyRequest](docs/PromotionApplyRequest.md)
- [PromotionEvidenceKind](docs/PromotionEvidenceKind.md)
- [PromotionKillSwitchRequest](docs/PromotionKillSwitchRequest.md)
- [PromotionPolicyInput](docs/PromotionPolicyInput.md)
- [PromotionPolicyOutput](docs/PromotionPolicyOutput.md)
- [PromotionPreviewRequest](docs/PromotionPreviewRequest.md)
- [PromotionRollbackRequest](docs/PromotionRollbackRequest.md)
- [PromotionTargetKind](docs/PromotionTargetKind.md)
- [PromptSpec](docs/PromptSpec.md)
- [ProviderMigrationDiagnostic](docs/ProviderMigrationDiagnostic.md)
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
- [Recordid](docs/Recordid.md)
- [ReduceExecutionRequest](docs/ReduceExecutionRequest.md)
- [ReduceExecutionResponse](docs/ReduceExecutionResponse.md)
- [Relative](docs/Relative.md)
- [ResolvedAgentEvaluation](docs/ResolvedAgentEvaluation.md)
- [ResolvedResourcePin](docs/ResolvedResourcePin.md)
- [ResolvedToolPin](docs/ResolvedToolPin.md)
- [ResourceLifecycle](docs/ResourceLifecycle.md)
- [ResourceMetadata](docs/ResourceMetadata.md)
- [ResourcesInner](docs/ResourcesInner.md)
- [ResumeTaskRequest](docs/ResumeTaskRequest.md)
- [RevokedCredentialsResponse](docs/RevokedCredentialsResponse.md)
- [RevokedSessionsResponse](docs/RevokedSessionsResponse.md)
- [RoleBinding](docs/RoleBinding.md)
- [RoleDefinition](docs/RoleDefinition.md)
- [RollingUpgradeStep](docs/RollingUpgradeStep.md)
- [RotateCredentialRequest](docs/RotateCredentialRequest.md)
- [RunObservation](docs/RunObservation.md)
- [RunnerCapabilities](docs/RunnerCapabilities.md)
- [RunnerId](docs/RunnerId.md)
- [RunnerMode](docs/RunnerMode.md)
- [RunnerNetworkAccess](docs/RunnerNetworkAccess.md)
- [RunningWorkPolicy](docs/RunningWorkPolicy.md)
- [SchedulePreview](docs/SchedulePreview.md)
- [ScimGroupRequest](docs/ScimGroupRequest.md)
- [ScimGroupResource](docs/ScimGroupResource.md)
- [ScimListResponse](docs/ScimListResponse.md)
- [ScimMember](docs/ScimMember.md)
- [ScimPatchOperation](docs/ScimPatchOperation.md)
- [ScimPatchRequest](docs/ScimPatchRequest.md)
- [ScimResourceMeta](docs/ScimResourceMeta.md)
- [ScimUserRequest](docs/ScimUserRequest.md)
- [ScimUserResource](docs/ScimUserResource.md)
- [Score](docs/Score.md)
- [SearchDocument](docs/SearchDocument.md)
- [SearchDocumentType](docs/SearchDocumentType.md)
- [SearchProjectionCondition](docs/SearchProjectionCondition.md)
- [SearchProjectionControlRequest](docs/SearchProjectionControlRequest.md)
- [SearchProjectionStatus](docs/SearchProjectionStatus.md)
- [SearchProjectionVerification](docs/SearchProjectionVerification.md)
- [SearchProjectionVerificationItem](docs/SearchProjectionVerificationItem.md)
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
- [ShadowEffect](docs/ShadowEffect.md)
- [ShadowFixture](docs/ShadowFixture.md)
- [ShadowRun](docs/ShadowRun.md)
- [SimulatedTaskResult](docs/SimulatedTaskResult.md)
- [SimulationComparison](docs/SimulationComparison.md)
- [SimulationEstimateModel](docs/SimulationEstimateModel.md)
- [SimulationEstimates](docs/SimulationEstimates.md)
- [SimulationEvidence](docs/SimulationEvidence.md)
- [SimulationFixture](docs/SimulationFixture.md)
- [SimulationFixtureSource](docs/SimulationFixtureSource.md)
- [SimulationPlan](docs/SimulationPlan.md)
- [SimulationPlanDiff](docs/SimulationPlanDiff.md)
- [SimulationPolicyDecision](docs/SimulationPolicyDecision.md)
- [SimulationRequest](docs/SimulationRequest.md)
- [SimulationSubstitution](docs/SimulationSubstitution.md)
- [SimulationTaskPlan](docs/SimulationTaskPlan.md)
- [SimulationTaskState](docs/SimulationTaskState.md)
- [SimulationUnknown](docs/SimulationUnknown.md)
- [SkillSpec](docs/SkillSpec.md)
- [SourcePosition](docs/SourcePosition.md)
- [SourceRange](docs/SourceRange.md)
- [Spec](docs/Spec.md)
- [Spec1](docs/Spec1.md)
- [SubflowMode](docs/SubflowMode.md)
- [SubflowPropagation](docs/SubflowPropagation.md)
- [TaskArtifactRecord](docs/TaskArtifactRecord.md)
- [TaskAssetRecord](docs/TaskAssetRecord.md)
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
- [Tolerance](docs/Tolerance.md)
- [ToolProviderKind](docs/ToolProviderKind.md)
- [TriggerActionRequest](docs/TriggerActionRequest.md)
- [TriggerOccurrence](docs/TriggerOccurrence.md)
- [TriggerOccurrenceState](docs/TriggerOccurrenceState.md)
- [TriggerRuntimeState](docs/TriggerRuntimeState.md)
- [TrustedCircuitState](docs/TrustedCircuitState.md)
- [TrustedPluginRuntimeSnapshot](docs/TrustedPluginRuntimeSnapshot.md)
- [TrustedPluginRuntimeStatus](docs/TrustedPluginRuntimeStatus.md)
- [TrustedPluginState](docs/TrustedPluginState.md)
- [UiSessionResponse](docs/UiSessionResponse.md)
- [UpgradeCapacityThresholds](docs/UpgradeCapacityThresholds.md)
- [UpgradeCheck](docs/UpgradeCheck.md)
- [UpgradeCheckStatus](docs/UpgradeCheckStatus.md)
- [UpgradePath](docs/UpgradePath.md)
- [UpgradePhase](docs/UpgradePhase.md)
- [UpgradePolicy](docs/UpgradePolicy.md)
- [UpgradeRelease](docs/UpgradeRelease.md)
- [UpgradeReport](docs/UpgradeReport.md)
- [UpgradeReportRequest](docs/UpgradeReportRequest.md)
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
- [Weight](docs/Weight.md)
- [WorkerCompatibility](docs/WorkerCompatibility.md)
- [WorkerInventory](docs/WorkerInventory.md)
- [WorkerLiveness](docs/WorkerLiveness.md)
- [WorkerStatus](docs/WorkerStatus.md)
- [WorkflowApp](docs/WorkflowApp.md)
- [WorkflowAppLaunchRequest](docs/WorkflowAppLaunchRequest.md)
- [WorkflowAppUpsertRequest](docs/WorkflowAppUpsertRequest.md)
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
