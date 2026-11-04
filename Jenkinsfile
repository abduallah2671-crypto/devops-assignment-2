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
    stage('Resolve push sender') {
      steps {
        script {
          env.PUSHER_EMAIL = sh(script: 'cat "/var/lib/jenkins/assignment-pushers/${GIT_COMMIT}.email"', returnStdout: true).trim()
          if (!env.PUSHER_EMAIL) { error('No push sender email was captured from the GitHub webhook') }
        }
      }
    }
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
      script {
        if (env.PUSHER_EMAIL) {
          emailext(to: env.PUSHER_EMAIL, from: 'abduallah2671@gmail.com',
            subject: "${JOB_NAME} #${BUILD_NUMBER}: ${currentBuild.currentResult}",
            body: "Result: ${currentBuild.currentResult}\nBuild: ${BUILD_URL}\nCommit: ${GIT_COMMIT}")
        } else {
          echo 'Email not sent because the webhook push sender address is unavailable'
        }
      }
    }
  }
}
