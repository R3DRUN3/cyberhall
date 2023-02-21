# K8S SERVICE ACCOUNT CREATION DEMO

## Instructions:

Apply the *flask.yaml* manifest, this will create a serviceAccount (“flask backend”), a Role that grants some permissions over the other pods in this “flask” 
<br/>
namespace, a RoleBinding associating the serviceAccount and the Role and finally, a deployment of pods that will use the serviceAccount:  
```console
kubectl apply -f flask.yaml
```

<br/>

If you query the secrets for the flask namespace, you can verify that an API access token was automatically created for your serviceAccount:  
```console
kubectl get secrets -n flask
```

<br/>

check that the permissions are working as expected with the kubectl auth command that can query access for verbs and subjects, as well as impersonate other accounts:  
```console
kubectl auth can-i list pods -n default --as=system:serviceaccount:flask:flask-backend

no
```
<br/>

```console
kubectl auth can-i list pods -n flask --as=system:serviceaccount:flask:flask-backend

yes
```

To summarize, you will need to configure a serviceAccount and its related Kubernetes RBAC permissions if your software needs to interact with the hosting Kubernetes cluster.

