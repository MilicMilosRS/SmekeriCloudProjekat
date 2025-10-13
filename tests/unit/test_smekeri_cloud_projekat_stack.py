import aws_cdk as core
import aws_cdk.assertions as assertions

from smekeri_cloud_projekat.smekeri_cloud_projekat_stack import SmekeriCloudProjekatStack

# example tests. To run these tests, uncomment this file along with the example
# resource in smekeri_cloud_projekat/smekeri_cloud_projekat_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SmekeriCloudProjekatStack(app, "smekeri-cloud-projekat")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
