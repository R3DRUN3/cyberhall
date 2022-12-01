# INJECT SECRETS INTO A POD WITH THE VAULT AGENT INJECTOR (SIDECAR CONTAINER)

In this demo we will leverage vault agent injector (sidecar) to inject secrets into a pod.
<br/>
<br/>
We will read the secrets from an application running inside the pod (read_secret.py)
<br/>
and we will inspect the pods log to see if the container correctly print the secret value every ten seconds.
<br/>
<br/>
NOTE: To follow this demo you need to complete `demo-1` first.
<br/>
<br/>
As always I will use `minikube` as my local Kubernetes cluster.
<br/>

# Instructions
Start an interactive shell inside `vault-0` pod:  
```console
kubectl exec -n $VAULT_K8S_NAMESPACE -it vault-0 -- /bin/sh
```

<br/>

Enable the `kv` secret engine:  
```console
vault secrets enable -path=secret/ kv
```

<br/>

Lets write a secret to this path:  
```console
vault kv put secret/basic-secret/helloworld username=r3drun3 password=!iS.This-Sec_ur3?_
```

<br/>

Enable K8s Auth method on Vault:  
```console
vault auth enable kubernetes
```
<br/>

Configure K8s auth:  
```console
vault write auth/kubernetes/config \
token_reviewer_jwt="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
kubernetes_host=https://${KUBERNETES_PORT_443_TCP_ADDR}:443 \
kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
issuer="https://kubernetes.default.svc.cluster.local"
```

<br/>

Now we need to create a role and a policy for our app deployment.
<br/>
```console
vault write auth/kubernetes/role/basic-secret-role \
   bound_service_account_names=basic-secret \
   bound_service_account_namespaces=example-app \
   policies=basic-secret-policy \
   ttl=1h
```
<br/>

This will bound the service account of our deployment to a vault read policy.
<br/>

Let's create the vault policy:  
```console
cat <<EOF > /home/vault/app-policy.hcl
path "secret/basic-secret/*" {
  capabilities = ["read"]
}
EOF
vault policy write basic-secret-policy /home/vault/app-policy.hcl
```
<br/>

We can now close the pod's shell:  
```console
exit
```


<br/>
Now is time to deploy our application to Kubernetes!
<br/>

First of all we will create a dedicated kubernetes namespace:  
```console
kubectl create ns example-app
```
<br/>

Now we need to build a docker image for our app, import that image in minikube and start the kubernetes deployment.
<br/>
Before proceding with this part it is recomended to gain familiarity with the following files:  
- *read_secret.py* (the app for which wi will create a container)
- *deployment.yml* (kubernetes deployment manifest)

<br/>

Once you are familiar with these files and understand how the various parts interact with each other,
<br/>
you can launch the deployment with a single command:  
```console
docker build -t r3drun3/read-secret . \
&& minikube image load r3drun3/read-secret:latest \
&& kubectl -n example-app apply -f deployment.yml
```

<br/>

Output Sample:  
```console
[+] Building 1.6s (11/11) FINISHED                                                                                                                                                                        
 => [internal] load build definition from Dockerfile                                                                                                                                                 0.0s
 => => transferring dockerfile: 905B                                                                                                                                                                 0.0s
 => [internal] load .dockerignore                                                                                                                                                                    0.0s
 => => transferring context: 409B                                                                                                                                                                    0.0s
 => [internal] load metadata for docker.io/library/python:3.8-slim                                                                                                                                   1.2s
 => [internal] load build context                                                                                                                                                                    0.0s
 => => transferring context: 1.75kB                                                                                                                                                                  0.0s
 => [1/6] FROM docker.io/library/python:3.8-slim@sha256:c4dabc05d60118d99f9464418b63bc37250d199ab7a153a2e69440c63a04c960                                                                             0.0s
 => CACHED [2/6] COPY requirements.txt .                                                                                                                                                             0.0s
 => CACHED [3/6] RUN python -m pip install -r requirements.txt                                                                                                                                       0.0s
 => CACHED [4/6] WORKDIR /app                                                                                                                                                                        0.0s
 => [5/6] COPY . /app                                                                                                                                                                                0.0s
 => [6/6] RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app                                                                                                        0.3s
 => exporting to image                                                                                                                                                                               0.0s
 => => exporting layers                                                                                                                                                                              0.0s
 => => writing image sha256:1af5a9b0ec96e341fbab06c0360c61fe27278b4f814ac8ef5ecff133362ef967                                                                                                         0.0s
 => => naming to docker.io/r3drun3/read-secret                                                

deployment.apps/basic-secret created
serviceaccount/basic-secret created
```

<br/>

Now inspect the pods in the `example-app` namespace:  
```console
kubectl -n exmple-app get pods

NAME                           READY   STATUS    RESTARTS   AGE
basic-secret-7467b6946-qt9f8   2/2     Running   0          2m35s
```

<br/>

Finally you can inspect the pod's log and you will see our secret!  
```console
kubectl -n example-app logs basic-secret-7467b6946-qt9f8

THE SECRET IS: 
 ['{\n', '  "username" : "r3drun3",\n', '  "password" : "!iS.This-Sec_ur3?_"\n', '}\n']
THE SECRET IS: 
 ['{\n', '  "username" : "r3drun3",\n', '  "password" : "!iS.This-Sec_ur3?_"\n', '}\n']
THE SECRET IS: 
 ['{\n', '  "username" : "r3drun3",\n', '  "password" : "!iS.This-Sec_ur3?_"\n', '}\n']
THE SECRET IS: 
 ['{\n', '  "username" : "r3drun3",\n', '  "password" : "!iS.This-Sec_ur3?_"\n', '}\n']
THE SECRET IS: 
 ['{\n', '  "username" : "r3drun3",\n', '  "password" : "!iS.This-Sec_ur3?_"\n', '}\n']
THE SECRET IS: 
 ['{\n', '  "username" : "r3drun3",\n', '  "password" : "!iS.This-Sec_ur3?_"\n', '}\n']
THE SECRET IS: 
 ['{\n', '  "username" : "r3drun3",\n', '  "password" : "!iS.This-Sec_ur3?_"\n', '}\n']
THE SECRET IS: 
 ['{\n', '  "username" : "r3drun3",\n', '  "password" : "!iS.This-Sec_ur3?_"\n', '}\n']
```

<br/>

Note that the python code write to stdout every ten seconds, that is the reason whny the secret is logged multiple times!

