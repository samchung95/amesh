{{- define "amesh.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "amesh.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name (include "amesh.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{- define "amesh.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
app.kubernetes.io/name: {{ include "amesh.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "amesh.selectorLabels" -}}
app.kubernetes.io/name: {{ include "amesh.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "amesh.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "amesh.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- required "serviceAccount.name is required when serviceAccount.create=false" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "amesh.taskNamespace" -}}
{{- default .Release.Namespace .Values.taskNamespace }}
{{- end }}

{{- define "amesh.image" -}}
{{- printf "%s:%s" .Values.image.repository (.Values.image.tag | default .Chart.AppVersion) }}
{{- end }}

{{- define "amesh.enabledRolesJson" -}}
{{- $enabled := list "webserver" -}}
{{- range $role, $config := .Values.serviceRoles -}}
{{- if $config.enabled -}}
{{- $enabled = append $enabled $role -}}
{{- end -}}
{{- end -}}
{{- toJson $enabled -}}
{{- end }}

{{- define "amesh.runtimeEnv" -}}
- name: APP_ENV
  value: {{ .Values.appEnv | quote }}
- name: AUTH_MODE
  value: {{ .Values.auth.mode | quote }}
- name: AUTH_POLICY
  value: {{ .Values.auth.policy | quote }}
- name: AUTH_SESSION_IDLE_SECONDS
  value: {{ .Values.auth.sessionIdleSeconds | quote }}
- name: AUTH_SESSION_ABSOLUTE_SECONDS
  value: {{ .Values.auth.sessionAbsoluteSeconds | quote }}
- name: AUTH_SESSION_ROTATION_SECONDS
  value: {{ .Values.auth.sessionRotationSeconds | quote }}
- name: AUTH_SESSION_OVERLAP_SECONDS
  value: {{ .Values.auth.sessionOverlapSeconds | quote }}
- name: AUTH_LOGIN_RATE_LIMIT_PER_MINUTE
  value: {{ .Values.auth.loginRateLimitPerMinute | quote }}
- name: AUTH_LOGIN_MAX_FAILURES
  value: {{ .Values.auth.loginMaxFailures | quote }}
- name: AUTH_LOGIN_LOCK_SECONDS
  value: {{ .Values.auth.loginLockSeconds | quote }}
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: {{ .Values.database.existingSecret | quote }}
      key: {{ .Values.database.key | quote }}
{{- if .Values.database.readReplicaExistingSecret }}
- name: DATABASE_READ_REPLICA_URL
  valueFrom:
    secretKeyRef:
      name: {{ .Values.database.readReplicaExistingSecret | quote }}
      key: {{ .Values.database.readReplicaKey | quote }}
{{- end }}
- name: DATABASE_POOL_SIZE
  value: {{ .Values.database.poolSize | quote }}
- name: DATABASE_MAX_OVERFLOW
  value: {{ .Values.database.maxOverflow | quote }}
- name: DATABASE_POOL_TIMEOUT_SECONDS
  value: {{ .Values.database.poolTimeoutSeconds | quote }}
- name: DATABASE_POOL_RECYCLE_SECONDS
  value: {{ .Values.database.poolRecycleSeconds | quote }}
- name: DATABASE_PREPARED_STATEMENT_CACHE_SIZE
  value: {{ .Values.database.preparedStatementCacheSize | quote }}
- name: DATABASE_TLS_MODE
  value: {{ .Values.database.tlsMode | quote }}
{{- if .Values.database.tlsCAFile }}
- name: DATABASE_TLS_CA_FILE
  value: {{ .Values.database.tlsCAFile | quote }}
{{- end }}
- name: OBJECT_STORAGE_BACKEND
  value: {{ .Values.objectStorage.backend | quote }}
- name: OBJECT_STORAGE_ENDPOINT
  value: {{ .Values.objectStorage.endpoint | quote }}
- name: OBJECT_STORAGE_REGION
  value: {{ .Values.objectStorage.region | quote }}
- name: OBJECT_STORAGE_BUCKET
  value: {{ .Values.objectStorage.bucket | quote }}
- name: OBJECT_STORAGE_WORKLOAD_IDENTITY
  value: {{ .Values.objectStorage.workloadIdentity | quote }}
- name: OBJECT_STORAGE_CONSISTENCY_ATTEMPTS
  value: {{ .Values.objectStorage.consistencyAttempts | quote }}
- name: OBJECT_STORAGE_CONSISTENCY_DELAY_SECONDS
  value: {{ .Values.objectStorage.consistencyDelaySeconds | quote }}
- name: OBJECT_STORAGE_SPOOL_MEMORY_BYTES
  value: {{ .Values.objectStorage.spoolMemoryBytes | quote }}
{{- if .Values.objectStorage.encryptionKeyId }}
- name: OBJECT_STORAGE_ENCRYPTION_KEY_ID
  value: {{ .Values.objectStorage.encryptionKeyId | quote }}
{{- end }}
{{- if .Values.objectStorage.proxyURL }}
- name: OBJECT_STORAGE_PROXY_URL
  value: {{ .Values.objectStorage.proxyURL | quote }}
{{- end }}
{{- if .Values.objectStorage.caFile }}
- name: OBJECT_STORAGE_CA_FILE
  value: {{ .Values.objectStorage.caFile | quote }}
{{- end }}
{{- if .Values.objectStorage.azureAccountURL }}
- name: OBJECT_STORAGE_AZURE_ACCOUNT_URL
  value: {{ .Values.objectStorage.azureAccountURL | quote }}
{{- end }}
{{- if .Values.objectStorage.googleProject }}
- name: OBJECT_STORAGE_GCS_PROJECT
  value: {{ .Values.objectStorage.googleProject | quote }}
{{- end }}
{{- if .Values.objectStorage.googleEndpoint }}
- name: OBJECT_STORAGE_GCS_ENDPOINT
  value: {{ .Values.objectStorage.googleEndpoint | quote }}
{{- end }}
{{- if .Values.objectStorage.googleCredentialsFile }}
- name: OBJECT_STORAGE_GCS_CREDENTIALS_FILE
  value: {{ .Values.objectStorage.googleCredentialsFile | quote }}
{{- end }}
{{- if .Values.objectStorage.existingSecret }}
{{- if eq .Values.objectStorage.backend "s3" }}
- name: OBJECT_STORAGE_ACCESS_KEY
  valueFrom:
    secretKeyRef:
      name: {{ .Values.objectStorage.existingSecret | quote }}
      key: {{ .Values.objectStorage.accessKeyKey | quote }}
- name: OBJECT_STORAGE_SECRET_KEY
  valueFrom:
    secretKeyRef:
      name: {{ .Values.objectStorage.existingSecret | quote }}
      key: {{ .Values.objectStorage.secretKeyKey | quote }}
{{- else if eq .Values.objectStorage.backend "azure" }}
- name: OBJECT_STORAGE_AZURE_ACCOUNT_KEY
  valueFrom:
    secretKeyRef:
      name: {{ .Values.objectStorage.existingSecret | quote }}
      key: {{ .Values.objectStorage.azureAccountKeyKey | quote }}
{{- end }}
{{- end }}
- name: AMESH_ADMIN_TOKEN
  valueFrom:
    secretKeyRef:
      name: {{ .Values.adminToken.existingSecret | quote }}
      key: {{ .Values.adminToken.key | quote }}
- name: AMESH_TOKEN_PEPPER
  valueFrom:
    secretKeyRef:
      name: {{ .Values.tokenPepper.existingSecret | quote }}
      key: {{ .Values.tokenPepper.key | quote }}
{{- if .Values.tokenPepper.previousKey }}
- name: AMESH_PREVIOUS_TOKEN_PEPPER
  valueFrom:
    secretKeyRef:
      name: {{ .Values.tokenPepper.existingSecret | quote }}
      key: {{ .Values.tokenPepper.previousKey | quote }}
{{- end }}
- name: KUBERNETES_TASK_NAMESPACE
  value: {{ include "amesh.taskNamespace" . | quote }}
{{- with .Values.taskRunner.profiles }}
- name: KUBERNETES_RUNNER_PROFILES
  value: {{ toJson . | quote }}
{{- end }}
- name: TENANCY_MODE
  value: {{ .Values.tenancy.mode | quote }}
- name: SINGLE_TENANT_SLUG
  value: {{ .Values.tenancy.singleTenantSlug | quote }}
- name: LOG_LEVEL
  value: {{ .Values.logLevel | quote }}
- name: LOG_DESTINATION
  value: {{ .Values.observability.logDestination | quote }}
{{- with .Values.observability.logFilePath }}
- name: LOG_FILE_PATH
  value: {{ . | quote }}
{{- end }}
- name: LOG_SYSLOG_ADDRESS
  value: {{ .Values.observability.logSyslogAddress | quote }}
- name: LOG_QUEUE_CAPACITY
  value: {{ .Values.observability.logQueueCapacity | quote }}
{{- with .Values.observability.otlpEndpoint }}
- name: OTEL_EXPORTER_OTLP_ENDPOINT
  value: {{ . | quote }}
{{- end }}
{{- if .Values.observability.otlpHeadersExistingSecret }}
- name: OTEL_EXPORTER_OTLP_HEADERS
  valueFrom:
    secretKeyRef:
      name: {{ .Values.observability.otlpHeadersExistingSecret | quote }}
      key: {{ .Values.observability.otlpHeadersKey | quote }}
{{- end }}
- name: OTEL_BATCH_QUEUE_SIZE
  value: {{ .Values.observability.otlpBatchQueueSize | quote }}
- name: OTEL_BATCH_SIZE
  value: {{ .Values.observability.otlpBatchSize | quote }}
- name: OTEL_EXPORT_TIMEOUT_SECONDS
  value: {{ .Values.observability.otlpExportTimeoutSeconds | quote }}
- name: SERVICE_HEARTBEAT_SECONDS
  value: {{ .Values.serviceHeartbeatSeconds | quote }}
- name: SERVICE_STALE_AFTER_SECONDS
  value: {{ .Values.serviceStaleAfterSeconds | quote }}
- name: SERVICE_CYCLE_SECONDS
  value: {{ .Values.serviceCycleSeconds | quote }}
- name: SERVICE_ENABLED_ROLES
  value: {{ include "amesh.enabledRolesJson" . | quote }}
- name: NETWORK_TOPOLOGY
  value: {{ .Values.network.topology | quote }}
- name: NETWORK_PRIVATE_ENDPOINT
  value: {{ .Values.network.privateEndpoint | quote }}
- name: NETWORK_INBOUND_TLS_MODE
  value: {{ .Values.network.tls.mode | quote }}
- name: NETWORK_TLS_CLIENT_AUTH
  value: {{ .Values.network.tls.clientAuth | quote }}
- name: NETWORK_TLS_MINIMUM_VERSION
  value: {{ .Values.network.tls.minimumVersion | quote }}
- name: NETWORK_TLS_CIPHERS
  value: {{ .Values.network.tls.ciphers | quote }}
- name: NETWORK_TRUSTED_PROXY_RANGES
  value: {{ toJson .Values.network.trustedProxyRanges | quote }}
- name: NETWORK_NO_PROXY
  value: {{ toJson .Values.network.proxy.noProxy | quote }}
- name: NETWORK_EGRESS_ALLOWED_HOSTS
  value: {{ toJson .Values.network.egress.allowedHosts | quote }}
- name: CORE_HTTP_ALLOWED_PRIVATE_HOSTS
  value: {{ toJson .Values.network.egress.allowedPrivateHosts | quote }}
- name: NETWORK_DIAGNOSTIC_HOSTS
  value: {{ toJson .Values.network.egress.diagnosticHosts | quote }}
{{- with .Values.network.externalBaseURL }}
- name: NETWORK_EXTERNAL_BASE_URL
  value: {{ . | quote }}
{{- end }}
{{- if .Values.network.proxy.existingSecret }}
- name: NETWORK_HTTP_PROXY_URL
  valueFrom:
    secretKeyRef:
      name: {{ .Values.network.proxy.existingSecret | quote }}
      key: {{ .Values.network.proxy.httpKey | quote }}
      optional: true
- name: NETWORK_HTTPS_PROXY_URL
  valueFrom:
    secretKeyRef:
      name: {{ .Values.network.proxy.existingSecret | quote }}
      key: {{ .Values.network.proxy.httpsKey | quote }}
      optional: true
{{- else }}
{{- with .Values.network.proxy.httpURL }}
- name: NETWORK_HTTP_PROXY_URL
  value: {{ . | quote }}
{{- end }}
{{- with .Values.network.proxy.httpsURL }}
- name: NETWORK_HTTPS_PROXY_URL
  value: {{ . | quote }}
{{- end }}
{{- end }}
{{- if .Values.network.tls.existingSecret }}
{{- if eq .Values.network.tls.mode "direct" }}
- name: NETWORK_TLS_CERTIFICATE_FILE
  value: {{ printf "%s/%s" .Values.network.tls.mountPath .Values.network.tls.certificateKey | quote }}
- name: NETWORK_TLS_PRIVATE_KEY_FILE
  value: {{ printf "%s/%s" .Values.network.tls.mountPath .Values.network.tls.privateKeyKey | quote }}
{{- end }}
{{- if ne .Values.network.tls.clientAuth "none" }}
- name: NETWORK_TLS_CLIENT_CA_FILE
  value: {{ printf "%s/%s" .Values.network.tls.mountPath .Values.network.tls.clientCAKey | quote }}
{{- end }}
{{- if .Values.network.outboundTLS.useCA }}
- name: NETWORK_OUTBOUND_CA_FILE
  value: {{ printf "%s/%s" .Values.network.tls.mountPath .Values.network.outboundTLS.caKey | quote }}
{{- end }}
{{- if .Values.network.outboundTLS.useClientCertificate }}
- name: NETWORK_OUTBOUND_CLIENT_CERTIFICATE_FILE
  value: {{ printf "%s/%s" .Values.network.tls.mountPath .Values.network.outboundTLS.clientCertificateKey | quote }}
- name: NETWORK_OUTBOUND_CLIENT_KEY_FILE
  value: {{ printf "%s/%s" .Values.network.tls.mountPath .Values.network.outboundTLS.clientKeyKey | quote }}
{{- end }}
{{- end }}
- name: OPENROUTER_MODEL
  value: {{ .Values.openRouter.model | quote }}
{{- if .Values.openRouter.existingSecret }}
- name: OPENROUTER_API_KEY
  valueFrom:
    secretKeyRef:
      name: {{ .Values.openRouter.existingSecret | quote }}
      key: {{ .Values.openRouter.key | quote }}
{{- end }}
{{- end }}
