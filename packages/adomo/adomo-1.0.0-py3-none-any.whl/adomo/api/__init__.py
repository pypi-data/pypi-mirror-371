# flake8: noqa

if __import__("typing").TYPE_CHECKING:
    # import apis into api package
    from adomo.api.activities_api import ActivitiesApi
    from adomo.api.ai_api import AiApi
    from adomo.api.api_service_api import ApiServiceApi
    from adomo.api.auth_api import AuthApi
    from adomo.api.graphql_api import GraphqlApi
    from adomo.api.integrations_api import IntegrationsApi
    from adomo.api.jobs_api import JobsApi
    from adomo.api.schedules_api import SchedulesApi
    from adomo.api.users_api import UsersApi
    from adomo.api.workflows_api import WorkflowsApi


else:
    from lazy_imports import LazyModule, as_package, load

    load(
        LazyModule(
            *as_package(__file__),
            """# import apis into api package
from adomo.api.activities_api import ActivitiesApi
from adomo.api.ai_api import AiApi
from adomo.api.api_service_api import ApiServiceApi
from adomo.api.auth_api import AuthApi
from adomo.api.graphql_api import GraphqlApi
from adomo.api.integrations_api import IntegrationsApi
from adomo.api.jobs_api import JobsApi
from adomo.api.schedules_api import SchedulesApi
from adomo.api.users_api import UsersApi
from adomo.api.workflows_api import WorkflowsApi

""",
            name=__name__,
            doc=__doc__,
        )
    )
