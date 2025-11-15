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

// Add the cron schedule to properties
properties([
    pipelineTriggers([cron('0 8 * * 3')]),  // Runs Wednesday at 8 AM PST
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
                echo "INFO: Checking out ${env.BRANCH_NAME}"
                checkout scm
            }
        }
        
        stage('Install Prerequisites') {
            steps {
                script {
                    installPrereq()
                }
            }
        }
        
        stage('Get Secret and Run Script') {
            steps {
                script {
                    withCredentials([[
                        $class: 'AmazonWebServicesCredentialsBinding',
                        credentialsId: 'aws-credentials',
                        accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                        secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                    ]]) {
                        def SECRET_NAME = 'nso-scheduler-generator'
                        def REGION = 'us-east-1'
                        def JSON_FILE_PATH = 'credentials.json'
                        
                        echo "Getting Service Account Credentials from AWS Secrets Manager"
                        
                        // Fetch secret and write directly to file (preserves all formatting)
                        sh """
                            aws secretsmanager get-secret-value \
                                --secret-id ${SECRET_NAME} \
                                --region ${REGION} \
                                --query SecretString \
                                --output text > ${JSON_FILE_PATH}
                        """
                        
                        def currentDir = pwd()
                        echo "Current Directory: ${currentDir}"
                        
                        // List directory contents
                        sh 'ls -al'
                        
                        // Verify the credentials file exists and is valid JSON
                        sh """
                            if [ ! -f ${JSON_FILE_PATH} ]; then
                                echo "ERROR: ${JSON_FILE_PATH} was not created"
                                exit 1
                            fi
                            
                            if [ ! -s ${JSON_FILE_PATH} ]; then
                                echo "ERROR: ${JSON_FILE_PATH} is empty"
                                exit 1
                            fi
                            
                            # Validate JSON format
                            if python3 -m json.tool ${JSON_FILE_PATH} > /dev/null 2>&1; then
                                echo "Credentials file validated successfully"
                            else
                                echo "ERROR: ${JSON_FILE_PATH} is not valid JSON"
                                exit 1
                            fi
                        """
                        
                        try {
                            echo "Running Python script"
                            createMeeting()
                        } finally {
                            // Clean up sensitive credential file
                            sh "rm -f ${JSON_FILE_PATH}"
                            echo "Cleaned up credentials file"
                        }
                    }
                }
            }
        }
    }
}