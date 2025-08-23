"""SQL generator for building SELECT queries with GraphQL-aware JSONB projection.

Supports JSONB path extraction and camelCase aliasing for GraphQL field names.
Integrates deeply with FraiseQL's AST selection and schema mappings to construct
optimized PostgreSQL queries using `jsonb_build_object` for minimal post-processing.
"""

from collections.abc import Sequence

from psycopg import sql
from psycopg.sql import SQL, Composed, Identifier

from fraiseql.core.ast_parser import FieldPath


def _convert_order_by_to_tuples(order_by):
    """Convert any OrderBy format to list of tuples.

    Args:
        order_by: OrderBy in any format (GraphQL dicts, tuples, OrderBySet)

    Returns:
        List of (field, direction) tuples or None
    """
    if not order_by:
        return None

    # Already a list of tuples
    if isinstance(order_by, list) and order_by and isinstance(order_by[0], tuple):
        return order_by

    # GraphQL format - convert using FraiseQL
    if isinstance(order_by, (list, dict)):
        try:
            from fraiseql.sql.graphql_order_by_generator import _convert_order_by_input_to_sql

            order_by_set = _convert_order_by_input_to_sql(order_by)
            if order_by_set:
                return [(instr.field, instr.direction) for instr in order_by_set.instructions]
        except (ImportError, AttributeError):
            pass

    # OrderBySet object
    if hasattr(order_by, "instructions"):
        return [(instr.field, instr.direction) for instr in order_by.instructions]

    return None


