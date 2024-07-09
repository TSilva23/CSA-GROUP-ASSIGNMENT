#!/usr/bin/env python3
import os

import aws_cdk as cdk

from my_cdk_app.my_cdk_app_stack import TranslationPipelineStack


app = cdk.App()
TranslationPipelineStack(app, "TranslationPipelineStack")
app.synth()
