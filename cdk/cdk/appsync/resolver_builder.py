"""
Builder pattern for AppSync resolvers.

Simplifies creation of different resolver types (VTL, JS, Pipeline, Lambda).
Reduces boilerplate and ensures consistent patterns across resolvers.
"""

from pathlib import Path
from typing import Any

from aws_cdk import aws_appsync as appsync
from constructs import Construct


class ResolverBuilder:
    """
    Fluent builder for AppSync resolvers.

    Provides methods for creating different resolver types:
    - VTL resolvers (request/response mapping templates)
    - JavaScript resolvers (AppSync JS runtime)
    - Pipeline resolvers (multi-step with functions)
    - Lambda resolvers (delegating to Lambda data source)

    Example:
        builder = ResolverBuilder(api, datasources, lambda_datasources, scope)

        # Create a VTL resolver
        builder.create_vtl_resolver(
            field_name="getMyAccount",
            type_name="Query",
            datasource_name="accounts",
            request_template=MAPPING_TEMPLATES_DIR / "get_my_account_request.vtl",
            response_template=MAPPING_TEMPLATES_DIR / "get_my_account_response.vtl",
        )

        # Create a JS resolver
        builder.create_js_resolver(
            field_name="listMyProfiles",
            type_name="Query",
            datasource_name="profiles",
            code_file=RESOLVERS_DIR / "list_my_profiles_fn.js",
        )
    """

    def __init__(
        self,
        api: appsync.GraphqlApi,
        datasources: dict[str, Any],
        lambda_datasources: dict[str, appsync.LambdaDataSource],
        scope: Construct,
    ):
        """
        Initialize the resolver builder.

        Args:
            api: AppSync GraphQL API
            datasources: Dictionary of AppSync data sources (keyed by name)
            lambda_datasources: Dictionary of Lambda data sources (keyed by name)
            scope: CDK construct scope for creating resources
        """
        self.api = api
        self.datasources = datasources
        self.lambda_datasources = lambda_datasources
        self.scope = scope

    def create_vtl_resolver(
        self,
        field_name: str,
        type_name: str,
        datasource_name: str,
        request_template: Path,
        response_template: Path,
        id_suffix: str | None = None,
    ) -> appsync.Resolver:
        """
        Create a VTL resolver with request/response mapping templates.

        Args:
            field_name: GraphQL field name (e.g., "getMyAccount")
            type_name: GraphQL type name (e.g., "Query", "Mutation", "Campaign")
            datasource_name: Key in datasources dict (e.g., "accounts")
            request_template: Path to request VTL template file
            response_template: Path to response VTL template file
            id_suffix: Optional custom CDK construct ID suffix

        Returns:
            The created resolver
        """
        resolver_id = id_suffix or f"{field_name}Resolver"

        datasource = self.datasources[datasource_name]
        resolver: appsync.Resolver = datasource.create_resolver(
            resolver_id,
            type_name=type_name,
            field_name=field_name,
            request_mapping_template=appsync.MappingTemplate.from_file(str(request_template)),
            response_mapping_template=appsync.MappingTemplate.from_file(str(response_template)),
        )
        return resolver

    def create_js_resolver(
        self,
        field_name: str,
        type_name: str,
        datasource_name: str,
        code_file: Path,
        id_suffix: str | None = None,
    ) -> appsync.Resolver:
        """
        Create a JavaScript resolver using AppSync JS runtime.

        Args:
            field_name: GraphQL field name
            type_name: GraphQL type name
            datasource_name: Key in datasources dict
            code_file: Path to JavaScript resolver code file
            id_suffix: Optional custom CDK construct ID suffix

        Returns:
            The created resolver
        """
        resolver_id = id_suffix or f"{field_name}Resolver"

        datasource = self.datasources[datasource_name]
        resolver: appsync.Resolver = datasource.create_resolver(
            resolver_id,
            type_name=type_name,
            field_name=field_name,
            runtime=appsync.FunctionRuntime.JS_1_0_0,
            code=appsync.Code.from_asset(str(code_file)),
        )
        return resolver

    def create_js_resolver_on_api(
        self,
        field_name: str,
        type_name: str,
        datasource_name: str,
        code_file: Path,
        id_suffix: str | None = None,
    ) -> appsync.Resolver:
        """
        Create a JS resolver via api.create_resolver() with explicit data_source.

        Some resolvers are created via api.create_resolver() instead of
        datasource.create_resolver(). This method handles that pattern.

        Args:
            field_name: GraphQL field name
            type_name: GraphQL type name
            datasource_name: Key in datasources dict
            code_file: Path to JavaScript resolver code file
            id_suffix: Optional custom CDK construct ID suffix

        Returns:
            The created resolver
        """
        resolver_id = id_suffix or f"{field_name}Resolver"

        datasource = self.datasources[datasource_name]
        return self.api.create_resolver(
            resolver_id,
            type_name=type_name,
            field_name=field_name,
            data_source=datasource,
            runtime=appsync.FunctionRuntime.JS_1_0_0,
            code=appsync.Code.from_asset(str(code_file)),
        )

    def create_pipeline_resolver(
        self,
        field_name: str,
        type_name: str,
        functions: list[appsync.AppsyncFunction],
        code_file: Path,
        id_suffix: str | None = None,
    ) -> appsync.Resolver:
        """
        Create a pipeline resolver with multiple functions.

        Args:
            field_name: GraphQL field name
            type_name: GraphQL type name
            functions: List of AppsyncFunction objects to execute in order
            code_file: Path to pipeline orchestration JavaScript file
            id_suffix: Optional custom CDK construct ID suffix

        Returns:
            The created resolver
        """
        resolver_id = id_suffix or f"{field_name}PipelineResolver"

        return self.api.create_resolver(
            resolver_id,
            type_name=type_name,
            field_name=field_name,
            runtime=appsync.FunctionRuntime.JS_1_0_0,
            pipeline_config=functions,
            code=appsync.Code.from_asset(str(code_file)),
        )

    def create_pipeline_resolver_on_scope(
        self,
        field_name: str,
        type_name: str,
        functions: list[appsync.AppsyncFunction],
        code_file: Path,
        id_suffix: str | None = None,
    ) -> appsync.Resolver:
        """
        Create a pipeline resolver with multiple functions, using scope as parent.

        This method uses appsync.Resolver(scope, ...) instead of api.create_resolver()
        to maintain backwards compatibility with existing CloudFormation resources
        that don't have the 'Api' prefix in their logical IDs.

        Use this ONLY for resolvers that were originally created before the
        ResolverBuilder migration (e.g., DeleteCatalogPipelineResolver,
        ListInvitesByProfilePipelineResolver).

        Args:
            field_name: GraphQL field name
            type_name: GraphQL type name
            functions: List of AppsyncFunction objects to execute in order
            code_file: Path to pipeline orchestration JavaScript file
            id_suffix: Optional custom CDK construct ID suffix

        Returns:
            The created resolver
        """
        resolver_id = id_suffix or f"{field_name}PipelineResolver"

        return appsync.Resolver(
            self.scope,
            resolver_id,
            api=self.api,
            type_name=type_name,
            field_name=field_name,
            runtime=appsync.FunctionRuntime.JS_1_0_0,
            pipeline_config=functions,
            code=appsync.Code.from_asset(str(code_file)),
        )

    def create_vtl_pipeline_resolver(
        self,
        field_name: str,
        type_name: str,
        functions: list[appsync.AppsyncFunction],
        request_template: Path,
        response_template: Path,
        id_suffix: str | None = None,
    ) -> appsync.Resolver:
        """
        Create a VTL-style pipeline resolver using appsync.Resolver construct.

        Some older resolvers use VTL templates with pipeline_config.
        This pattern uses the Resolver construct directly.

        Args:
            field_name: GraphQL field name
            type_name: GraphQL type name
            functions: List of AppsyncFunction objects to execute in order
            request_template: Path to request VTL template file
            response_template: Path to response VTL template file
            id_suffix: Optional custom CDK construct ID suffix

        Returns:
            The created resolver
        """
        resolver_id = id_suffix or f"{field_name}Resolver"

        return appsync.Resolver(
            self.scope,
            resolver_id,
            api=self.api,
            type_name=type_name,
            field_name=field_name,
            request_mapping_template=appsync.MappingTemplate.from_file(str(request_template)),
            response_mapping_template=appsync.MappingTemplate.from_file(str(response_template)),
            pipeline_config=functions,
        )

    def create_lambda_resolver(
        self,
        field_name: str,
        type_name: str,
        lambda_datasource_name: str,
        id_suffix: str | None = None,
    ) -> appsync.Resolver:
        """
        Create a Lambda resolver.

        Args:
            field_name: GraphQL field name
            type_name: GraphQL type name
            lambda_datasource_name: Key in lambda_datasources dict
            id_suffix: Optional custom CDK construct ID suffix

        Returns:
            The created resolver
        """
        resolver_id = id_suffix or f"{field_name}Resolver"

        lambda_ds = self.lambda_datasources[lambda_datasource_name]
        return lambda_ds.create_resolver(
            resolver_id,
            type_name=type_name,
            field_name=field_name,
        )

    def create_batch_resolvers(
        self,
        resolvers: list[dict[str, Any]],
    ) -> list[appsync.Resolver]:
        """
        Create multiple resolvers from a configuration list.

        This is useful for creating many similar resolvers (e.g., field resolvers)
        from a declarative configuration.

        Args:
            resolvers: List of resolver configurations, each containing:
                - type: "vtl", "js", "pipeline", "lambda"
                - field_name: GraphQL field name
                - type_name: GraphQL type name
                - datasource_name: (for vtl, js) Key in datasources dict
                - lambda_datasource_name: (for lambda) Key in lambda_datasources dict
                - request_template: (for vtl) Path to request template
                - response_template: (for vtl) Path to response template
                - code_file: (for js, pipeline) Path to JS code file
                - functions: (for pipeline) List of AppsyncFunction objects
                - id_suffix: (optional) Custom CDK construct ID

        Returns:
            List of created resolvers
        """
        created = []
        for config in resolvers:
            resolver_type = config["type"]

            if resolver_type == "vtl":
                resolver = self.create_vtl_resolver(
                    field_name=config["field_name"],
                    type_name=config["type_name"],
                    datasource_name=config["datasource_name"],
                    request_template=config["request_template"],
                    response_template=config["response_template"],
                    id_suffix=config.get("id_suffix"),
                )
            elif resolver_type == "js":
                resolver = self.create_js_resolver(
                    field_name=config["field_name"],
                    type_name=config["type_name"],
                    datasource_name=config["datasource_name"],
                    code_file=config["code_file"],
                    id_suffix=config.get("id_suffix"),
                )
            elif resolver_type == "js_on_api":
                resolver = self.create_js_resolver_on_api(
                    field_name=config["field_name"],
                    type_name=config["type_name"],
                    datasource_name=config["datasource_name"],
                    code_file=config["code_file"],
                    id_suffix=config.get("id_suffix"),
                )
            elif resolver_type == "pipeline":
                resolver = self.create_pipeline_resolver(
                    field_name=config["field_name"],
                    type_name=config["type_name"],
                    functions=config["functions"],
                    code_file=config["code_file"],
                    id_suffix=config.get("id_suffix"),
                )
            elif resolver_type == "lambda":
                resolver = self.create_lambda_resolver(
                    field_name=config["field_name"],
                    type_name=config["type_name"],
                    lambda_datasource_name=config["lambda_datasource_name"],
                    id_suffix=config.get("id_suffix"),
                )
            else:
                raise ValueError(f"Unknown resolver type: {resolver_type}")

            created.append(resolver)

        return created
