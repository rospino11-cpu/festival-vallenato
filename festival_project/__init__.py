from django.db.backends.mysql.base import DatabaseWrapper
from django.db.backends.mysql.features import DatabaseFeatures

# 1. Desactivar la validación estricta de versión de MariaDB
DatabaseWrapper.check_database_version_supported = lambda self: None

# 2. Forzar la desactivación de la cláusula RETURNING en las características del backend
DatabaseFeatures.can_return_columns_from_insert = False
DatabaseFeatures.can_return_rows_from_bulk_insert = False