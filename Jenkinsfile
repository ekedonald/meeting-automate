properties([
    pipelineTriggers([cron('0 8 * * 3')]),  // Runs Wednesday at 8 am PST
    disableConcurrentBuilds(),
    buildDiscarder(
        logRotator(
            artifactDaysToKeepStr: '',
            artifactNumToKeepStr: '25',
            daysToKeepStr: '',
            numToKeepStr: ''
        )
    )
])

pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                echo("INFO: Checking out ${env.BRANCH_NAME}")
                checkout scm
            }
        }
        
        stage('Setup and Run') {
            steps {
                script {
                    sh """
                        set -e  # Exit on any error
                        
                        # Install dependencies
                        python3 -m venv venv
                        . venv/bin/activate
                        pip install -r requirements.txt
                        
                        # Get secret from AWS and save to credentials.json
                        echo "Fetching secret from AWS Secrets Manager..."
                        aws secretsmanager get-secret-value \
                            --secret-id nso-scheduler-generator \
                            --region us-east-1 \
                            --query SecretString \
                            --output text > credentials.json
                        
                        # Verify credentials file was created and is not empty
                        if [ ! -f credentials.json ]; then
                            echo "ERROR: credentials.json was not created"
                            exit 1
                        fi
                        
                        if [ ! -s credentials.json ]; then
                            echo "ERROR: credentials.json is empty"
                            exit 1
                        fi
                        
                        # Validate JSON format
                        if ! python3 -m json.tool credentials.json > /dev/null 2>&1; then
                            echo "ERROR: credentials.json is not valid JSON"
                            echo "Content of credentials.json:"
                            cat credentials.json
                            exit 1
                        fi
                        
                        echo "Credentials file created and validated successfully"
                        
                        # Run the Python script
                        python3 google_meeting_generator.py
                        
                        # Clean up credentials file
                        rm -f credentials.json
                        echo "Cleaned up credentials file"
                    """
                }
            }
        }
    }
}