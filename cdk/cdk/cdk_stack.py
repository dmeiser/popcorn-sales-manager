from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_iam as iam,
    aws_cognito as cognito,
    aws_appsync as appsync,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_certificatemanager as acm,
)
from constructs import Construct
import os


class CdkStack(Stack):
    """
    Popcorn Sales Manager - Core Infrastructure Stack
    
    Creates foundational resources:
    - DynamoDB table with single-table design
    - S3 buckets for static assets and exports
    - IAM roles for Lambda functions
    - Cognito User Pool for authentication
    - AppSync GraphQL API
    - CloudFront distribution for SPA
    """

    def __init__(
        self, scope: Construct, construct_id: str, env_name: str = "dev", **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.env_name = env_name
        
        # Load configuration from environment variables
        base_domain = os.getenv("BASE_DOMAIN", "psm.repeatersolutions.com")

        # ====================================================================
        # Route 53 & DNS Configuration
        # ====================================================================
        
        # Import existing hosted zone
        self.hosted_zone = route53.HostedZone.from_lookup(
            self,
            "HostedZone",
            domain_name=base_domain,
        )
        
        # Define domain names based on environment
        if env_name == "prod":
            self.site_domain = base_domain
            self.api_domain = f"api.{base_domain}"
            self.cognito_domain = f"login.{base_domain}"
        else:
            self.site_domain = f"{env_name}.{base_domain}"
            self.api_domain = f"api.{env_name}.{base_domain}"
            self.cognito_domain = f"login.{env_name}.{base_domain}"

        # ACM Certificate for custom domains (must be in us-east-1 for CloudFront/Cognito)
        # Note: CloudFront and Cognito custom domains temporarily disabled due to account verification requirement
        # Certificate currently only includes AppSync API domain
        self.certificate = acm.Certificate(
            self,
            "Certificate",
            domain_name=self.api_domain,
            subject_alternative_names=[
                # self.cognito_domain,  # Uncomment when Cognito custom domain is re-enabled
                # self.site_domain,  # Uncomment when CloudFront is re-enabled
            ],
            validation=acm.CertificateValidation.from_dns(self.hosted_zone),
        )

        # ====================================================================
        # DynamoDB Table - Single Table Design
        # ====================================================================
        
        # Check if we should import existing table
        existing_table_name = self.node.try_get_context("table_name")
        if existing_table_name:
            self.table = dynamodb.Table.from_table_name(
                self, "PsmApp", existing_table_name
            )
        else:
            self.table = dynamodb.Table(
                self,
                "PsmApp",
                table_name=f"psm-app-{env_name}",
                partition_key=dynamodb.Attribute(
                    name="PK", type=dynamodb.AttributeType.STRING
                ),
                sort_key=dynamodb.Attribute(
                    name="SK", type=dynamodb.AttributeType.STRING
                ),
                billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
                point_in_time_recovery=True,
                removal_policy=RemovalPolicy.RETAIN,  # Don't delete on stack destroy
                stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,  # For audit logging
            )

            # GSI1: Shares by target account (for "My Shared Profiles" view)
            self.table.add_global_secondary_index(
                index_name="GSI1",
                partition_key=dynamodb.Attribute(
                    name="GSI1PK", type=dynamodb.AttributeType.STRING
                ),
                sort_key=dynamodb.Attribute(
                    name="GSI1SK", type=dynamodb.AttributeType.STRING
                ),
                projection_type=dynamodb.ProjectionType.ALL,
            )

            # GSI2: Orders by profile (for cross-season order queries)
            self.table.add_global_secondary_index(
                index_name="GSI2",
                partition_key=dynamodb.Attribute(
                    name="GSI2PK", type=dynamodb.AttributeType.STRING
                ),
                sort_key=dynamodb.Attribute(
                    name="GSI2SK", type=dynamodb.AttributeType.STRING
                ),
                projection_type=dynamodb.ProjectionType.ALL,
            )

            # GSI3: Catalog ownership and sharing (for catalog management)
            self.table.add_global_secondary_index(
                index_name="GSI3",
                partition_key=dynamodb.Attribute(
                    name="GSI3PK", type=dynamodb.AttributeType.STRING
                ),
                sort_key=dynamodb.Attribute(
                    name="GSI3SK", type=dynamodb.AttributeType.STRING
                ),
                projection_type=dynamodb.ProjectionType.ALL,
            )

        # ====================================================================
        # S3 Buckets
        # ====================================================================

        # Static assets bucket (for SPA hosting)
        # Check if we should import existing bucket
        existing_static_bucket = self.node.try_get_context("static_bucket_name")
        if existing_static_bucket:
            self.static_assets_bucket = s3.Bucket.from_bucket_name(
                self, "StaticAssets", existing_static_bucket
            )
        else:
            self.static_assets_bucket = s3.Bucket(
                self,
                "StaticAssets",
                bucket_name=None,  # Auto-generate name
                versioned=True,
                encryption=s3.BucketEncryption.S3_MANAGED,
                block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                removal_policy=RemovalPolicy.RETAIN,
            )

        # Exports bucket (for generated reports)
        # Check if we should import existing bucket
        existing_exports_bucket = self.node.try_get_context("exports_bucket_name")
        if existing_exports_bucket:
            self.exports_bucket = s3.Bucket.from_bucket_name(
                self, "Exports", existing_exports_bucket
            )
        else:
            self.exports_bucket = s3.Bucket(
                self,
                "Exports",
                bucket_name=None,  # Auto-generate name
                versioned=False,
                encryption=s3.BucketEncryption.S3_MANAGED,
                block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                removal_policy=RemovalPolicy.RETAIN,
            )

        # ====================================================================
        # IAM Roles
        # ====================================================================

        # Lambda execution role (base permissions)
        self.lambda_execution_role = iam.Role(
            self,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        # Grant Lambda role access to DynamoDB table
        self.table.grant_read_write_data(self.lambda_execution_role)

        # Grant Lambda role access to exports bucket
        self.exports_bucket.grant_read_write(self.lambda_execution_role)

        # AppSync service role (for direct DynamoDB resolvers)
        self.appsync_service_role = iam.Role(
            self,
            "AppSyncServiceRole",
            assumed_by=iam.ServicePrincipal("appsync.amazonaws.com"),
        )

        # Grant AppSync role access to DynamoDB table
        self.table.grant_read_write_data(self.appsync_service_role)

        # ====================================================================
        # Cognito User Pool - Authentication (Essentials tier)
        # ====================================================================

        # Check if we should import existing user pool
        existing_user_pool_id = self.node.try_get_context("user_pool_id")
        if existing_user_pool_id:
            self.user_pool = cognito.UserPool.from_user_pool_id(
                self, "UserPool", existing_user_pool_id
            )
            # For imported pools, also get the client if provided
            existing_client_id = self.node.try_get_context("user_pool_client_id")
            if existing_client_id:
                self.user_pool_client = cognito.UserPoolClient.from_user_pool_client_id(
                    self, "AppClient", existing_client_id
                )
        else:
            self.user_pool = cognito.UserPool(
                self,
                "UserPool",
                user_pool_name=f"popcorn-sales-manager-{env_name}",
                sign_in_aliases=cognito.SignInAliases(email=True, username=False),
                self_sign_up_enabled=True,
                auto_verify=cognito.AutoVerifiedAttrs(email=True),
                standard_attributes=cognito.StandardAttributes(
                    email=cognito.StandardAttribute(required=True, mutable=True),
                    given_name=cognito.StandardAttribute(required=False, mutable=True),
                    family_name=cognito.StandardAttribute(required=False, mutable=True),
                ),
                password_policy=cognito.PasswordPolicy(
                    min_length=8,
                    require_lowercase=True,
                    require_uppercase=True,
                    require_digits=True,
                    require_symbols=True,
                ),
                account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
                removal_policy=RemovalPolicy.RETAIN,
                # Note: Advanced security features (Essentials tier) must be configured via CloudFormation properties
            )

            # Note: COPPA compliance warning (13+ age requirement) must be displayed
            # in application UI. Lambda trigger for age verification deferred to later phase.

            # Create user groups
            cognito.CfnUserPoolGroup(
                self,
                "AdminGroup",
                user_pool_id=self.user_pool.user_pool_id,
                group_name="ADMIN",
                description="Administrator users with elevated privileges",
            )

            cognito.CfnUserPoolGroup(
                self,
                "UserGroup",
                user_pool_id=self.user_pool.user_pool_id,
                group_name="USER",
                description="Standard application users",
            )

            # Configure social identity providers (optional - only create if credentials provided)
            supported_providers = [cognito.UserPoolClientIdentityProvider.COGNITO]
            
            # Google OAuth (only if credentials provided)
            if os.environ.get("GOOGLE_CLIENT_ID") and os.environ.get("GOOGLE_CLIENT_SECRET"):
                google_provider = cognito.UserPoolIdentityProviderGoogle(
                    self,
                    "GoogleProvider",
                    user_pool=self.user_pool,
                    client_id=os.environ["GOOGLE_CLIENT_ID"],
                    client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
                    scopes=["email", "profile", "openid"],
                    attribute_mapping=cognito.AttributeMapping(
                        email=cognito.ProviderAttribute.GOOGLE_EMAIL,
                        given_name=cognito.ProviderAttribute.GOOGLE_GIVEN_NAME,
                        family_name=cognito.ProviderAttribute.GOOGLE_FAMILY_NAME,
                    ),
                )
                supported_providers.append(cognito.UserPoolClientIdentityProvider.GOOGLE)

            # Facebook OAuth (only if credentials provided)
            if os.environ.get("FACEBOOK_APP_ID") and os.environ.get("FACEBOOK_APP_SECRET"):
                facebook_provider = cognito.UserPoolIdentityProviderFacebook(
                    self,
                    "FacebookProvider",
                    user_pool=self.user_pool,
                    client_id=os.environ["FACEBOOK_APP_ID"],
                    client_secret=os.environ["FACEBOOK_APP_SECRET"],
                    scopes=["email", "public_profile"],
                    attribute_mapping=cognito.AttributeMapping(
                        email=cognito.ProviderAttribute.FACEBOOK_EMAIL,
                        given_name=cognito.ProviderAttribute.FACEBOOK_FIRST_NAME,
                        family_name=cognito.ProviderAttribute.FACEBOOK_LAST_NAME,
                    ),
                )
                supported_providers.append(cognito.UserPoolClientIdentityProvider.FACEBOOK)

            # Apple Sign In (only if credentials provided)
            if (
                os.environ.get("APPLE_SERVICES_ID")
                and os.environ.get("APPLE_TEAM_ID")
                and os.environ.get("APPLE_KEY_ID")
                and os.environ.get("APPLE_PRIVATE_KEY")
            ):
                apple_provider = cognito.UserPoolIdentityProviderApple(
                    self,
                    "AppleProvider",
                    user_pool=self.user_pool,
                    client_id=os.environ["APPLE_SERVICES_ID"],
                    team_id=os.environ["APPLE_TEAM_ID"],
                    key_id=os.environ["APPLE_KEY_ID"],
                    private_key=os.environ["APPLE_PRIVATE_KEY"],
                    scopes=["email", "name"],
                    attribute_mapping=cognito.AttributeMapping(
                        email=cognito.ProviderAttribute.APPLE_EMAIL,
                        given_name=cognito.ProviderAttribute.APPLE_FIRST_NAME,
                        family_name=cognito.ProviderAttribute.APPLE_LAST_NAME,
                    ),
                )
                supported_providers.append(cognito.UserPoolClientIdentityProvider.APPLE)

            # App client for SPA
            self.user_pool_client = self.user_pool.add_client(
                "AppClient",
                user_pool_client_name="PopcornSalesManager-Web",
                auth_flows=cognito.AuthFlow(
                    user_srp=True,
                    user_password=True,
                ),
                o_auth=cognito.OAuthSettings(
                    flows=cognito.OAuthFlows(
                        authorization_code_grant=True,
                        implicit_code_grant=True,
                    ),
                    scopes=[
                        cognito.OAuthScope.EMAIL,
                        cognito.OAuthScope.OPENID,
                        cognito.OAuthScope.PROFILE,
                    ],
                    callback_urls=[
                        "http://localhost:5173",
                        f"https://{self.site_domain}",
                        f"https://{self.site_domain}/callback",
                    ],
                    logout_urls=[
                        "http://localhost:5173",
                        f"https://{self.site_domain}",
                    ],
                ),
                supported_identity_providers=supported_providers,
                prevent_user_existence_errors=True,
            )

            # Cognito domain temporarily disabled while we fix the configuration
            # The existing managed domain needs to be removed before we can create a new one
            # TODO: Re-enable after cleanup
            # self.user_pool_domain = self.user_pool.add_domain(
            #     "UserPoolDomain",
            #     cognito_domain=cognito.CognitoDomainOptions(
            #         domain_prefix=f"popcorn-sales-manager-{env_name}",
            #     ),
            # )
            
            # TODO: Re-enable custom domain after AWS account verification
            # self.user_pool_domain = self.user_pool.add_domain(
            #     "UserPoolDomain",
            #     custom_domain=cognito.CustomDomainOptions(
            #         domain_name=self.cognito_domain,
            #         certificate=self.certificate,
            #     ),
            # )
            # 
            # # Route53 record for Cognito custom domain
            # route53.ARecord(
            #     self,
            #     "CognitoDomainRecord",
            #     zone=self.hosted_zone,
            #     record_name=self.cognito_domain,
            #     target=route53.RecordTarget.from_alias(
            #         targets.UserPoolDomainTarget(self.user_pool_domain)
            #     ),
            # )

        # ====================================================================
        # AppSync GraphQL API
        # ====================================================================

        # Read GraphQL schema from file
        schema_path = os.path.join(
            os.path.dirname(__file__), "..", "schema", "schema.graphql"
        )

        # Check if we should import existing API
        existing_api_id = self.node.try_get_context("appsync_api_id")
        if existing_api_id:
            self.api = appsync.GraphqlApi.from_graphql_api_attributes(
                self,
                "Api",
                graphql_api_id=existing_api_id,
            )
        else:
            self.api = appsync.GraphqlApi(
                self,
                "Api",
                name=f"popcorn-sales-manager-api-{env_name}",
                definition=appsync.Definition.from_file(schema_path),
                authorization_config=appsync.AuthorizationConfig(
                    default_authorization=appsync.AuthorizationMode(
                        authorization_type=appsync.AuthorizationType.USER_POOL,
                        user_pool_config=appsync.UserPoolConfig(user_pool=self.user_pool),
                    ),
                ),
                xray_enabled=True,
                log_config=appsync.LogConfig(
                    field_log_level=appsync.FieldLogLevel.ALL,
                    exclude_verbose_content=False,
                ),
            )

            # DynamoDB data source
            self.dynamodb_datasource = self.api.add_dynamo_db_data_source(
                "DynamoDBDataSource",
                table=self.table,
            )

            # Custom domain for AppSync API
            self.api_domain_name = appsync.CfnDomainName(
                self,
                "ApiDomainName",
                certificate_arn=self.certificate.certificate_arn,
                domain_name=self.api_domain,
            )

            # Associate custom domain with API
            self.api_domain_association = appsync.CfnDomainNameApiAssociation(
                self,
                "ApiDomainAssociation",
                api_id=self.api.api_id,
                domain_name=self.api_domain_name.attr_domain_name,
            )
            # Ensure domain exists before association
            self.api_domain_association.add_dependency(self.api_domain_name)

            # Route53 record for AppSync custom domain
            route53.CnameRecord(
                self,
                "ApiDomainRecord",
                zone=self.hosted_zone,
                record_name=self.api_domain,
                domain_name=self.api_domain_name.attr_app_sync_domain_name,
            )

        # ====================================================================
        # CloudFront Distribution for SPA
        # ====================================================================
        # TEMPORARILY DISABLED: AWS account needs verification before creating CloudFront resources
        # Error: "Your account must be verified before you can add new CloudFront resources"
        # Action Required: Contact AWS Support to verify account
        # Once verified, uncomment the code below to enable CloudFront with custom domain
        
        # # Origin Access Identity for S3
        # self.origin_access_identity = cloudfront.OriginAccessIdentity(
        #     self, "OAI", comment="OAI for Popcorn Sales Manager SPA"
        # )

        # # Grant CloudFront read access to static assets bucket
        # self.static_assets_bucket.grant_read(self.origin_access_identity)

        # # CloudFront distribution with custom domain
        # self.distribution = cloudfront.Distribution(
        #     self,
        #     "Distribution",
        #     domain_names=[self.site_domain],
        #     certificate=self.certificate,
        #     default_behavior=cloudfront.BehaviorOptions(
        #         origin=origins.S3Origin(
        #             self.static_assets_bucket,
        #             origin_access_identity=self.origin_access_identity,
        #         ),
        #         viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        #         cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
        #         compress=True,
        #     ),
        #     default_root_object="index.html",
        #     error_responses=[
        #         cloudfront.ErrorResponse(
        #             http_status=403,
        #             response_http_status=200,
        #             response_page_path="/index.html",
        #             ttl=Duration.seconds(0),
        #         ),
        #         cloudfront.ErrorResponse(
        #             http_status=404,
        #             response_http_status=200,
        #             response_page_path="/index.html",
        #             ttl=Duration.seconds(0),
        #         ),
        #     ],
        #     price_class=cloudfront.PriceClass.PRICE_CLASS_100,  # US, Canada, Europe only
        #     enabled=True,
        # )

        # # Route53 record for CloudFront distribution
        # route53.ARecord(
        #     self,
        #     "SiteDomainRecord",
        #     zone=self.hosted_zone,
        #     record_name=self.site_domain,
        #     target=route53.RecordTarget.from_alias(
        #         targets.CloudFrontTarget(self.distribution)
        #     ),
        # )


