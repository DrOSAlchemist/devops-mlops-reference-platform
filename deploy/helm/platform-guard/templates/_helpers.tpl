{{- define "platform-guard.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "platform-guard.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "platform-guard.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}