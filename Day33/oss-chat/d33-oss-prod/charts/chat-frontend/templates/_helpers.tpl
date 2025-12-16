{{- define "chatFrontend.labels" -}}
app.kubernetes.io/name: chat-frontend
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
{{- end -}}

{{- define "chat-frontend.fullname" -}}
{{ .Release.Name }}
{{- end -}}

{{- define "chat-frontend.name" -}}
chat-frontend
{{- end -}}
