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
            . venv/bin/activate
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
                        def secret = sh(
                            returnStdout: true,
                            script: """
                                aws secretsmanager get-secret-value \
                                    --secret-id ${SECRET_NAME} \
                                    --region ${REGION} \
                                    | jq -r '.SecretString'
                            """
                        ).trim()
                        
                        // Write the secret directly to file
                        writeFile file: JSON_FILE_PATH, text: secret
                        
                        def currentDir = pwd()
                        echo "Current Directory: ${currentDir}"
                        
                        // List directory contents
                        sh 'ls -al'

                        def filePath = 'credentials.json'
                        def fileContents = readFile(filePath)
                        
                        
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