#!/usr/bin/env python3
import os

import aws_cdk as cdk # type: ignore

from cdk_app.cdk_app_stack import CdkAppStack


app = cdk.App()
CdkAppStack(app, "CdkAppStack")

app.synth()
