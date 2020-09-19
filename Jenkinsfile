node("master") {
  timestamps {
    git branch: 'master',
        credentialsId: 'd7fe903f-1cdc-49e1-8031-a8ff56173796',
        url: 'git@github.com:luizatebesoi/restaurant-reviews.git'
    def GIT_TAG = gitTagName()
    properties([
        buildDiscarder(logRotator(daysToKeepStr: '14', numToKeepStr: '3')),
    ])
    stage('DockerHub registry login') {
      withCredentials([usernamePassword(credentialsId: '052cba25-f00d-4ff2-b593-4e143b90515a', usernameVariable: 'dockerhub_user', passwordVariable: 'dockerhub_password')]) {
        sh "docker login -u ${dockerhub_user} -p ${dockerhub_password}"
      }
    }
    stage('Build image') {
      sh "docker image build -f Dockerfile -t paulcosma/com-tebesoi-restaurants:${GIT_TAG} ."
    }
    stage('Tag image as latest') {
      sh "docker image tag paulcosma/com-tebesoi-restaurants:${GIT_TAG} paulcosma/com-tebesoi-restaurants:latest"
    }
    stage('Push image') {
      sh "docker image push paulcosma/com-tebesoi-restaurants:${GIT_TAG}"
      sh "docker image push paulcosma/com-tebesoi-restaurants:latest"
    }
    stage('Start deployments') {
      parallel(
          websites: {
            build job: 'DEPLOY-websites-stack'
          },
          apps: {
            build job: 'DEPLOY-apps-stack'
          }
      )
    }
  }
}

String gitTagName() {
  commit = getLatestTaggedCommit()
  sh "echo Debug: commit = $commit"
  if (commit) {
    desc = sh(script: "git describe --tags ${commit}", returnStdout: true)?.trim()
    sh "echo Debug: Tag = $desc"
  }
  return desc
}

String getLatestTaggedCommit() {
  return sh(script: 'git rev-list --tags --max-count=1', returnStdout: true)?.trim()
}