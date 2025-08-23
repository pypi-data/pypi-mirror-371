#!/usr/bin/env python3
"""
halfORM inspect extension CLI interface

Provides database inspection functionality through the halfORM CLI.
"""

import sys
import click
from half_orm.model import Model
from half_orm.cli_utils import add_direct_command

rel_type_d = {
    'r': ("📋", "table"),
    'v': ("👁️ ", "view"),
    'p': ("📊", "partitioned table"),
    'm': ("🔗", "materialized view")
}
type_map = { value[1].split()[0]: key for key, value in rel_type_d.items() }


def add_commands(main_group):
    """
    Add inspect commands to the main CLI group.
    
    This function is called by the halfORM CLI discovery system
    to integrate this extension's commands.
    
    Args:
        main_group: Click group to add commands to
    """
    
    # Utilise la nouvelle fonction utilitaire pour ajouter directement la commande
    @add_direct_command(main_group, sys.modules[__name__])
    @click.argument('target')
    @click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
    @click.option('--type', '-t', 'relation_type', 
                  type=click.Choice(['table', 'view', 'partitioned', 'materialized']),
                  help='Filter by relation type (only when inspecting database/schema)')
    @click.option('--schema-only', '-s', is_flag=True, help='Show only schema list (database level only)')
    def inspect_command(target, output_json, relation_type, schema_only):
        """Inspect database structure using halfORM introspection.
        
        TARGET can be:
        
        \b
        • DATABASE_NAME: List all relations in database
        • DATABASE.SCHEMA: List all relations in specific schema  
        • DATABASE.SCHEMA.RELATION: Inspect specific relation
        
        \b
        Examples:
        \b
            half_orm inspect mydb                    # List all relations
            half_orm inspect mydb -s                 # List only schemas
            half_orm inspect mydb.public             # List relations in schema
            half_orm inspect mydb.public.users       # Inspect specific table
            half_orm inspect mydb --type table       # Filter by type
            half_orm inspect mydb --json             # JSON output
        """
        try:
            # Connect to database first
            parts = target.split('.')
            database_name = parts[0]
            model = Model(database_name)
            
            # Smart parsing that handles dots in schema/table names
            schema_name, relation_name = _parse_target(model, target, database_name)
            
            if relation_name:
                # Inspect specific relation
                full_relation_name = f"{schema_name}.{relation_name}" if schema_name else relation_name
                _inspect_relation(model, full_relation_name, output_json)
            elif schema_name:
                # Inspect specific schema
                _inspect_schema(model, database_name, schema_name, output_json, relation_type)
            else:
                # Inspect entire database
                _inspect_database(model, database_name, schema_only, output_json, relation_type)
                    
        except ImportError:
            click.echo("❌ halfORM core not properly installed", err=True)
            sys.exit(1)
        except Exception as e:
            # Enhanced error message for parsing issues
            if "does not exist" in str(e) or "not found" in str(e):
                click.echo(f"❌ Error inspecting '{target}': {e}", err=True)
            else:
                click.echo(f"❌ Error inspecting '{target}': {e}", err=True)
                click.echo("💡 Check your database configuration in HALFORM_CONF_DIR", err=True)
            sys.exit(1)


def _parse_target(model, target, database_name):
    """
    Smart parsing of target that handles dots in schema/table names.
    
    Tries different interpretations and checks which ones actually exist:
    1. database -> (None, None)
    2. database.schema -> (schema, None) 
    3. database.schema.table -> (schema, table)
    
    Args:
        model: halfORM Model instance
        target: Full target string (e.g., "mydb.my.schema.table")
        database_name: Already extracted database name
        
    Returns:
        tuple: (None, None), (schema_name, None) or (schema_name, relation_name)
    """
    parts = target.split('.')
    
    # Just database name
    if len(parts) == 1:
        return None, None
    
    # Get all existing schemas and relations for validation
    all_relations = list(model._relations())
    existing_schemas = set(r[1][1] for r in all_relations)  # r[1] is (db, schema, table)
    existing_relations = {}  # schema -> set of tables
    for relation in all_relations:
        relation_type, (_, schema, table) = relation
        if schema not in existing_relations:
            existing_relations[schema] = set()
        existing_relations[schema].add(table)
    
    potential_schema = '.'.join(parts[1:])
    if potential_schema in existing_relations:
        return potential_schema, None
    potential_schema = '.'.join(parts[1:-1])
    potential_table = parts[-1]
    return potential_schema, potential_table

def _inspect_relation(model, relation_name, output_json=False):
    """Inspect a specific relation."""
    try:
        relation_class = model.get_relation_class(relation_name)
        relation_instance = relation_class()
        
        if output_json:
            import json
            # Create JSON representation
            relation_info = {
                'name': relation_name,
                'primary_key': _get_primary_key(relation_instance),
                'foreign_keys': _get_foreign_keys(relation_instance)
            }
            click.echo(json.dumps(relation_info, indent=2))
        else:
            click.echo(f"=== {relation_name} ===")
            click.echo(str(relation_instance))
            
    except Exception as e:
        click.echo(f"❌ Error inspecting {relation_name}: {e}", err=True)
        sys.exit(1)


