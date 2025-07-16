{{- define "prima-api.name" -}}
prima-api
{{- end }}

{{- define "prima-api.fullname" -}}
{{ .Release.Name }}-prima-api
{{- end }}
