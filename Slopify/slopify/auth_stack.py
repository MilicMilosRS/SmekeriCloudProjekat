from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_cognito as cognito,
    CfnOutput
)
from constructs import Construct

class AuthStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.user_pool = cognito.UserPool(
            self, "SlopifyUserPool",
            user_pool_name="SlopifyUserPool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(username=True, email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            standard_attributes=cognito.StandardAttributes(
                given_name=cognito.StandardAttribute(required=True, mutable=True),
                family_name=cognito.StandardAttribute(required=True, mutable=True),
                birthdate=cognito.StandardAttribute(required=True, mutable=True),
                ),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False
                ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY
            )

        self.user_pool_client = cognito.UserPoolClient(
            self, "UserPoolClient",
            user_pool=self.user_pool
        )

        # Groups
        cognito.CfnUserPoolGroup(
            self, "AdminsGroup",
            user_pool_id=self.user_pool.user_pool_id,
            group_name="admins"
        )

        cognito.CfnUserPoolGroup(
            self, "UsersGroup",
            user_pool_id=self.user_pool.user_pool_id,
            group_name="users"
        )

        # Lambda Triggers
        pre_sign_up = _lambda.Function(
            self, "PreSignUpHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/auth"),
            handler="pre_sign_up.handle"
        )

        pre_sign_up.add_to_role_policy(iam.PolicyStatement(
            actions=[
                "cognito-idp:ListUsers"
            ],
            resources=[f"*"]
        ))

        post_confirmation = _lambda.Function(
            self, "PostConfirmationHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("lambda/auth"),
            handler="post_confirmation.handle"
        )

        post_confirmation.add_to_role_policy(
            iam.PolicyStatement(
                actions=["cognito-idp:AdminAddUserToGroup"],
                resources=[f"*"]
                )
            )

        self.user_pool.add_trigger(cognito.UserPoolOperation.PRE_SIGN_UP, pre_sign_up )
        self.user_pool.add_trigger(cognito.UserPoolOperation.POST_CONFIRMATION, post_confirmation )

        CfnOutput(self, "UserPoolId", value=self.user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=self.user_pool_client.user_pool_client_id)
