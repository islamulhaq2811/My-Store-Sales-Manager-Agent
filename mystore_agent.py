from sqlalchemy import text
from mystore_db import get_mystore_session, get_mystore_tables, get_mystore_metadata, is_mystore_configured

class MystoreAgent:
    def __init__(self):
        self.db = None
        self.connected = False

    def _ensure_connection(self):
        if not is_mystore_configured():
            return False
        if self.db is None:
            self.db = get_mystore_session()
            self.connected = True
        return True

    def get_tables(self):
        if not self._ensure_connection():
            return []
        return get_mystore_tables()

    def get_table_data(self, table_name: str, limit: int = 50):
        if not self._ensure_connection():
            return None
        metadata = get_mystore_metadata()
        table = metadata.tables.get(table_name)
        if table is None:
            return None
        result = self.db.query(table).limit(limit).all()
        columns = [col.name for col in table.columns]
        rows = []
        for row in result:
            rows.append({col: getattr(row, col) for col in columns})
        return {"columns": columns, "rows": rows, "total": len(rows)}

    def get_store_stats(self):
        if not self._ensure_connection():
            return None
        metadata = get_mystore_metadata()
        tables = metadata.tables
        stats = {}

        for name, table in tables.items():
            try:
                count = self.db.query(table).count()
                stats[name] = {"record_count": count}
            except Exception:
                stats[name] = {"record_count": 0}

        return stats

    def search_products(self, query: str = "", limit: int = 20):
        if not self._ensure_connection():
            return None
        metadata = get_mystore_metadata()
        tables = metadata.tables

        product_tables = [t for t_name, t in tables.items()
                          if "product" in t_name.lower()]
        if not product_tables:
            return None

        table = product_tables[0]
        columns = [col.name for col in table.columns]
        name_cols = [c for c in columns if "name" in c.lower() or "title" in c.lower()]

        if query and name_cols:
            like_pattern = f"%{query}%"
            filters = [getattr(table.c, name_cols[0]).like(like_pattern)]
            result = self.db.query(table).filter(*filters).limit(limit).all()
        else:
            result = self.db.query(table).limit(limit).all()

        rows = [{col: getattr(row, col) for col in columns} for row in result]
        return {"columns": columns, "rows": rows, "total": len(rows)}

    def search_orders(self, query: str = "", limit: int = 20):
        if not self._ensure_connection():
            return None
        metadata = get_mystore_metadata()
        tables = metadata.tables

        order_tables = [t for t_name, t in tables.items()
                        if "order" in t_name.lower()]
        if not order_tables:
            return None

        table = order_tables[0]
        columns = [col.name for col in table.columns]

        if query:
            id_cols = [c for c in columns if "id" in c.lower()]
            customer_cols = [c for c in columns if "customer" in c.lower() or "email" in c.lower()]
            filters = []
            if id_cols and query.isdigit():
                filters.append(getattr(table.c, id_cols[0]) == int(query))
            if customer_cols:
                filters.append(getattr(table.c, customer_cols[0]).like(f"%{query}%"))
            if filters:
                from sqlalchemy import or_
                result = self.db.query(table).filter(or_(*filters)).limit(limit).all()
            else:
                result = self.db.query(table).limit(limit).all()
        else:
            result = self.db.query(table).order_by(
                getattr(table.c, list(table.columns)[0]).desc()
            ).limit(limit).all()

        rows = [{col: getattr(row, col) for col in columns} for row in result]
        return {"columns": columns, "rows": rows, "total": len(rows)}

    def is_sql_query(self, text: str) -> bool:
        keywords = ["select", "insert", "update", "delete", "create", "drop", "alter", "show", "describe", "explain", "truncate", "sql:"]
        return any(text.strip().lower().startswith(kw) for kw in keywords)

    def execute_raw_query(self, sql: str):
        if not self._ensure_connection():
            return None
        if not self.is_sql_query(sql):
            return {"error": "Not a valid SQL query. Try: SELECT * FROM products"}
        clean = sql.replace("sql:", "", 1).strip() if sql.lower().startswith("sql:") else sql.strip()
        try:
            result = self.db.execute(text(clean))
            if result.returns_rows:
                columns = list(result.keys())
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                return {"columns": columns, "rows": rows, "total": len(rows)}
            else:
                self.db.commit()
                return {"affected": result.rowcount}
        except Exception as e:
            return {"error": str(e)}

    def process_query(self, query: str) -> str:
        if not is_mystore_configured():
            return "Mystore is not configured. Please set your Mystore database credentials in the .env file."

        if not self._ensure_connection():
            return "Could not connect to Mystore database. Check your credentials."

        q = query.lower()

        if "table" in q or "schema" in q or "structure" in q or "list" in q:
            tables = self.get_tables()
            if not tables:
                return "No tables found in Mystore database."
            return f"Mystore database has {len(tables)} tables: {', '.join(tables)}"

        if "product" in q or "item" in q:
            search_term = q.replace("product", "").replace("search", "").replace("find", "").strip()
            result = self.search_products(search_term)
            if result is None:
                return "No products table found in Mystore."
            if result["total"] == 0:
                return "No products found in Mystore."
            names = []
            for row in result["rows"][:10]:
                name = next((str(row[c]) for c in result["columns"]
                            if "name" in c.lower() or "title" in c.lower() or "product" in c.lower()), str(row))
                names.append(name)
            return f"Found {result['total']} products in Mystore. Latest: {' | '.join(names)}"

        if "order" in q or "purchase" in q:
            result = self.search_orders()
            if result is None:
                return "No orders table found in Mystore."
            if result["total"] == 0:
                return "No orders found in Mystore."
            order_ids = [str(row.get(list(row.keys())[0], "")) for row in result["rows"][:10]]
            return f"Found {result['total']} orders in Mystore. Recent IDs: {', '.join(order_ids)}"

        if "stat" in q or "count" in q or "summary" in q or "overview" in q:
            stats = self.get_store_stats()
            if stats is None:
                return "Could not get Mystore statistics."
            summary = "; ".join([f"{name}: {info['record_count']} records" for name, info in stats.items()])
            return f"Mystore Store Overview: {summary}"

        return ("Mystore Agent: I can query your e-commerce database. Try: "
                "'List Mystore tables', 'Show products', 'Show orders', or 'Store stats'. "
                "You can also run custom SQL queries by starting with 'SQL:'")
