{{- define "ragBackend.labels" -}}
app.kubernetes.io/name: rag-backend
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version | replace "+" "_" }}
{{- end -}}

{{- define "rag-backend.fullname" -}}
{{ .Release.Name }}
{{- end -}}

{{- define "rag-backend.name" -}}
rag-backend
{{- end -}}
