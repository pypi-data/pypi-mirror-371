
# flake8: noqa

# Import all APIs into this package.
# If you have many APIs here with many many models used in each API this may
# raise a `RecursionError`.
# In order to avoid this, import only the API that you directly need like:
#
#   from .api.entity_match_api import EntityMatchApi
#
# or import this package, but before doing it, use:
#
#   import sys
#   sys.setrecursionlimit(n)

# Import APIs into API package:
from fds.sdk.FactSetConcordance.api.entity_match_api import EntityMatchApi
from fds.sdk.FactSetConcordance.api.entity_match___bulk_api import EntityMatchBulkApi
from fds.sdk.FactSetConcordance.api.mappings_api import MappingsApi
from fds.sdk.FactSetConcordance.api.people_mapping_api import PeopleMappingApi
from fds.sdk.FactSetConcordance.api.people_match_api import PeopleMatchApi
from fds.sdk.FactSetConcordance.api.people_match___bulk_api import PeopleMatchBulkApi
from fds.sdk.FactSetConcordance.api.snowflake_api import SnowflakeApi
from fds.sdk.FactSetConcordance.api.universes_api import UniversesApi
