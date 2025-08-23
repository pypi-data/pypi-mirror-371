"""MCP server for BigQuery dry-run operations."""

import asyncio
import json
import logging
import os
import re
from typing import Any

import mcp.server.stdio
import mcp.types as types
from google.cloud import bigquery
from google.cloud.exceptions import BadRequest
from mcp.server import NotificationOptions, Server

from . import __version__
from .bigquery_client import get_bigquery_client
from .info_schema import analyze_query_performance, query_info_schema
from .schema_explorer import describe_table, get_table_info, list_datasets, list_tables
from .sql_analyzer import SQLAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.environ.get("DEBUG") else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

server = Server("mcp-bigquery")


def extract_error_location(error_message: str) -> dict[str, int] | None:
    """
    Extract line and column from BigQuery error message.

    Looks for patterns like [3:15] in the error message.

    Args:
        error_message: The error message from BigQuery

    Returns:
        Dict with 'line' and 'column' if found, None otherwise
    """
    match = re.search(r"\[(\d+):(\d+)\]", error_message)
    if match:
        return {"line": int(match.group(1)), "column": int(match.group(2))}
    return None


def build_query_parameters(params: dict[str, Any] | None) -> list[bigquery.ScalarQueryParameter]:
    """
    Build BigQuery query parameters from a dictionary.

    Initial implementation treats all values as STRING type.

    Args:
        params: Dictionary of parameter names to values

    Returns:
        List of ScalarQueryParameter objects
    """
    if not params:
        return []

    return [
        bigquery.ScalarQueryParameter(name, "STRING", str(value)) for name, value in params.items()
    ]


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    logger.debug("Listing available tools")
    """List available MCP tools."""
    return [
        types.Tool(
            name="bq_validate_sql",
            description=("Validate BigQuery SQL syntax without executing the query"),
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL query to validate",
                    },
                    "params": {
                        "type": "object",
                        "description": ("Optional query parameters (key-value pairs)"),
                        "additionalProperties": True,
                    },
                },
                "required": ["sql"],
            },
        ),
        types.Tool(
            name="bq_dry_run_sql",
            description=(
                "Perform a dry-run of a BigQuery SQL query to get cost " "estimates and metadata"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL query to dry-run",
                    },
                    "params": {
                        "type": "object",
                        "description": ("Optional query parameters (key-value pairs)"),
                        "additionalProperties": True,
                    },
                    "pricePerTiB": {
                        "type": "number",
                        "description": (
                            "Price per TiB for cost estimation " "(defaults to env var or 5.0)"
                        ),
                    },
                },
                "required": ["sql"],
            },
        ),
        types.Tool(
            name="bq_analyze_query_structure",
            description=("Analyze BigQuery SQL query structure and complexity"),
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL query to analyze",
                    },
                    "params": {
                        "type": "object",
                        "description": ("Optional query parameters (key-value pairs)"),
                        "additionalProperties": True,
                    },
                },
                "required": ["sql"],
            },
        ),
        types.Tool(
            name="bq_extract_dependencies",
            description=("Extract table and column dependencies from BigQuery SQL"),
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL query to analyze",
                    },
                    "params": {
                        "type": "object",
                        "description": ("Optional query parameters (key-value pairs)"),
                        "additionalProperties": True,
                    },
                },
                "required": ["sql"],
            },
        ),
        types.Tool(
            name="bq_validate_query_syntax",
            description=("Enhanced syntax validation with detailed error reporting"),
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL query to validate",
                    },
                    "params": {
                        "type": "object",
                        "description": ("Optional query parameters (key-value pairs)"),
                        "additionalProperties": True,
                    },
                },
                "required": ["sql"],
            },
        ),
        types.Tool(
            name="bq_list_datasets",
            description=("List all datasets in the BigQuery project"),
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "GCP project ID (uses default if not provided)",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of datasets to return",
                    },
                },
            },
        ),
        types.Tool(
            name="bq_list_tables",
            description=("List all tables in a BigQuery dataset with metadata"),
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_id": {
                        "type": "string",
                        "description": "The dataset ID",
                    },
                    "project_id": {
                        "type": "string",
                        "description": "GCP project ID (uses default if not provided)",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of tables to return",
                    },
                    "table_type_filter": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by table types (TABLE, VIEW, EXTERNAL, MATERIALIZED_VIEW)",
                    },
                },
                "required": ["dataset_id"],
            },
        ),
        types.Tool(
            name="bq_describe_table",
            description=("Get table schema, metadata, and statistics"),
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The table ID",
                    },
                    "dataset_id": {
                        "type": "string",
                        "description": "The dataset ID",
                    },
                    "project_id": {
                        "type": "string",
                        "description": "GCP project ID (uses default if not provided)",
                    },
                    "format_output": {
                        "type": "boolean",
                        "description": "Whether to format schema as table string",
                    },
                },
                "required": ["table_id", "dataset_id"],
            },
        ),
        types.Tool(
            name="bq_get_table_info",
            description=(
                "Get comprehensive table information including partitioning and clustering"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "The table ID",
                    },
                    "dataset_id": {
                        "type": "string",
                        "description": "The dataset ID",
                    },
                    "project_id": {
                        "type": "string",
                        "description": "GCP project ID (uses default if not provided)",
                    },
                },
                "required": ["table_id", "dataset_id"],
            },
        ),
        types.Tool(
            name="bq_query_info_schema",
            description=("Query INFORMATION_SCHEMA views for metadata"),
            inputSchema={
                "type": "object",
                "properties": {
                    "query_type": {
                        "type": "string",
                        "description": "Type of query (tables, columns, table_storage, partitions, views, routines, custom)",
                    },
                    "dataset_id": {
                        "type": "string",
                        "description": "The dataset to query metadata for",
                    },
                    "project_id": {
                        "type": "string",
                        "description": "GCP project ID (uses default if not provided)",
                    },
                    "table_filter": {
                        "type": "string",
                        "description": "Optional table name filter",
                    },
                    "custom_query": {
                        "type": "string",
                        "description": "Custom INFORMATION_SCHEMA query (when query_type is 'custom')",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 100)",
                    },
                },
                "required": ["query_type", "dataset_id"],
            },
        ),
        types.Tool(
            name="bq_analyze_query_performance",
            description=("Analyze query performance and provide optimization suggestions"),
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "The SQL query to analyze",
                    },
                    "project_id": {
                        "type": "string",
                        "description": "GCP project ID (uses default if not provided)",
                    },
                },
                "required": ["sql"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution requests."""
    logger.info(f"Executing tool: {name}")
    logger.debug(f"Tool arguments: {arguments}")

    if name == "bq_validate_sql":
        result = await validate_sql(sql=arguments["sql"], params=arguments.get("params"))
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "bq_dry_run_sql":
        result = await dry_run_sql(
            sql=arguments["sql"],
            params=arguments.get("params"),
            price_per_tib=arguments.get("pricePerTiB"),
        )
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "bq_analyze_query_structure":
        result = await analyze_query_structure(sql=arguments["sql"], params=arguments.get("params"))
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "bq_extract_dependencies":
        result = await extract_dependencies(sql=arguments["sql"], params=arguments.get("params"))
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "bq_validate_query_syntax":
        result = await validate_query_syntax(sql=arguments["sql"], params=arguments.get("params"))
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "bq_list_datasets":
        result = await list_datasets(
            project_id=arguments.get("project_id"), max_results=arguments.get("max_results")
        )
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "bq_list_tables":
        result = await list_tables(
            dataset_id=arguments["dataset_id"],
            project_id=arguments.get("project_id"),
            max_results=arguments.get("max_results"),
            table_type_filter=arguments.get("table_type_filter"),
        )
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "bq_describe_table":
        result = await describe_table(
            table_id=arguments["table_id"],
            dataset_id=arguments["dataset_id"],
            project_id=arguments.get("project_id"),
            format_output=arguments.get("format_output", False),
        )
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "bq_get_table_info":
        result = await get_table_info(
            table_id=arguments["table_id"],
            dataset_id=arguments["dataset_id"],
            project_id=arguments.get("project_id"),
        )
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "bq_query_info_schema":
        result = await query_info_schema(
            query_type=arguments["query_type"],
            dataset_id=arguments["dataset_id"],
            project_id=arguments.get("project_id"),
            table_filter=arguments.get("table_filter"),
            custom_query=arguments.get("custom_query"),
            limit=arguments.get("limit", 100),
        )
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "bq_analyze_query_performance":
        result = await analyze_query_performance(
            sql=arguments["sql"], project_id=arguments.get("project_id")
        )
        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def validate_sql(sql: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Validate BigQuery SQL syntax using dry-run.

    Args:
        sql: The SQL query to validate
        params: Optional query parameters

    Returns:
        Dict with 'isValid' boolean and optional 'error' details
    """
    logger.debug(
        f"Validating SQL query: {sql[:100]}..."
        if len(sql) > 100
        else f"Validating SQL query: {sql}"
    )
    try:
        client = get_bigquery_client()

        job_config = bigquery.QueryJobConfig(
            dry_run=True,
            use_query_cache=False,
            query_parameters=build_query_parameters(params),
        )

        client.query(sql, job_config=job_config)

        logger.info("SQL validation successful")
        return {"isValid": True}

    except BadRequest as e:
        error_msg = str(e)
        logger.warning(f"SQL validation failed: {error_msg}")
        error_result = {
            "isValid": False,
            "error": {"code": "INVALID_SQL", "message": error_msg},
        }

        location = extract_error_location(error_msg)
        if location:
            error_result["error"]["location"] = location

        if hasattr(e, "errors") and e.errors:
            error_result["error"]["details"] = e.errors

        return error_result

    except Exception as e:
        return {
            "isValid": False,
            "error": {"code": "UNKNOWN_ERROR", "message": str(e)},
        }


async def dry_run_sql(
    sql: str,
    params: dict[str, Any] | None = None,
    price_per_tib: float | None = None,
) -> dict[str, Any]:
    """
    Perform a dry-run of a BigQuery SQL query.

    Args:
        sql: The SQL query to dry-run
        params: Optional query parameters
        price_per_tib: Price per TiB for cost estimation

    Returns:
        Dict with totalBytesProcessed, usdEstimate, referencedTables,
        and schemaPreview
        or error details if the query is invalid
    """
    try:
        client = get_bigquery_client()

        job_config = bigquery.QueryJobConfig(
            dry_run=True,
            use_query_cache=False,
            query_parameters=build_query_parameters(params),
        )

        query_job = client.query(sql, job_config=job_config)

        # Get price per TiB (precedence: arg > env > default)
        if price_per_tib is None:
            price_per_tib = float(os.environ.get("SAFE_PRICE_PER_TIB", "5.0"))

        # Calculate cost estimate
        bytes_processed = query_job.total_bytes_processed or 0
        tib_processed = bytes_processed / (2**40)
        usd_estimate = round(tib_processed * price_per_tib, 6)

        # Extract referenced tables
        referenced_tables = []
        if query_job.referenced_tables:
            for table_ref in query_job.referenced_tables:
                referenced_tables.append(
                    {
                        "project": table_ref.project,
                        "dataset": table_ref.dataset_id,
                        "table": table_ref.table_id,
                    }
                )

        # Extract schema preview
        schema_preview = []
        if query_job.schema:
            for field in query_job.schema:
                schema_preview.append(
                    {
                        "name": field.name,
                        "type": field.field_type,
                        "mode": field.mode,
                    }
                )

        return {
            "totalBytesProcessed": bytes_processed,
            "usdEstimate": usd_estimate,
            "referencedTables": referenced_tables,
            "schemaPreview": schema_preview,
        }

    except BadRequest as e:
        error_msg = str(e)
        # Improve error message clarity
        if "Table not found" in error_msg:
            error_msg = (
                f"Table not found. {error_msg}. Please verify the table exists and you have access."
            )
        elif "Column not found" in error_msg:
            error_msg = f"Column not found. {error_msg}. Please check column names and spelling."

        error_result = {"error": {"code": "INVALID_SQL", "message": error_msg}}

        location = extract_error_location(error_msg)
        if location:
            error_result["error"]["location"] = location

        if hasattr(e, "errors") and e.errors:
            error_result["error"]["details"] = e.errors

        return error_result

    except Exception as e:
        # Provide more context for common errors
        error_msg = str(e)
        if "credentials" in error_msg.lower():
            error_msg = f"Authentication error: {error_msg}. Please run 'gcloud auth application-default login' to set up credentials."
        elif "permission" in error_msg.lower():
            error_msg = f"Permission denied: {error_msg}. Please verify you have the necessary BigQuery permissions."

        return {"error": {"code": "UNKNOWN_ERROR", "message": error_msg}}


async def analyze_query_structure(sql: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Analyze BigQuery SQL query structure and complexity.

    Args:
        sql: The SQL query to analyze
        params: Optional query parameters (not used in static analysis)

    Returns:
        Dict with structure analysis including query type, complexity score,
        and feature detection
    """
    try:
        analyzer = SQLAnalyzer(sql)
        result = analyzer.analyze_structure()
        return result

    except Exception as e:
        return {
            "error": {
                "code": "ANALYSIS_ERROR",
                "message": f"Failed to analyze query structure: {str(e)}",
            }
        }


async def extract_dependencies(sql: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Extract table and column dependencies from BigQuery SQL.

    Args:
        sql: The SQL query to analyze
        params: Optional query parameters (not used in static analysis)

    Returns:
        Dict with tables, columns, and dependency graph information
    """
    try:
        analyzer = SQLAnalyzer(sql)
        result = analyzer.extract_dependencies()
        return result

    except Exception as e:
        return {
            "error": {
                "code": "ANALYSIS_ERROR",
                "message": f"Failed to extract dependencies: {str(e)}",
            }
        }


async def validate_query_syntax(sql: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Enhanced syntax validation with detailed error reporting.

    Args:
        sql: The SQL query to validate
        params: Optional query parameters (not used in static analysis)

    Returns:
        Dict with validation results, issues, and suggestions
    """
    try:
        analyzer = SQLAnalyzer(sql)
        result = analyzer.validate_syntax_enhanced()
        return result

    except Exception as e:
        return {
            "error": {
                "code": "ANALYSIS_ERROR",
                "message": f"Failed to validate query syntax: {str(e)}",
            }
        }


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            mcp.server.InitializationOptions(
                server_name="mcp-bigquery",
                server_version=__version__,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
