"""Tool for querying metrics from Lightdash"""

import logging
from typing import Dict, Any, List, Optional

from mcp.types import Tool, TextContent

from dbt_mcp.config.config import Config
from dbt_mcp.lightdash.client import LightdashAPIClient
from dbt_mcp.tools.argument_parser import parse_arguments

logger = logging.getLogger(__name__)


def get_lightdash_query_metrics_tool() -> Tool:
    """Get the Lightdash query metrics tool definition"""
    return Tool(
        name="lightdash_query_metrics",
        description="""Execute a metrics query after discovering available metrics and dimensions.

This is the FINAL STEP in the discovery flow:
1. lightdash_list_explores → Find data models
2. lightdash_list_metrics → Find available metrics  
3. lightdash_get_dimensions → Find grouping dimensions
4. lightdash_query_metrics → Run the analysis (THIS TOOL)

## CRITICAL: Correct Field Names
Use EXACT field names from schema:
- Attribution: Use 'model' (NOT attribution_mode, NOT attribution_model)
- Channel: Use 'channel' (NOT platform, NOT source)
- Date: Use 'event_date' for pixel_joined

## Filter Examples
```json
{"field": "channel", "operator": "equals", "value": "facebook"}
{"field": "model", "operator": "equals", "value": "last_click"}
{"field": "attribution_window", "operator": "equals", "value": "7_days"}
{"field": "event_date", "operator": "inThePast", "value": 30, "unit": "days"}
```

## Smart Value Normalization
The tool automatically fixes common mistakes:
- Attribution windows: "7_day" → "7_days", "30_day" → "30_days" 
- Models: "last-click" → "last_click", "first click" → "first_click"
- Field names: "attribution_model" → "model", "attribution_mode" → "model"

## Full Query Examples

### Example 1: Facebook ROAS with attribution
{
  "explore": "pixel_joined",
  "metrics": ["total_roas_excluding_blended"],
  "group_by": ["event_date"],
  "filters": [
    {"field": "channel", "operator": "equals", "value": "facebook"},
    {"field": "model", "operator": "equals", "value": "last_click"},
    {"field": "attribution_window", "operator": "equals", "value": "7_days"}
  ],
  "order_by": [{"field": "event_date", "order": "desc"}],
  "limit": 30
}

### Example 2: Revenue by product category
{
  "explore": "orders",
  "metrics": ["total_revenue", "order_count"],
  "group_by": ["product_category"],
  "order_by": [{"field": "total_revenue", "order": "desc"}],
  "limit": 10
}

## Required Filters for pixel_joined
ALWAYS include these filters for attribution data:
- model: "last_click" or "first_click"  
- attribution_window: "7_days" or "30_days" (note: plural form with 's')
Without these, results aggregate ALL attribution models!""",
        inputSchema={
            "type": "object",
            "properties": {
                "explore": {
                    "type": "string",
                    "description": "The explore to query"
                },
                "metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of metric names to query"
                },
                "group_by": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional list of dimensions to group by"
                },
                "order_by": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {"type": "string"},
                            "order": {"type": "string", "enum": ["asc", "desc"]}
                        }
                    },
                    "description": "Optional ordering"
                },
                "filters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "field": {"type": "string"},
                            "operator": {"type": "string"},
                            "value": {}
                        }
                    },
                    "description": "Optional filters"
                },
                "limit": {
                    "type": "integer",
                    "description": "Result limit",
                    "default": 100
                }
            },
            "required": ["explore", "metrics"]
        }
    )


