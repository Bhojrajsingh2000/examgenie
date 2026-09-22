# Prefer the native mysqlclient driver; fall back to PyMySQL (pure-Python,
# no system build tools needed) on hosts like PythonAnywhere where
# mysqlclient may not be pre-installed.
try:
    import MySQLdb  # noqa: F401
except ImportError:
    import pymysql
    pymysql.install_as_MySQLdb()
