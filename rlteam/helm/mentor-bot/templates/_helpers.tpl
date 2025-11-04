{{/*
Expand the name of the chart.
*/}}
{{- define "mentor-bot.name" -}}
{{- default .Chart.Name .Values.global.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "mentor-bot.fullname" -}}
{{- if .Values.global.fullnameOverride }}
{{- .Values.global.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.global.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "mentor-bot.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "mentor-bot.labels" -}}
helm.sh/chart: {{ include "mentor-bot.chart" . }}
{{ include "mentor-bot.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- with .Values.labels }}
{{ toYaml . }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "mentor-bot.selectorLabels" -}}
app.kubernetes.io/name: {{ include "mentor-bot.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "mentor-bot.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "mentor-bot.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Create the name of the configmap to use
*/}}
{{- define "mentor-bot.configMapName" -}}
{{- printf "%s-config" (include "mentor-bot.fullname" .) }}
{{- end }}

{{/*
Create the name of the secret to use
*/}}
{{- define "mentor-bot.secretName" -}}
{{- default (printf "%s-secrets" (include "mentor-bot.fullname" .)) .Values.secrets.name }}
{{- end }}

{{/*
Return the image name
*/}}
{{- define "mentor-bot.image" -}}
{{- $tag := .Values.image.tag | default .Chart.AppVersion -}}
{{- if .Values.image.repository }}
{{- printf "%s:%s" .Values.image.repository $tag }}
{{- else }}
{{- printf "mentor-bot:%s" $tag }}
{{- end }}
{{- end }}