def _inspect_schema(model, database_name, schema_name, output_json=False, type_filter=None):
    """Inspect a specific schema."""
    try:
        relations = list(model._relations())
        
        schema_relations = [
            r for r in relations 
            if r[1][1] == schema_name  # r[1] is (db, schema, table)
        ]
        
        # Apply type filter
        if type_filter:
            schema_relations = _filter_relations(schema_relations, None, type_filter)
        
        if not schema_relations:
            click.echo(f"No relations found in schema '{schema_name}'")
            return
        
        if output_json:
            import json
            relations_data = []
            for relation in schema_relations:
                relation_type, (_, schema, table) = relation
                rel_data = {
                    'schema': schema,
                    'table': table,
                    'type': _get_relation_type_name(relation_type)
                }
                relations_data.append(rel_data)
            click.echo(json.dumps({
                'database': database_name,
                'schema': schema_name,
                'relations': relations_data,
                'total': len(relations_data)
            }, indent=2))
        else:
            click.echo(f"=== Schema: {schema_name} (Database: {database_name}) ===")
            _display_relations_list(schema_relations, model)
            
    except Exception as e:
        click.echo(f"❌ Error inspecting schema '{schema_name}': {e}", err=True)
        sys.exit(1)


def _inspect_database(model, database_name, schema_only, output_json=False, type_filter=None):
    """Inspect entire database."""
    click.echo(f"=== Database: {database_name} ===")
    relations = list(model._relations())
    
    if not relations:
        click.echo("No relations found in database")
        return
    
    # Apply filters
    if type_filter:
        relations = _filter_relations(relations, None, type_filter)
    
    if output_json:
        import json
        relations_data = []
        for relation in relations:
            relation_type, (_, schema, table) = relation
            rel_data = {
                'schema': schema,
                'table': table,
                'type': _get_relation_type_name(relation_type)
            }
            relations_data.append(rel_data)
        click.echo(json.dumps({
            'database': database_name,
            'relations': relations_data,
            'total': len(relations_data)
        }, indent=2))
    else:
        _display_relations_grouped(database_name, relations, model, schema_only)


def _filter_relations(relations, schema_filter, type_filter):
    """Filter relations based on criteria."""
    filtered = []
        
    for relation in relations:
        relation_type, (_, schema, table) = relation
        
        # Schema filter
        if schema_filter and schema != schema_filter:
            continue
            
        # Type filter
        if type_filter and relation_type != type_map.get(type_filter):
            continue
            
        filtered.append(relation)
    
    return filtered


def _display_relations_grouped(database_name, relations=False, model=None, schema_only=False):
    """Display relations grouped by schema."""
    # Group by schema
    schemas = {}
    for relation in relations:
        relation_type, (_, schema, table) = relation
        if schema not in schemas:
            schemas[schema] = []
        schemas[schema].append((relation_type, table))
    
    # Display grouped by schema
    count_d = {}
    
    for schema, tables in sorted(schemas.items()):
        sch_item = f"📂 Schema: {schema}"
        if schema_only:
            click.echo(sch_item)
            continue
        click.echo(f"\n{sch_item}")
        for rel_type, table in sorted(tables):
            if rel_type not in count_d:
                count_d[rel_type] = 0
            count_d[rel_type] += 1
            type_icon = rel_type_d.get(rel_type, ("❓", "unknown"))[0]
            click.echo(f"  {type_icon} {table}")
    
    # Summary
    click.echo(f"\nTotal: {len(relations)} relations")
    for rel_type in rel_type_d:
        count = count_d.get(rel_type)
        if count:
            plural = 's' if count > 1 else ''
            icon, name = rel_type_d[rel_type]
            click.echo(f"   {icon}: {count} {name}{plural}")
    
    click.echo(f"\nUse 'half_orm inspect {database_name}.<schema>[.<table>]' for detailed information")


def _display_relations_list(relations=False, model=None):
    """Display relations as a simple list (for single schema)."""
    count_d = {}
    
    for relation in relations:
        relation_type, (_, schema, table) = relation
        if relation_type not in count_d:
            count_d[relation_type] = 0
        count_d[relation_type] += 1
        type_icon = rel_type_d.get(relation_type, ("❓", "unknown"))[0]
        click.echo(f"  {type_icon} {table}")
        
        # Show additional info if requested

    # Summary
    click.echo(f"\nTotal: {len(relations)} relations")
    for rel_type in rel_type_d:
        count = count_d.get(rel_type)
        if count:
            plural = 's' if count > 1 else ''
            icon, name = rel_type_d[rel_type]
            click.echo(f"   {icon}: {count} {name}{plural}")


def _get_relation_type_name(relation_type):
    """Convert relation type code to human readable name."""
    return type_map.get(relation_type, 'unknown')


def _get_primary_key(relation_instance):
    """Extract primary key information."""
    try:
        return getattr(relation_instance, '_primary_key', None)
    except:
        return None


def _get_foreign_keys(relation_instance):
    """Extract foreign key information."""
    try:
        return getattr(relation_instance, '_foreign_keys', [])
    except:
        return []
