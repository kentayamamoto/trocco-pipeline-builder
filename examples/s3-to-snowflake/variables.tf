# ─── TROCCO ─────────────────────────────────────────

variable "trocco_api_key" {
  description = "TROCCO API Key"
  type        = string
  sensitive   = true
}

# ─── Amazon S3 ──────────────────────────────────────
# モードA: s3_connection_id を設定 → 既存接続を参照
# モードB: s3_connection_id を null → aws_auth_type + 認証情報で新規作成

variable "s3_connection_id" {
  description = "Existing TROCCO S3 connection ID. If set, skips connection creation."
  type        = number
  default     = null
}

variable "s3_connection_name" {
  description = "Connection name in TROCCO (used only when creating new connection)"
  type        = string
  default     = "s3-auto"
}

variable "s3_aws_auth_type" {
  description = "AWS auth type: iam_user or assume_role (used only when creating new connection)"
  type        = string
  default     = "iam_user"

  validation {
    condition     = contains(["iam_user", "assume_role"], var.s3_aws_auth_type)
    error_message = "s3_aws_auth_type must be 'iam_user' or 'assume_role'."
  }
}

variable "s3_aws_access_key_id" {
  description = "AWS access key ID (used only when auth_type = iam_user)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "s3_aws_secret_access_key" {
  description = "AWS secret access key (used only when auth_type = iam_user)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "s3_aws_account_id" {
  description = "AWS account ID (used only when auth_type = assume_role)"
  type        = string
  default     = ""
}

variable "s3_aws_role_name" {
  description = "IAM role name (used only when auth_type = assume_role)"
  type        = string
  default     = ""
}

variable "s3_bucket" {
  description = "S3 bucket name"
  type        = string
}

variable "s3_path_prefix" {
  description = "S3 path prefix"
  type        = string
}

variable "s3_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-1"
}

variable "s3_default_time_zone" {
  description = "Default time zone for date/time parsing"
  type        = string
  default     = "Asia/Tokyo"
}

variable "s3_csv_delimiter" {
  description = "CSV delimiter character"
  type        = string
  default     = ","
}

variable "s3_csv_skip_header_lines" {
  description = "Number of header lines to skip in CSV"
  type        = number
  default     = 1
}

# # ─── Excel固有（excel_parser 使用時のみ有効化）───────
# variable "s3_excel_sheet_name" {
#   description = "Excel sheet name (required for excel_parser)"
#   type        = string
#   default     = "Sheet1"
# }
#
# variable "s3_excel_skip_header_lines" {
#   description = "Number of header lines to skip in Excel"
#   type        = number
#   default     = 1
# }
#
# variable "input_columns_excel" {
#   description = "Excel input column definitions (with formula_handling)"
#   type = list(object({
#     name              = string
#     type              = string
#     format            = optional(string)
#     formula_handling  = string  # "cashed_value" or "evaluate"
#   }))
#   default = []
# }

# ─── Snowflake ───────────────────────────────────────
# モードA: snowflake_connection_id を設定 → 既存接続を参照
# モードB: snowflake_connection_id を null → host/user/password or private_key で新規作成

variable "snowflake_connection_id" {
  description = "Existing TROCCO Snowflake connection ID. If set, skips connection creation."
  type        = number
  default     = null
}

variable "snowflake_connection_name" {
  description = "Connection name in TROCCO (used only when creating new connection)"
  type        = string
  default     = "snowflake-auto"
}

variable "snowflake_host" {
  description = "Snowflake host (used only when creating new connection)"
  type        = string
  default     = ""
}

variable "snowflake_user" {
  description = "Snowflake username (used only when creating new connection)"
  type        = string
  default     = ""
}

variable "snowflake_auth_method" {
  description = "Snowflake auth method: user_password or key_pair"
  type        = string
  default     = "user_password"

  validation {
    condition     = contains(["user_password", "key_pair"], var.snowflake_auth_method)
    error_message = "snowflake_auth_method must be 'user_password' or 'key_pair'."
  }
}

variable "snowflake_password" {
  description = "Snowflake password (used only when auth_method = user_password)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "snowflake_private_key" {
  description = "Snowflake private key (used only when auth_method = key_pair)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "snowflake_role" {
  description = "Snowflake role (specify the role created for TROCCO)"
  type        = string
}

variable "snowflake_warehouse" {
  description = "Snowflake warehouse name"
  type        = string
}

variable "snowflake_database" {
  description = "Snowflake database name"
  type        = string
}

variable "snowflake_schema" {
  description = "Snowflake schema name"
  type        = string
  default     = "PUBLIC"
}

variable "snowflake_table" {
  description = "Snowflake table name"
  type        = string
}

variable "snowflake_load_mode" {
  description = "Load mode (insert, insert_direct, truncate_insert, replace, merge)"
  type        = string
  default     = "replace"
}

# ─── Job Definition ──────────────────────────────────

variable "job_name" {
  description = "Transfer job name"
  type        = string
}

variable "job_description" {
  description = "Transfer job description"
  type        = string
  default     = "Auto-generated by TROCCO Pipeline Builder"
}

variable "input_columns" {
  description = "Input column definitions"
  type = list(object({
    name   = string
    type   = string
    format = optional(string)
  }))
}

variable "filter_columns" {
  description = "Filter column definitions (source → destination mapping)"
  type = list(object({
    name                = string
    src                 = string
    type                = string
    default             = optional(string, "")
    format              = optional(string)
    json_expand_enabled = optional(bool, false)
  }))
}
