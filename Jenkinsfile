pipeline {
    agent {
        kubernetes {
            label 'kube-agent'
        }
    }
    environment {
        IMAGE_URL = '531915313382.dkr.ecr.ap-northeast-2.amazonaws.com/biz/iiac-lawlib-api'
        IMAGE_TAG = '0.1.4'
    }
    stages {
        stage('Clone') {
            steps {
                container('jnlp') {
                    checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: '0256052d-c7b0-4d08-add0-8c14889cde47', url: 'https://bitbucket.org/dmk_dev/iiaclaw-web.git']])
                }
            }
        }
        stage("Build & Push Docker Image") {
            steps {
                container('kaniko') {
                    script {
                        sh '/kaniko/executor --context . --dockerfile Dockerfile --destination ${IMAGE_URL}:${IMAGE_TAG}'
                    }
                }
            }
        }
    }
}