properties([
    pipelineTriggers([cron('0 8 * * 3')]),
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
                    // Wrap the AWS commands with AWS credentials
                    withCredentials([[
                        $class: 'AmazonWebServicesCredentialsBinding',
                        credentialsId: 'aws-credentials',  // Use the ID you created
                        accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                        secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                    ]]) {
                        sh """
                            set -e
                            
                            # Install dependencies
                            python3 -m venv venv
                            . venv/bin/activate
                            pip install -r requirements.txt
                            
                            # Get secret from AWS (credentials are now available as env vars)
                            echo "Fetching secret from AWS Secrets Manager..."
                            aws secretsmanager get-secret-value \
                                --secret-id nso-scheduler-generator \
                                --region us-east-1 \
                                --query SecretString \
                                --output text > credentials.json
                            
                            # Verify credentials file
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
                                exit 1
                            fi
                            
                            echo "Credentials file validated successfully"
                            
                            # Run the Python script
                            python3 google_meeting_generator.py
                            
                            # Clean up
                            rm -f credentials.json
                            echo "Cleaned up credentials file"
                        """
                    }
                }
            }
        }
    }
}