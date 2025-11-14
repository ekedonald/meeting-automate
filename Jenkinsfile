#!groovy

def installPrereq() {
    dir("${WORKSPACE}") {
        sh """
        python3 --version
        python3 -m venv venv
        . venv/bin/activate
        pip install -r requirements.txt
        """
    }
}

def createMeeting() {
  dir("${WORKSPACE}") {
      sh """
python3 google_meeting_generator.py
"""
  }
}

// Add the cron schedule to properties.
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

        stage('Install Pre Reqs') {
            steps {
                installPrereq()
            }
        }

        stage('Get secret from AWS') {
            steps {
                script {
                    echo "Getting Secrets from AWS Secrets Manager"
                    def JSON_FILE_PATH = 'credentials.json'
                    
                    def secret = sh(
                        returnStdout: true, 
                        script: "aws secretsmanager get-secret-value --secret-id nso-scheduler-generator --region us-east-1 | jq -r '.SecretString'"
                    ).trim()
            
                    def secretJson = readJSON text: secret

                    // Directly access the attributes from the JSON response
                    env.type = secretJson.type
                    env.project_id = secretJson.project_id
                    env.private_key_id = secretJson.private_key_id
                    env.private_key = secretJson.private_key
                    env.client_email = secretJson.client_email
                    env.client_id = secretJson.client_id
                    env.auth_uri = secretJson.auth_uri
                    env.token_uri = secretJson.token_uri
                    env.auth_provider_x509_cert_url = secretJson.auth_provider_x509_cert_url
                    env.client_x509_cert_url = secretJson.client_x509_cert_url

                    // Create the JSON content
                    def jsonContent = """
                    {
                        "type": "${env.type}",
                        "project_id": "${env.project_id}",
                        "private_key_id": "${env.private_key_id}",
                        "private_key": "${env.private_key}",
                        "client_email": "${env.client_email}",
                        "client_id": "${env.client_id}",
                        "auth_uri": "${env.auth_uri}",
                        "token_uri": "${env.token_uri}",
                        "auth_provider_x509_cert_url": "${env.auth_provider_x509_cert_url}",
                        "client_x509_cert_url": "${env.client_x509_cert_url}"
                    }
                    """

                    // Write the JSON content to a file
                    writeFile file: "${JSON_FILE_PATH}", text: jsonContent
                    
                    echo "Credentials file created"
                    
                    // Verify the credentials file exists and is valid JSON
                    sh 'python3 -m json.tool credentials.json > /dev/null && echo "Credentials file is valid JSON"'
                }
            }
        }

        stage('Run Script') {
            steps {
                script {
                    try {
                        echo("Running python script to create calendar event")
                        createMeeting()
                        
                        // Clean up sensitive credential file on success
                        sh 'rm -f credentials.json'
                        echo "Cleaned up credentials file"

                    } catch (Exception e) {
                        currentBuild.result = 'FAILURE'
                        throw e
                    }
                }
            }
        }
    }
}