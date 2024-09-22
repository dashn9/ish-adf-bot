#!/bin/bash

ENCRYPTION_KEY=$(head -c 32 /dev/urandom | base64)

cd $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

cat > ./configs/gens/encryption-config.yaml <<EOF
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: ${ENCRYPTION_KEY}
      - identity: {}

EOF