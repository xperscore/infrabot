pipeline {
  agent {
    label "jenkins-python"
  }
  environment {
    ORG = 'xperscore'
    APP_NAME = 'infrabot'
    CHARTMUSEUM_CREDS = credentials('jenkins-x-chartmuseum')
  }
  stages {
    stage('Build Release') {
      when {
        branch 'master'
      }
      steps {
        container('python') {
          // ensure we're not on a detached head
          sh "git checkout master"
          sh "git config --global credential.helper store"
          sh "jx step git credentials"

          // so we can retrieve the version in later steps
          sh "echo \$(jx-release-version) > VERSION"
          sh "jx step tag --version \$(cat VERSION)"
          sh "export VERSION=`cat VERSION` && skaffold build -f skaffold.yaml"
          sh "jx step post build --image $DOCKER_REGISTRY/$ORG/$APP_NAME:\$(cat VERSION)"
        }
      }
    }
    stage('Promote to Environments') {
      when {
        branch 'master'
      }
      steps {
        container('python') {
          dir('./charts/infrabot') {
            sh "jx step changelog --version v\$(cat ../../VERSION)"

            // release the helm chart
            sh "jx step helm release"

            // promote through all 'Auto' promotion Environments
            sh "jx promote -b ---env production --timeout 1h --version \$(cat ../../VERSION) --verbose"
          }
        }
      }
    }
  }
  post {
        always {
          cleanWs()
        }
  }
}
