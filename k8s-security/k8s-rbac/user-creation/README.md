# K8S USER CREATION DEMO

## Instructions:

Create a new private key:  
```console
openssl genrsa -out myuser.key 2048
```

<br/>
Now create a certificate signing request containing the public key and other subject information:  

```console
openssl req -new -key myuser.key -out myuser.csr -subj "/CN=myuser/O=examplegroup"
```

<br/>

You will sign this CSR using the root Kubernetes CA, found in /etc/kubernetes/pki for this example.
<br/>
The file location in your deployment may vary:  
```console
openssl x509 -req -in myuser.csr -CA /etc/kubernetes/pki/ca.crt -CAkey /etc/kubernetes/pki/ca.key -CAcreateserial -out myuser.crt
```

<br/>

NOTE: if you are using *KinD* you can copy the the root Kubernetes CA with the following commands:  
```console
docker cp <kind-copntrol-plane-container-id>:/etc/kubernetes/pki/ca.key . \
&& docker cp <kind-copntrol-plane-container-id>:/etc/kubernetes/pki/ca.crt .
```
<br/>

Now we can create a new clusterrolebinding:  
```console
kubectl create clusterrolebinding examplegroup-admin-binding --clusterrole=cluster-admin --group=examplegroup
```

<br/>

Now register new credentials and config the user context:  
```console
kubectl config set-credentials myuser --client-certificate=myuser.crt --client-key=myuser.key \
&& kubectl config set-context myuser@kubernetes --cluster=kubernetes --user=myuser \
&& kubectl config use-context myuser@kubernetes
```

<br/>

Try to retrieve pods:  
```console
❯ kubectl get pods
NAME        READY     STATUS    RESTARTS   AGE
flask-cap   1/1       Running   0          1m
```




