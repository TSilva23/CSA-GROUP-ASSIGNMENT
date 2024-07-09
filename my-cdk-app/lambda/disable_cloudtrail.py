import boto3

def handler(event, context):
    cloudtrail = boto3.client('cloudtrail')

    if event['RequestType'] == 'Create' or event['RequestType'] == 'Update':
        # List existing trails
        trails = cloudtrail.describe_trails()['trailList']
        for trail in trails:
            # Stop logging for each trail
            cloudtrail.stop_logging(Name=trail['Name'])
            # Delete the trail
            cloudtrail.delete_trail(Name=trail['Name'])
        
        response_data = {"Status": "CloudTrail logging stopped and trails deleted"}
        return response_data

    elif event['RequestType'] == 'Delete':
        # No action needed on stack deletion
        response_data = {"Status": "No action needed on delete"}
        return response_data
