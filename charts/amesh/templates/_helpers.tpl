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

{{- define "amesh.runtimeEnv" -}}
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: {{ .Values.database.existingSecret | quote }}
      key: {{ .Values.database.key | quote }}
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
- name: TENANCY_MODE
  value: {{ .Values.tenancy.mode | quote }}
- name: SINGLE_TENANT_SLUG
  value: {{ .Values.tenancy.singleTenantSlug | quote }}
- name: LOG_LEVEL
  value: {{ .Values.logLevel | quote }}
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
