from aws_cdk import (
    aws_s3 as s3,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda as _lambda,
    custom_resources as cr,
    aws_logs as logs,
    App, Stack, Duration
)
from constructs import Construct

class TranslationPipelineStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # S3 Bucket
        bucket = s3.Bucket(self, "TranslationBucket", versioned=True)

        # IAM Role for Step Functions
        role = iam.Role(self, "StepFunctionsRole",
                        assumed_by=iam.ServicePrincipal("states.amazonaws.com"))

        # Grant necessary permissions to the role
        bucket.grant_read_write(role)
        role.add_to_policy(iam.PolicyStatement(
            actions=[
                "transcribe:StartTranscriptionJob",
                "transcribe:GetTranscriptionJob",
                "translate:TranslateText",
                "polly:SynthesizeSpeech"
            ],
            resources=["*"]
        ))

        # Step Functions Tasks
        transcribe_task = tasks.CallAwsService(self, "Transcribe Audio",
                                               service="transcribe",
                                               action="startTranscriptionJob",
                                               parameters={
                                                   "TranscriptionJobName": "transcriptionJob",
                                                   "LanguageCode": "auto",
                                                   "Media": {
                                                       "MediaFileUri": sfn.JsonPath.string_at("$.detail.bucket.name"),
                                                   },
                                                   "OutputBucketName": bucket.bucket_name,
                                                   "OutputKey": "transcriptions/output.json"
                                               },
                                               iam_resources=["*"])

        get_transcription_task = tasks.CallAwsService(self, "Get Transcription",
                                                      service="transcribe",
                                                      action="getTranscriptionJob",
                                                      parameters={
                                                          "TranscriptionJobName": sfn.JsonPath.string_at("$.TranscriptionJob.TranscriptionJobName")
                                                      },
                                                      iam_resources=["*"])

        check_language_task = sfn.Choice(self, "Check Language")
        is_english = sfn.Condition.string_equals("$.TranscriptionJob.LanguageCode", "en")

        translate_task = tasks.CallAwsService(self, "Translate Text",
                                              service="translate",
                                              action="translateText",
                                              parameters={
                                                  "Text": sfn.JsonPath.string_at("$.transcription.result"),
                                                  "SourceLanguageCode": sfn.JsonPath.string_at("$.TranscriptionJob.LanguageCode"),
                                                  "TargetLanguageCode": "en"
                                              },
                                              iam_resources=["*"])

        polly_task = tasks.CallAwsService(self, "Generate Speech",
                                          service="polly",
                                          action="synthesizeSpeech",
                                          parameters={
                                              "OutputFormat": "mp3",
                                              "Text": sfn.JsonPath.string_at("$.translated.text"),
                                              "VoiceId": "Joanna"
                                          },
                                          iam_resources=["*"])

        # Task to save Polly output to S3
        save_to_s3_task = tasks.CallAwsService(self, "Save to S3",
                                               service="s3",
                                               action="putObject",
                                               parameters={
                                                   "Bucket": bucket.bucket_name,
                                                   "Key": sfn.JsonPath.string_at("$.translated.key"),
                                                   "Body": sfn.JsonPath.string_at("$.translated.mp3")
                                               },
                                               iam_resources=[bucket.bucket_arn])

        # Define workflow
        definition = transcribe_task \
            .next(get_transcription_task) \
            .next(check_language_task
                  .when(is_english, sfn.Pass(self, "Already in English"))
                  .otherwise(translate_task.next(polly_task).next(save_to_s3_task)))

        # Step Functions State Machine
        state_machine = sfn.StateMachine(self, "StateMachine",
                                         definition_body=sfn.DefinitionBody.from_chainable(definition),
                                         role=role)

        # EventBridge Rule
        rule = events.Rule(self, "Rule",
                           event_pattern={
                               "source": ["aws.s3"],
                               "detail": {
                                   "eventName": ["PutObject"]
                               }
                           })

        rule.add_target(targets.SfnStateMachine(state_machine))

        # Lambda Function to disable CloudTrail
        disable_cloudtrail_lambda = _lambda.Function(self, "DisableCloudTrailFunction",
                                                     runtime=_lambda.Runtime.PYTHON_3_8,
                                                     handler="disable_cloudtrail.handler",
                                                     code=_lambda.Code.from_asset("lambda"),
                                                     environment={
                                                         "TRAIL_NAME": "YourTrailName"  # specify your trail name here
                                                     },
                                                     log_retention=logs.RetentionDays.ONE_DAY,
                                                     timeout=Duration.minutes(5))

        # IAM Policy for Lambda to disable CloudTrail
        disable_cloudtrail_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudtrail:StopLogging", "cloudtrail:DeleteTrail"],
            resources=["*"]
        ))

        # Custom Resource to invoke the Lambda Function
        provider = cr.Provider(self, "CustomResourceProvider",
                               on_event_handler=disable_cloudtrail_lambda)

        custom_resource = cr.AwsCustomResource(self, "DisableCloudTrailCustomResource",
                                               on_create=cr.AwsSdkCall(
                                                   service="CloudTrail",
                                                   action="stopLogging",
                                                   parameters={
                                                       "Name": "YourTrailName"  # specify your trail name here
                                                   },
                                                   physical_resource_id=cr.PhysicalResourceId.of("DisableCloudTrailCustomResource")
                                               ),
                                               policy=cr.AwsCustomResourcePolicy.from_statements([
                                                   iam.PolicyStatement(
                                                       actions=["cloudtrail:StopLogging", "cloudtrail:DeleteTrail"],
                                                       resources=["*"]
                                                   )
                                               ]))

app = App()
TranslationPipelineStack(app, "TranslationPipelineStack")
app.synth()