async def handle_lightdash_query_metrics(
    arguments: Dict[str, Any], config: Config
) -> List[TextContent]:
    """Handle the query metrics request"""
    
    # Parse arguments
    try:
        arguments = parse_arguments(arguments)
    except Exception as e:
        logger.error(f"Failed to parse arguments: {e}")
        return [
            TextContent(
                type="text",
                text=f"Error parsing arguments: {str(e)}"
            )
        ]
    
    if not config.lightdash_config:
        return [
            TextContent(
                type="text",
                text="Error: Lightdash configuration is not available"
            )
        ]
    
    explore = arguments.get("explore")
    metrics = arguments.get("metrics", [])
    group_by = arguments.get("group_by", [])
    order_by = arguments.get("order_by", [])
    filters = arguments.get("filters", [])
    limit = arguments.get("limit", 100)
    
    if not explore:
        return [
            TextContent(
                type="text",
                text="Error: explore is required"
            )
        ]
    
    if not metrics:
        return [
            TextContent(
                type="text",
                text="Error: at least one metric is required"
            )
        ]
    
    try:
        client = LightdashAPIClient(config.lightdash_config)
        
        logger.info(f"Executing query on explore '{explore}' with metrics: {metrics}")
        
        # Build the metric query in Lightdash format
        # Always add the explore prefix unless it's already there
        processed_metrics = []
        for m in metrics:
            if m.startswith(f"{explore}_"):
                processed_metrics.append(m)
            else:
                processed_metrics.append(f"{explore}_{m}")
        
        processed_dimensions = []
        for d in group_by:
            if d.startswith(f"{explore}_"):
                processed_dimensions.append(d)
            else:
                processed_dimensions.append(f"{explore}_{d}")
        
        metric_query = {
            "exploreName": explore,
            "dimensions": processed_dimensions,
            "metrics": processed_metrics,
            "sorts": [],
            "limit": limit,
            "filters": {},
            "tableCalculations": [],
            "additionalMetrics": []
        }
        
        # Add filters if present
        if filters:
            filter_rules = []
            for filter_spec in filters:
                field = filter_spec.get("field")
                operator = filter_spec.get("operator", "equals")
                value = filter_spec.get("value")
                
                # Smart value normalization for common mistakes
                if field == "attribution_window" and value:
                    # Fix common attribution window mistakes
                    value_mapping = {
                        "1_day": "1_days",
                        "7_day": "7_days", 
                        "14_day": "14_days",
                        "30_day": "30_days",
                        "60_day": "60_days",
                        "90_day": "90_days",
                        # Also handle without underscore
                        "1 day": "1_days",
                        "7 days": "7_days",
                        "14 days": "14_days",
                        "30 days": "30_days",
                        "60 days": "60_days",
                        "90 days": "90_days",
                        # Handle numeric only
                        "1": "1_days",
                        "7": "7_days",
                        "14": "14_days",
                        "30": "30_days",
                        "60": "60_days",
                        "90": "90_days"
                    }
                    if value in value_mapping:
                        logger.info(f"Normalizing attribution_window value from '{value}' to '{value_mapping[value]}'")
                        value = value_mapping[value]
                
                # Smart normalization for model/attribution model
                if field in ["model", "attribution_model", "attribution_mode"] and value:
                    # Normalize field name
                    field = "model"
                    # Normalize common model values
                    value_mapping = {
                        "last-click": "last_click",
                        "first-click": "first_click", 
                        "last click": "last_click",
                        "first click": "first_click",
                        "lastclick": "last_click",
                        "firstclick": "first_click"
                    }
                    if value.lower() in value_mapping:
                        logger.info(f"Normalizing model value from '{value}' to '{value_mapping[value.lower()]}'")
                        value = value_mapping[value.lower()]
                
                # Add prefix if not already present
                if field.startswith(f"{explore}_"):
                    field_id = field
                else:
                    field_id = f"{explore}_{field}"
                
                filter_rule = {
                    "id": field_id,
                    "target": {"fieldId": field_id},
                    "operator": operator,
                    "values": [value] if value is not None else []
                }
                
                # Handle time-based filters
                if operator == "inThePast" and filter_spec.get("unit"):
                    filter_rule["settings"] = {
                        "unitOfTime": filter_spec["unit"],
                        "completed": False
                    }
                
                filter_rules.append(filter_rule)
            
            if filter_rules:
                # FIXED: Use correct Lightdash filter structure
                # Filters go in dimensions/metrics/tableCalculations, not in a top-level "and"
                metric_query["filters"] = {
                    "dimensions": {
                        "id": "root",
                        "and": filter_rules
                    }
                }
        
        # Add sorts
        for sort_spec in order_by:
            field = sort_spec.get("field")
            order = sort_spec.get("order", "asc")
            if field:
                # Add prefix if not already present
                if field.startswith(f"{explore}_"):
                    field_id = field
                else:
                    field_id = f"{explore}_{field}"
                metric_query["sorts"].append({
                    "fieldId": field_id,
                    "descending": order == "desc"
                })
        
        # Execute using compile + SQL approach
        compile_endpoint = f"/projects/{client.project_id}/explores/{explore}/compileQuery"
        compile_result = await client._make_request("POST", compile_endpoint, data=metric_query)
        
        if "results" in compile_result:
            sql = compile_result["results"]
            
            # Execute SQL
            v2_sql_endpoint = f"/projects/{client.project_id}/query/sql"
            sql_payload = {"sql": sql}
            
            sql_result = await client._make_request("POST", v2_sql_endpoint, data=sql_payload, use_v2=True)
            
            if "results" in sql_result and "queryUuid" in sql_result["results"]:
                query_uuid = sql_result["results"]["queryUuid"]
                
                # Poll for results
                import asyncio
                max_attempts = 30
                for attempt in range(max_attempts):
                    status_endpoint = f"/projects/{client.project_id}/query/{query_uuid}"
                    status_result = await client._make_request("GET", status_endpoint, use_v2=True)
                    
                    if "results" in status_result:
                        status_data = status_result["results"]
                        status = status_data.get("status")
                        
                        if status in ["completed", "ready"]:
                            query_result = status_data
                            break
                        elif status == "error":
                            error_msg = status_data.get("error", "Unknown error")
                            raise Exception(f"Query failed: {error_msg}")
                    
                    await asyncio.sleep(1)
                else:
                    raise Exception("Query timed out after 30 seconds")
        else:
            raise Exception("Failed to compile query")
        
        # Format results
        result_text = f"Query Results:\n"
        result_text += f"Metrics: {', '.join(metrics)}\n"
        if group_by:
            result_text += f"Grouped by: {', '.join(group_by)}\n"
        result_text += "\n"
        
        if "rows" in query_result:
            row_count = len(query_result["rows"])
            result_text += f"Found {row_count} rows\n\n"
            
            if row_count > 0:
                # Format as table-like output
                for i, row in enumerate(query_result["rows"][:20], 1):
                    result_text += f"{i}. "
                    # Format each field
                    formatted_fields = []
                    for key, value in row.items():
                        # Clean up field names (remove table prefix)
                        clean_key = key.split('_', 1)[-1] if '_' in key else key
                        # Handle nested value structure
                        if isinstance(value, dict) and 'value' in value:
                            val = value['value']
                            if isinstance(val, dict):
                                display_val = val.get('formatted', val.get('raw', str(val)))
                            else:
                                display_val = val
                        else:
                            display_val = value
                        formatted_fields.append(f"{clean_key}: {display_val}")
                    result_text += " | ".join(formatted_fields) + "\n"
                
                if row_count > 20:
                    result_text += f"\n... and {row_count - 20} more rows"
        else:
            result_text += "No results found"
        
        return [
            TextContent(
                type="text",
                text=result_text
            )
        ]
        
    except Exception as e:
        error_msg = f"Error executing query: {str(e)}"
        logger.error(error_msg)
        return [
            TextContent(
                type="text",
                text=error_msg
            )
        ]