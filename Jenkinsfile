pipeline {
  agent { label 'docker' }
  options { disableConcurrentBuilds(); timestamps(); timeout(time: 5, unit: 'MINUTES') }
  triggers { githubPush() }
  environment {
    DB_PASSWORD = credentials('assignment-db-password')
    SOURCE_DIR = "${WORKSPACE}"
  }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Validate in Docker') {
      steps {
        script {
          docker.image('python:3.12-slim').inside {
            sh 'python -m py_compile app.py'
          }
        }
      }
    }
    stage('Start Part II') {
      steps {
        sh 'docker compose -f docker-compose.ci.yml up -d --wait --wait-timeout 90'
        sh '''for i in $(seq 1 60); do
          if curl --fail --silent http://localhost:8082/health; then exit 0; fi
          sleep 2
        done
        exit 1'''
      }
    }
  }
  post {
    always {
      emailext(subject: "${JOB_NAME} #${BUILD_NUMBER}: ${currentBuild.currentResult}",
        body: "Result: ${currentBuild.currentResult}\nBuild: ${BUILD_URL}",
        recipientProviders: [developers(), requestor()])
    }
  }
}
