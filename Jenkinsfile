#!groovy

def installPrereq() {
    dir("${WORKSPACE}") {
        sh """
        python3 --version
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
                script {
                    installPrereq()
                }
            }
        }
        
        stage('Get Secret and Run') {
            steps {
                script {
                    // Use your AWS credentials to fetch the secret
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
                        
                        // Fetch secret and parse it
                        def secret = sh(
                            returnStdout: true, 
                            script: """
                                aws secretsmanager get-secret-value \
                                    --secret-id ${SECRET_NAME} \
                                    --region ${REGION} \
                                    | jq -r '.SecretString'
                            """
                        ).trim()
                        
                        def secretJson = readJSON text: secret
                        
                        // Create the service account JSON content
                        def jsonContent = """{
                            "type": "${secretJson.type}",
                            "project_id": "${secretJson.project_id}",
                            "private_key_id": "${secretJson.private_key_id}",
                            "private_key": "${secretJson.private_key}",
                            "client_email": "${secretJson.client_email}",
                            "client_id": "${secretJson.client_id}",
                            "auth_uri": "${secretJson.auth_uri}",
                            "token_uri": "${secretJson.token_uri}",
                            "auth_provider_x509_cert_url": "${secretJson.auth_provider_x509_cert_url}",
                            "client_x509_cert_url": "${secretJson.client_x509_cert_url}"
                        }
                        """
                        
                        // Write the JSON content to a file
                        writeFile file: JSON_FILE_PATH, text: jsonContent
                        
                        def currentDir = pwd()
                        echo "Current Directory: ${currentDir}"
                        
                        // List the contents of the current directory
                        sh 'ls -al'
                        
                        // Verify the credentials file exists and is valid JSON
                        sh 'python3 -m json.tool credentials.json > /dev/null'
                        
                        try {
                            echo "Running Python script"
                            createMeeting()
                        } finally {
                            // Clean up sensitive credential file
                            sh 'rm -f credentials.json'
                            echo "Cleaned up credentials file"
                        }
                    }
                }
            }
        }
    }
}