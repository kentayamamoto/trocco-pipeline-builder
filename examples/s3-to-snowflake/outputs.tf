output "job_definition_id" {
  description = "Created TROCCO job definition ID"
  value       = trocco_job_definition.s3_to_snowflake.id
}

output "s3_connection_id" {
  description = "S3 connection ID (existing or newly created)"
  value       = local.s3_connection_id
}

output "snowflake_connection_id" {
  description = "Snowflake connection ID (existing or newly created)"
  value       = local.snowflake_connection_id
}

output "job_name" {
  description = "Job definition name"
  value       = trocco_job_definition.s3_to_snowflake.name
}

output "pipeline_summary" {
  description = "Pipeline summary"
  value = {
    source      = "s3 (bucket: ${var.s3_bucket}, prefix: ${var.s3_path_prefix})"
    destination = "snowflake (${var.snowflake_database}.${var.snowflake_schema}.${var.snowflake_table})"
    columns     = length(var.filter_columns)
  }
}