def build_sql_query(
    table: str,
    field_paths: Sequence[FieldPath],
    where_clause: SQL | None = None,
    *,
    json_output: bool = False,
    typename: str | None = None,
    order_by: Sequence[tuple[str, str]] | None = None,
    group_by: Sequence[str] | None = None,
    auto_camel_case: bool = False,
    raw_json_output: bool = False,
    field_limit_threshold: int | None = None,
    camelforge_enabled: bool = False,
    camelforge_function: str = "turbo.fn_camelforge",
    entity_type: str | None = None,
) -> Composed:
    """Build a SELECT SQL query using jsonb path extraction and optional WHERE/ORDER BY/GROUP BY.

    If `json_output` is True, wraps the result in jsonb_build_object(...)
    and aliases it as `result`. Adds '__typename' if `typename` is provided.

    Args:
        table: Table name to query
        field_paths: Sequence of field paths to extract
        where_clause: Optional WHERE clause
        json_output: Whether to wrap output in jsonb_build_object
        typename: Optional GraphQL typename to include
        order_by: Optional list of (field_path, direction) tuples for ORDER BY
        group_by: Optional list of field paths for GROUP BY
        auto_camel_case: Whether to preserve camelCase field paths (True) or convert to snake_case
        raw_json_output: Whether to cast output to text for raw JSON passthrough
        field_limit_threshold: If set and field count exceeds this, return full data column
        camelforge_enabled: Whether to wrap jsonb_build_object with CamelForge function
        camelforge_function: Name of the CamelForge function to use (default: turbo.fn_camelforge)
        entity_type: Entity type for CamelForge transformation (required if camelforge_enabled=True)
    """
    # Validate CamelForge parameters
    if camelforge_enabled and entity_type is None:
        raise ValueError("entity_type is required when camelforge_enabled=True")

    # Check if we should use full data column to avoid parameter limit
    if field_limit_threshold is not None and len(field_paths) > field_limit_threshold:
        # Simply select the full data column
        if raw_json_output:
            select_clause = SQL("data::text AS result")
        elif json_output:
            select_clause = SQL("data AS result")
        else:
            select_clause = SQL("data")

        base = SQL("SELECT {} FROM {}").format(select_clause, Identifier(table))

        # Build query with clauses in correct SQL order
        query_parts = [base]

        if where_clause:
            query_parts.append(SQL(" WHERE "))
            query_parts.append(where_clause)

        # Note: GROUP BY and ORDER BY are skipped when using full data column
        # This is a current limitation that could be addressed in future versions

        return sql.SQL("").join(query_parts)

    # Original implementation for when threshold is not exceeded
    object_pairs: list[sql.Composable] = []

    for field in field_paths:
        json_path_parts = [sql.Literal(part) for part in field.path[:-1]]
        last_part = field.path[-1]

        expr = sql.SQL("data")
        for key in json_path_parts:
            expr = sql.SQL("{}->{}").format(expr, key)

        # CRITICAL FIX: Selective type preservation for frontend compatibility
        # Use -> operator for JSON-native types (int, float, bool, null, arrays, objects)
        # Use ->> operator for PostgreSQL-specific types that need string conversion
        #
        # Frontend-compatible types: number, boolean, null, string, array, object
        # PostgreSQL types needing conversion: uuid, inet, cidr, ltree, daterange, etc.
        #
        # Strategy: Use -> by default to preserve JSON types, let the serializer handle
        # PostgreSQL-specific type conversion in the FraiseQLJSONEncoder
        expr = sql.SQL("{}->{}").format(expr, sql.Literal(last_part))
        object_pairs.append(sql.Literal(field.alias))
        object_pairs.append(expr)

    if typename is not None:
        object_pairs.append(sql.Literal("__typename"))
        object_pairs.append(sql.Literal(typename))

    if json_output:
        # Build the jsonb_build_object expression
        jsonb_expr = SQL("jsonb_build_object({})").format(SQL(", ").join(object_pairs))

        # Wrap with CamelForge if enabled
        if camelforge_enabled:
            camelforge_expr = SQL("{}({}, {})").format(
                SQL(camelforge_function), jsonb_expr, sql.Literal(entity_type)
            )
            if raw_json_output:
                select_clause = SQL("{}::text AS result").format(camelforge_expr)
            else:
                select_clause = SQL("{} AS result").format(camelforge_expr)
        # Normal jsonb_build_object without CamelForge
        elif raw_json_output:
            select_clause = SQL("{}::text AS result").format(jsonb_expr)
        else:
            select_clause = SQL("{} AS result").format(jsonb_expr)
    else:
        select_items = [
            SQL("{} AS {}{}").format(expr, Identifier(field.alias), SQL(""))
            for field, expr in zip(field_paths, object_pairs[1::2], strict=False)
        ]
        select_clause = SQL(", ").join(select_items)

    base = SQL("SELECT {} FROM {}").format(select_clause, Identifier(table))

    # Build query with clauses in correct SQL order
    query_parts = [base]

    if where_clause:
        query_parts.append(SQL(" WHERE "))
        query_parts.append(where_clause)

    if group_by:
        group_by_parts = []
        for field_path in group_by:
            # Convert field path (e.g., "profile.age") to JSONB expression
            path_parts = field_path.split(".")

            # Apply snake_case transformation if auto_camel_case is disabled
            if not auto_camel_case:
                from fraiseql.utils.casing import to_snake_case

                path_parts = [to_snake_case(part) for part in path_parts]

            if len(path_parts) == 1:
                # Top-level field
                expr = SQL("data->>{}").format(sql.Literal(path_parts[0]))
            else:
                # Nested field
                json_path = [sql.Literal(part) for part in path_parts[:-1]]
                expr = SQL("data")
                for part in json_path:
                    expr = SQL("{}->{}").format(expr, part)
                expr = SQL("{}->>{}").format(expr, sql.Literal(path_parts[-1]))
            group_by_parts.append(expr)

        query_parts.append(SQL(" GROUP BY "))
        query_parts.append(SQL(", ").join(group_by_parts))

    if order_by:
        order_by_parts = []
        # Safety net: convert OrderBy to tuples if needed
        order_by_tuples = _convert_order_by_to_tuples(order_by)
        if not order_by_tuples:
            # If conversion failed, assume it's already in correct format
            order_by_tuples = order_by

        for field_path, direction in order_by_tuples:
            # Convert field path to JSONB expression
            path_parts = field_path.split(".")

            # Apply snake_case transformation if auto_camel_case is disabled
            if not auto_camel_case:
                from fraiseql.utils.casing import to_snake_case

                path_parts = [to_snake_case(part) for part in path_parts]

            if len(path_parts) == 1:
                # Top-level field
                expr = SQL("data->>{}").format(sql.Literal(path_parts[0]))
            else:
                # Nested field
                json_path = [sql.Literal(part) for part in path_parts[:-1]]
                expr = SQL("data")
                for part in json_path:
                    expr = SQL("{}->{}").format(expr, part)
                expr = SQL("{}->>{}").format(expr, sql.Literal(path_parts[-1]))

            # Add direction (ASC/DESC)
            order_expr = expr + SQL(" ") + SQL(direction.upper())
            order_by_parts.append(order_expr)

        query_parts.append(SQL(" ORDER BY "))
        query_parts.append(SQL(", ").join(order_by_parts))

    return sql.Composed(query_parts)
