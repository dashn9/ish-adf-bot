kubectl create namespace argocd --kubeconfig admin.kubeconfig

kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml --kubeconfig admin.kubeconfig