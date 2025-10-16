import aws_cdk as core
import aws_cdk.assertions as assertions

from slopify.slopify_stack import SlopifyStack

# example tests. To run these tests, uncomment this file along with the example
# resource in slopify/slopify_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SlopifyStack(app, "slopify")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
