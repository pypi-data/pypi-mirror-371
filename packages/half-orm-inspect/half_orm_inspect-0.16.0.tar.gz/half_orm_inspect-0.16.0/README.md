# half-orm-inspect

Database inspection extension for halfORM - powerful PostgreSQL database introspection and exploration tools.

[![PyPI version](https://badge.fury.io/py/half-orm-inspect.svg)](https://badge.fury.io/py/half-orm-inspect)
[![Python Support](https://img.shields.io/pypi/pyversions/half-orm-inspect.svg)](https://pypi.org/project/half-orm-inspect/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

## 🎯 Overview

`half-orm-inspect` provides comprehensive database inspection capabilities for halfORM projects. Explore your PostgreSQL database structure, analyze tables, views, and schemas with ease through both CLI and programmatic interfaces.

## ✨ Features

- **📊 Database Overview**: List all relations with type indicators and statistics
- **🔍 Detailed Inspection**: Deep dive into specific tables, views, and schemas
- **📈 Schema Analysis**: Explore schema organization and relationship mapping
- **📋 Multiple Output Formats**: Human-readable console output and JSON export
- **🎯 Smart Filtering**: Filter by relation type with intelligent target parsing
- **🔗 halfORM Integration**: Seamless integration with halfORM CLI ecosystem
- **🧠 Smart Target Parsing**: Handles dots in schema and table names automatically

## 🚀 Installation

```bash
# Install via pip
pip install half-orm-inspect

# Or install from source
git clone https://github.com/half-orm/half-orm-inspect.git
cd half-orm-inspect
pip install -e .
```

### Prerequisites

- Python 3.7+
- halfORM >= 0.16.0
- PostgreSQL database with halfORM configuration

## 📖 Usage

### Through halfORM CLI (Recommended)

```bash
# List all database relations
half_orm inspect mydatabase

# Inspect specific schema
half_orm inspect mydatabase.public

# Inspect specific table
half_orm inspect mydatabase.public.users

# Show only schema list
half_orm inspect mydatabase --schema-only

# Filter by relation type
half_orm inspect mydatabase --type table
half_orm inspect mydatabase.public --type view

# JSON output for scripting
half_orm inspect mydatabase --json
```

### Advanced Target Parsing

The inspect command intelligently handles dots in schema and table names:

```bash
# These all work correctly:
half_orm inspect mydatabase
half_orm inspect mydatabase.my_schema
half_orm inspect mydatabase.my.complex.schema
half_orm inspect mydatabase.my.schema.table_name
```

## 💡 Examples

### Basic Database Exploration

```bash
$ half_orm inspect ecommerce

=== Database: ecommerce ===

📂 Schema: public
  📋 users
  📋 products
  📋 orders
  👁️  order_summary
  🔗 sales_report

📂 Schema: inventory
  📋 stock_items
  📋 suppliers
  📊 product_stats

Total: 8 relations
   📋: 5 tables
   👁️ : 1 views
   🔗: 1 materialized views
   📊: 1 partitioned tables

Use 'half_orm inspect ecommerce.<schema>[.<table>]' for detailed information
```

### Schema-Only Listing

```bash
$ half_orm inspect ecommerce --schema-only

=== Database: ecommerce ===
📂 Schema: public
📂 Schema: inventory
📂 Schema: analytics
```

### Schema Inspection

```bash
$ half_orm inspect ecommerce.public

=== Schema: public (Database: ecommerce) ===
  📋 users
  📋 products
  📋 orders
  👁️  order_summary
  🔗 sales_report

Total: 5 relations
   📋: 3 tables
   👁️ : 1 views
   🔗: 1 materialized views
```

### Table Details

```bash
$ half_orm inspect ecommerce.public.users

=== ecommerce.public.users ===
Table: users
Columns:
  • id (integer, PRIMARY KEY)
  • email (varchar(255), NOT NULL, UNIQUE)
  • created_at (timestamp with time zone, DEFAULT now())
  • profile_data (jsonb)

Indexes:
  • users_pkey (PRIMARY KEY on id)
  • users_email_idx (UNIQUE on email)

Foreign Keys: None
Referenced By:
  • orders.user_id → users.id
```

### Filtering by Type

```bash
# Show only tables in database
$ half_orm inspect ecommerce --type table

# Show only views in specific schema
$ half_orm inspect ecommerce.public --type view

# Available types: table, view, partitioned, materialized
```

### JSON Output for Scripts

```bash
$ half_orm inspect ecommerce --json | jq '.relations[] | select(.type=="table")'

{
  "schema": "public",
  "table": "users", 
  "type": "table"
}
{
  "schema": "public",
  "table": "products",
  "type": "table"
}
```

```bash
$ half_orm inspect ecommerce.public --json

{
  "database": "ecommerce",
  "schema": "public",
  "relations": [
    {
      "schema": "public",
      "table": "users",
      "type": "table"
    },
    {
      "schema": "public", 
      "table": "products",
      "type": "table"
    }
  ],
  "total": 5
}
```

## 🔧 Configuration

`half-orm-inspect` uses your existing halfORM database configuration. Ensure your database is properly configured in your halfORM project:

```bash
# Verify your database configuration
export HALFORM_CONF_DIR=/path/to/your/config
half_orm inspect yourdatabase
```

## 🔧 Command Options

### Target Formats

| Format | Description | Example |
|--------|-------------|---------|
| `DATABASE` | List all relations in database | `half_orm inspect mydb` |
| `DATABASE.SCHEMA` | List relations in specific schema | `half_orm inspect mydb.public` |
| `DATABASE.SCHEMA.RELATION` | Inspect specific relation | `half_orm inspect mydb.public.users` |

### Available Options

| Option | Short | Description |
|--------|--------|-------------|
| `--json` | | Output as JSON format |
| `--type` | `-t` | Filter by relation type (table, view, partitioned, materialized) |
| `--schema-only` | `-s` | Show only schema list (database level only) |

### Type Filters

- `table` - Regular tables (📋)
- `view` - Database views (👁️)
- `partitioned` - Partitioned tables (📊)
- `materialized` - Materialized views (🔗)

## 🛠️ Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/half-orm/half-orm-inspect.git
cd half-orm-inspect

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
black half_orm_inspect/
flake8 half_orm_inspect/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=half_orm_inspect --cov-report=html

# Run specific test categories
pytest tests/test_cli.py -v
```

## 📊 Output Formats

### Console Output
- **Emoji indicators**: 📋 tables, 👁️ views, 🔗 materialized views, 📊 partitioned tables
- **Color coding**: Schema names, relation types, and statistics
- **Hierarchical display**: Grouped by schema for easy navigation
- **Smart parsing**: Handles complex schema and table names with dots

### JSON Output
Perfect for scripting and automation:

```json
{
  "database": "ecommerce",
  "relations": [
    {
      "schema": "public",
      "table": "users",
      "type": "table"
    }
  ],
  "total": 8
}
```

For schema-specific inspection:
```json
{
  "database": "ecommerce", 
  "schema": "public",
  "relations": [...],
  "total": 5
}
```

## 📌 Integration with halfORM CLI

This extension integrates seamlessly with the halfORM CLI ecosystem:

```bash
# List all extensions
half_orm --list-extensions

# Show extension info
half_orm version

# Manage extension trust (for non-official extensions)
half_orm --untrust half-orm-inspect
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

The GPL-v3 ensures that this software remains free and open source, and that any derivative works are also made available under the same terms. This helps maintain and grow the open source ecosystem around halfORM.

## 🔗 Links

- **halfORM Core**: [https://github.com/half-orm/half_orm](https://github.com/half-orm/half_orm)
- **Documentation**: [https://half-orm.org/extensions/inspect](https://half-orm.org/extensions/inspect)
- **PyPI Package**: [https://pypi.org/project/half-orm-inspect/](https://pypi.org/project/half-orm-inspect/)
- **Issue Tracker**: [https://github.com/half-orm/half-orm-inspect/issues](https://github.com/half-orm/half-orm-inspect/issues)

## 📈 Version Compatibility

The `<major>.<minor>` version of `half-orm-inspect` must match your `half-orm` core version for compatibility.

## 💬 Support

- **Documentation**: Check the [halfORM docs](https://half-orm.github.io/half-orm)
- **Issues**: Report bugs on [GitHub Issues](https://github.com/half-orm/half-orm-inspect/issues)
- **Discussions**: Join conversations on [GitHub Discussions](https://github.com/half-orm/half_orm/discussions)

---

**Made with ❤️ by the halfORM Team**