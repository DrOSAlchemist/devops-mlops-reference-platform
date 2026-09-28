pipeline {
  agent {
    docker {
      image 'python:3.12-slim'
      args '-u root'
    }
  }
  options {
    timestamps()
    disableConcurrentBuilds()
  }
  stages {
    stage('Install') {
      steps {
        sh 'python -m pip install --upgrade pip setuptools'
        sh "python -m pip install -e '.[dev]'"
      }
    }
    stage('Verify') {
      steps {
        sh 'ruff check .'
        sh 'pytest -q'
      }
    }
    stage('Security') {
      steps {
        sh 'pip-audit --skip-editable'
        sh 'bandit -q -r src/platform_guard'
      }
    }
  }
  post {
    always {
      junit testResults: 'junit.xml', allowEmptyResults: true
    }
  }
}