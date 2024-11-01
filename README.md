### Translation Pipeline Project

#### Overview
This project involves creating a translation pipeline using the AWS Cloud Development Kit (CDK) for Python. The pipeline is capable of handling audio transcription, translation, and text-to-speech synthesis, using various AWS services including S3, Step Functions, Transcribe, Translate, and Polly. The project also incorporates automation and security considerations with EventBridge rules and Lambda functions.

The goal of the project is to automate the process of translating audio files uploaded to an S3 bucket and generate synthesized speech in the target language.

#### Project Structure
The main components of the project are:

- **TranslationPipelineStack**: This is the primary stack, which includes the following AWS resources:
    - **S3 Bucket**: Stores audio files, transcriptions, and translated outputs.
    - **IAM Roles**: Manages permissions for the various services used.
    - **Step Functions State Machine**: Orchestrates the workflow for transcribing, translating, and generating speech.
    - **Lambda Functions**: Used for additional custom operations, including disabling CloudTrail logging.
    - **EventBridge Rule**: Triggers the workflow when a new file is added to the S3 bucket.

#### Setting Up the Project

##### Prerequisites
- Python 3
- AWS CDK (AWS Cloud Development Kit)

##### Installation
1. Clone the repository and navigate to the project directory.
2. Create a virtual environment:
    ```bash
    $ python -m venv .venv
    ```
3. Activate the virtual environment:
    - On MacOS and Linux:
        ```bash
        $ source .venv/bin/activate
        ```
    - On Windows:
        ```bash
        % .venv\Scripts\activate.bat
        ```
4. Install the required dependencies:
    ```bash
    $ pip install -r requirements.txt
    ```

##### Useful Commands
```bash
cdk ls       # List all stacks in the app.
cdk synth    # Synthesize the CloudFormation template for this project.
cdk deploy   # Deploy the stack to your AWS account/region.
cdk diff     # Compare the deployed stack with the current state.
cdk docs     # Open AWS CDK documentation.
```
## Project Workflow
- **Audio Upload**: An audio file is uploaded to the S3 bucket.
- **Event Trigger**: An EventBridge rule triggers the State Machine.
- **Transcription**: AWS Transcribe is used to convert the audio into text.
- **Translation**: AWS Translate translates the text into English (if necessary).
- **Speech Synthesis**: AWS Polly converts the translated text into speech.
- **Storage**: The synthesized audio is saved back to the S3 bucket.

## Future Improvements
- Adding more languages and enhancing translation accuracy.
- Implementing more sophisticated error handling in the State Machine.
- Introducing a web-based UI for users to upload audio files and manage outputs.

## Getting Help
For any questions or issues, please feel free to open an issue in the repository or contact me directly.

## License
This project is licensed under the MIT License.


