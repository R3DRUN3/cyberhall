# FIRST SCAN AGAINST A CLUSTER
This demo shows how to get started with `kube-hunter` on a `minikube` cluster.
<br/>

## Prerequisites
- `pip3` installed
- `docker` installed
- `minikube` installed and ready to rock!

<br/>

## Instructions
Start the cluster:  
```console
minikube start

😄  minikube v1.28.0 on Darwin 13.0 (arm64)
✨  Automatically selected the docker driver
📌  Using Docker Desktop driver with root privileges
👍  Starting control plane node minikube in cluster minikube
🚜  Pulling base image ...
🔥  Creating docker container (CPUs=2, Memory=4000MB) ...--
🐳  Preparing Kubernetes v1.25.3 on Docker 20.10.20 ...
    ▪ Generating certificates and keys ...
    ▪ Booting up control plane ...
    ▪ Configuring RBAC rules ...
🔎  Verifying Kubernetes components...
    ▪ Using image gcr.io/k8s-minikube/storage-provisioner:v5
🌟  Enabled addons: storage-provisioner, default-storageclass
🏄  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

<br/>

Next we need to install `kube-hunter`, we will use `pip`:  
```console
pip3 install kube-hunter
```


<br/>

Verify that the package is installed with this command:  
```python
pip3 freeze | grep kube-hunter

kube-hunter==0.6.8
```

<br/>

Cool! we are ready to start our scan.
<br/>
Kube-hunter can be launched in different mode, for this demo we will run it as a Kubernetes job inside our cluster.
<br/>
The job manifest can be found in the `job.yml` file.
<br/>


Lets apply this manifest:  
```console
kubectl apply -f job.yml && kubectl get pods -w

job.batch/kube-hunter created
NAME                READY   STATUS              RESTARTS   AGE
kube-hunter-fdrmc   0/1     ContainerCreating   0          13s
kube-hunter-fdrmc   1/1     Running             0          14s
kube-hunter-fdrmc   0/1     Completed           0          36s
kube-hunter-fdrmc   0/1     Completed           0          38s
kube-hunter-fdrmc   0/1     Completed           0          39s
```
<br/>

Wait until the job is in `Completed` status.
<br/>


Now we can retrieve the report with the following command:  
```console
kubectl logs kube-hunter-fdrmc >> vapt-report.txt
```

<br/>

Now if you open the `vapt-report.txt` file, you can inspect your cluster vulnerabilities:  
```console
+--------+----------------------+----------------------+----------------------+----------------------+----------------------+
| ID     | LOCATION             | MITRE CATEGORY       | VULNERABILITY        | DESCRIPTION          | EVIDENCE             |
+--------+----------------------+----------------------+----------------------+----------------------+----------------------+
| None   | Local to Pod (kube-  | Lateral Movement //  | CAP_NET_RAW Enabled  | CAP_NET_RAW is       |                      |
|        | hunter-fdrmc)        | ARP poisoning and IP |                      | enabled by default   |                      |
|        |                      | spoofing             |                      | for pods.            |                      |
|        |                      |                      |                      |     If an attacker   |                      |
|        |                      |                      |                      | manages to           |                      |
|        |                      |                      |                      | compromise a pod,    |                      |
|        |                      |                      |                      |     they could       |                      |
|        |                      |                      |                      | potentially take     |                      |
|        |                      |                      |                      | advantage of this    |                      |
|        |                      |                      |                      | capability to        |                      |
|        |                      |                      |                      | perform network      |                      |
|        |                      |                      |                      |     attacks on other |                      |
|        |                      |                      |                      | pods running on the  |                      |
|        |                      |                      |                      | same node            |                      |
+--------+----------------------+----------------------+----------------------+----------------------+----------------------+
| KHV002 | 10.96.0.1:443        | Initial Access //    | K8s Version          | The kubernetes       | v1.25.3              |
|        |                      | Exposed sensitive    | Disclosure           | version could be     |                      |
|        |                      | interfaces           |                      | obtained from the    |                      |
|        |                      |                      |                      | /version endpoint    |                      |
+--------+----------------------+----------------------+----------------------+----------------------+----------------------+
| KHV005 | 10.96.0.1:443        | Discovery // Access  | Access to API using  | The API Server port  | b'{"kind":"APIVersio |
|        |                      | the K8S API Server   | service account      | is accessible.       | ns","versions":["v1" |
|        |                      |                      | token                |     Depending on     | ],"serverAddressByCl |
|        |                      |                      |                      | your RBAC settings   | ientCIDRs":[{"client |
|        |                      |                      |                      | this could expose    | CIDR":"0.0.0.0/0","s |
|        |                      |                      |                      | access to or control | ...                  |
|        |                      |                      |                      | of your cluster.     |                      |
+--------+----------------------+----------------------+----------------------+----------------------+----------------------+
| None   | Local to Pod (kube-  | Credential Access // | Access to pod's      | Accessing the pod's  | ['/var/run/secrets/k |
|        | hunter-fdrmc)        | Access container     | secrets              | secrets within a     | ubernetes.io/service |
|        |                      | service account      |                      | compromised pod      | account/token', '/va |
|        |                      |                      |                      | might disclose       | r/run/secrets/kubern |
|        |                      |                      |                      | valuable data to a   | etes.io/serviceaccou |
|        |                      |                      |                      | potential attacker   | ...                  |
+--------+----------------------+----------------------+----------------------+----------------------+----------------------+
| KHV050 | Local to Pod (kube-  | Credential Access // | Read access to pod's | Accessing the pod    | eyJlbGciOiJSUzI1NiIs |
|        | hunter-fdrmc)        | Access container     | service account      | service account      | ImtpZCI6ImFUbG5pUnNw |
|        |                      | service account      | token                | token gives an       | b1BubPxFTU5KT3ppS0xD |
|        |                      |                      |                      | attacker the option  | SU1QOWlNWEk3bklwS29u |
|        |                      |                      |                      | to use the server    | UkRbTjQifQ.eyJhdWQiO |
|        |                      |                      |                      | API                  | ...                  |
+--------+----------------------+----------------------+----------------------+----------------------+----------------------+
```

<br/>

We are done! You can now delete the job pod:  
```console
kubectl delete job kube-hunter

job.batch "kube-hunter" deleted
```

