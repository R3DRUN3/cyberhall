# KUBERNETES TRIVY OPERATOR

The [trivy-operator](https://github.com/aquasecurity/trivy-operator), by Aquasecurity, is a kubernetes operator  
that enhances cluster security via continuous configuration and vulnerabilities audit scans.  

## Prerequisites

- Docker
- Helm
- KinD
- Kubectl

## Instructions to test

Launch a local cluster with *KinD*

```console
kind create cluster --name security-cluster --config test/cluster-config.yaml
```   

Install the `trivy-operator` via helm:  
```console
helm repo add aqua https://aquasecurity.github.io/helm-charts/
helm repo update
helm install trivy-operator aqua/trivy-operator \
    --namespace trivy-system \
    --create-namespace \
    --version 0.18.4
```  

Check the namespaces of your cluster:  
```console
kubectl get ns

NAME                 STATUS   AGE
default              Active   2m21s
kube-node-lease      Active   2m21s
kube-public          Active   2m21s
kube-system          Active   2m21s
local-path-storage   Active   2m15s
trivy-system         Active   8s
```  
As you can see the `trivy-system` namespace has been created.  
Inspect the resources in that namespace:  
```console
kubectl -n trivy-system get all


NAME                                          READY   STATUS    RESTARTS   AGE
pod/node-collector-79fdd6ddc-tbgxb            0/1     Pending   0          2m25s
pod/scan-vulnerabilityreport-b49fc47b-zlmh9   1/1     Running   0          3m25s
pod/trivy-operator-f6cd59866-kskjz            1/1     Running   0          3m38s

NAME                     TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
service/trivy-operator   ClusterIP   None         <none>        80/TCP    3m39s

NAME                             READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/trivy-operator   1/1     1            1           3m39s

NAME                                       DESIRED   CURRENT   READY   AGE
replicaset.apps/trivy-operator-f6cd59866   1         1         1       3m38s

NAME                                          COMPLETIONS   DURATION   AGE
job.batch/node-collector-79fdd6ddc            0/1           2m25s      2m25s
job.batch/scan-vulnerabilityreport-b49fc47b   0/1           3m25s      3m25s
```   

Retrieve the list of the CRDs that has been installed:  
```console
kubectl get crd

NAME                                                   CREATED AT
clustercompliancereports.aquasecurity.github.io        2024-01-15T13:44:27Z
clusterconfigauditreports.aquasecurity.github.io       2024-01-15T13:44:27Z
clusterinfraassessmentreports.aquasecurity.github.io   2024-01-15T13:44:27Z
clusterrbacassessmentreports.aquasecurity.github.io    2024-01-15T13:44:27Z
configauditreports.aquasecurity.github.io              2024-01-15T13:44:27Z
exposedsecretreports.aquasecurity.github.io            2024-01-15T13:44:27Z
infraassessmentreports.aquasecurity.github.io          2024-01-15T13:44:27Z
rbacassessmentreports.aquasecurity.github.io           2024-01-15T13:44:27Z
sbomreports.aquasecurity.github.io                     2024-01-15T13:44:27Z
vulnerabilityreports.aquasecurity.github.io            2024-01-15T13:44:27Z
```   

After some time you should be able to retrieve a list of all `vulnerabilityreports` in all namespaces:  
```console
kubectl get vulnerabilityreports -o wide -A  

NAMESPACE            NAME                                                 REPOSITORY                       TAG                  SCANNER   AGE     CRITICAL   HIGH   MEDIUM   LOW   UNKNOWN
kube-system          daemonset-kindnet-kindnet-cni                        kindest/kindnetd                 v20230511-dc714da8   Trivy     5m28s   0          5      16       22    0
kube-system          daemonset-kube-proxy-kube-proxy                      kube-proxy                       v1.27.3              Trivy     4m46s   0          8      19       22    0
kube-system          pod-6ccff544b9                                       kube-apiserver                   v1.27.3              Trivy     4m47s   0          5      4        0     0
kube-system          pod-78546fd8d9                                       kube-controller-manager          v1.27.3              Trivy     4m39s   0          5      5        0     0
kube-system          pod-797c99d8b5                                       kube-scheduler                   v1.27.3              Trivy     5m3s    0          5      4        0     0
kube-system          pod-etcd-security-cluster-control-plane-etcd         etcd                             3.5.7-0              Trivy     4m17s   0          16     16       0     0
kube-system          replicaset-coredns-5d78c9869d-coredns                coredns/coredns                  v1.10.1              Trivy     5m1s    0          3      4        0     0
local-path-storage   replicaset-7b5b9784d4                                kindest/local-path-provisioner   v20230511-dc714da8   Trivy     5m26s   0          5      18       11    0
trivy-system         replicaset-trivy-operator-f6cd59866-trivy-operator   aquasecurity/trivy-operator      0.16.4               Trivy     4m46s   1          2      7        0     0
```  

These are reports containing the results from the trivy scan on the pods running on the cluster, saved as kubernetes custom resources.  

Try to inspect one of them, for example the one relative to the kube-apiserver:  
```console
kubectl -n kube-system get vulnerabilityreport pod-6ccff544b9 -o yaml
```  

Output example:  
```yaml
apiVersion: aquasecurity.github.io/v1alpha1
kind: VulnerabilityReport
metadata:
  annotations:
    trivy-operator.aquasecurity.github.io/report-ttl: 24h0m0s
  creationTimestamp: "2024-01-15T13:48:24Z"
  generation: 1
  labels:
    resource-spec-hash: 5764dcdd79
    trivy-operator.container.name: kube-apiserver
    trivy-operator.resource.kind: Pod
    trivy-operator.resource.name: kube-apiserver-security-cluster-control-plane
    trivy-operator.resource.namespace: kube-system
  name: pod-6ccff544b9
  namespace: kube-system
  ownerReferences:
  - apiVersion: v1
    blockOwnerDeletion: false
    controller: true
    kind: Pod
    name: kube-apiserver-security-cluster-control-plane
    uid: 7f2e283c-85c7-4a00-81f6-0ee84fa2f8b4
  resourceVersion: "1413"
  uid: f20a6af2-8155-48de-89f5-aa1c22036e47
report:
  artifact:
    digest: sha256:08a0c939e61b7340db53ebf07b4d0e908a35ad8d94e2cb7d0f958210e567079a
    repository: kube-apiserver
    tag: v1.27.3
  registry:
    server: registry.k8s.io
  scanner:
    name: Trivy
    vendor: Aqua Security
    version: 0.45.1
  summary:
    criticalCount: 0
    highCount: 5
    lowCount: 0
    mediumCount: 4
    noneCount: 0
    unknownCount: 0
  updateTimestamp: "2024-01-15T13:48:24Z"
  vulnerabilities:
  - fixedVersion: 2.8.2-beta.1
    installedVersion: v2.8.1+incompatible
    lastModifiedDate: "2023-06-29T16:15:09Z"
    links: []
    primaryLink: https://avd.aquasec.com/nvd/cve-2023-2253
    publishedDate: "2023-06-06T20:15:12Z"
    resource: github.com/docker/distribution
    score: 6.5
    severity: HIGH
    target: ""
    title: DoS from malicious API request
    vulnerabilityID: CVE-2023-2253
  - fixedVersion: 0.46.0
    installedVersion: v0.35.0
    lastModifiedDate: "2023-11-20T19:34:26Z"
    links: []
    primaryLink: https://avd.aquasec.com/nvd/cve-2023-47108
    publishedDate: "2023-11-10T19:15:16Z"
    resource: go.opentelemetry.io/contrib/instrumentation/google.golang.org/grpc/otelgrpc
    score: 7.5
    severity: HIGH
    target: ""
    title: 'opentelemetry-go-contrib: DoS vulnerability in otelgrpc due to unbound
      cardinality metrics'
    vulnerabilityID: CVE-2023-47108
  - fixedVersion: 0.44.0
    installedVersion: v0.35.1
    lastModifiedDate: "2023-10-18T18:27:50Z"
    links: []
    primaryLink: https://avd.aquasec.com/nvd/cve-2023-45142
    publishedDate: "2023-10-12T17:15:09Z"
    resource: go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp
    score: 7.5
    severity: HIGH
    target: ""
    title: 'opentelemetry: DoS vulnerability in otelhttp'
    vulnerabilityID: CVE-2023-45142
  - fixedVersion: 0.17.0
    installedVersion: v0.1.0
    lastModifiedDate: "2024-01-11T04:15:07Z"
    links: []
    primaryLink: https://avd.aquasec.com/nvd/cve-2023-48795
    publishedDate: "2023-12-18T16:15:10Z"
    resource: golang.org/x/crypto
    score: 5.9
    severity: MEDIUM
    target: ""
    title: 'ssh: Prefix truncation attack on Binary Packet Protocol (BPP)'
    vulnerabilityID: CVE-2023-48795
  - fixedVersion: 0.17.0
    installedVersion: v0.8.0
    lastModifiedDate: "2023-12-07T03:15:06Z"
    links: []
    primaryLink: https://avd.aquasec.com/nvd/cve-2023-39325
    publishedDate: "2023-10-11T22:15:09Z"
    resource: golang.org/x/net
    score: 7.5
    severity: HIGH
    target: ""
    title: 'golang: net/http, x/net/http2: rapid stream resets can cause excessive
      work (CVE-2023-44487)'
    vulnerabilityID: CVE-2023-39325
  - fixedVersion: 0.13.0
    installedVersion: v0.8.0
    lastModifiedDate: "2023-11-07T04:20:03Z"
    links: []
    primaryLink: https://avd.aquasec.com/nvd/cve-2023-3978
    publishedDate: "2023-08-02T20:15:12Z"
    resource: golang.org/x/net
    score: 6.1
    severity: MEDIUM
    target: ""
    title: 'golang.org/x/net/html: Cross site scripting'
    vulnerabilityID: CVE-2023-3978
  - fixedVersion: 0.17.0
    installedVersion: v0.8.0
    lastModifiedDate: "2023-12-20T17:55:36Z"
    links: []
    primaryLink: https://avd.aquasec.com/nvd/cve-2023-44487
    publishedDate: "2023-10-10T14:15:10Z"
    resource: golang.org/x/net
    score: 7.5
    severity: MEDIUM
    target: ""
    title: 'HTTP/2: Multiple HTTP/2 enabled web servers are vulnerable to a DDoS attack
      (Rapid Reset Attack)'
    vulnerabilityID: CVE-2023-44487
  - fixedVersion: 1.56.3, 1.57.1, 1.58.3
    installedVersion: v1.51.0
    lastModifiedDate: ""
    links: []
    primaryLink: https://github.com/advisories/GHSA-m425-mq94-257g
    publishedDate: ""
    resource: google.golang.org/grpc
    score: 7.5
    severity: HIGH
    target: ""
    title: gRPC-Go HTTP/2 Rapid Reset vulnerability
    vulnerabilityID: GHSA-m425-mq94-257g
  - fixedVersion: 1.58.3, 1.57.1, 1.56.3
    installedVersion: v1.51.0
    lastModifiedDate: "2023-12-20T17:55:36Z"
    links: []
    primaryLink: https://avd.aquasec.com/nvd/cve-2023-44487
    publishedDate: "2023-10-10T14:15:10Z"
    resource: google.golang.org/grpc
    score: 7.5
    severity: MEDIUM
    target: ""
    title: 'HTTP/2: Multiple HTTP/2 enabled web servers are vulnerable to a DDoS attack
      (Rapid Reset Attack)'
    vulnerabilityID: CVE-2023-44487
```

You can also retrieve the `configauditreports`:  
```console
kubectl get configauditreports -o wide -A

NAMESPACE            NAME                                                         SCANNER   AGE     CRITICAL   HIGH   MEDIUM   LOW
default              service-kubernetes                                           Trivy     6m43s   0          0      0        1
kube-system          daemonset-kindnet                                            Trivy     6m43s   0          3      6        7
kube-system          daemonset-kube-proxy                                         Trivy     6m40s   0          3      5        11
kube-system          pod-etcd-security-cluster-control-plane                      Trivy     6m40s   0          1      4        8
kube-system          pod-kube-apiserver-security-cluster-control-plane            Trivy     6m37s   0          1      4        10
kube-system          pod-kube-controller-manager-security-cluster-control-plane   Trivy     6m43s   0          1      4        9
kube-system          pod-kube-scheduler-security-cluster-control-plane            Trivy     6m36s   0          1      4        9
kube-system          replicaset-coredns-5d78c9869d                                Trivy     6m42s   0          2      4        5
kube-system          service-kube-dns                                             Trivy     6m40s   0          0      1        1
local-path-storage   replicaset-local-path-provisioner-6bc4bddd6b                 Trivy     6m40s   0          1      3        11
trivy-system         replicaset-trivy-operator-f6cd59866                          Trivy     6m37s   0          1      2        8
trivy-system         service-trivy-operator                                       Trivy     6m38s   0          0      0        1
```  

These are reports containing the configuration issues of the cluster's components, saved as kubernetes custom resources.  

Try to inspect one:  
```console
kubectl -n kube-system get configauditreport pod-kube-apiserver-security-cluster-control-plane -o yaml
```   


Output example:  
```yaml
apiVersion: aquasecurity.github.io/v1alpha1
kind: ConfigAuditReport
metadata:
  annotations:
    trivy-operator.aquasecurity.github.io/report-ttl: 24h0m0s
  creationTimestamp: "2024-01-15T14:03:47Z"
  generation: 1
  labels:
    plugin-config-hash: 659b7b9c46
    resource-spec-hash: 5764dcdd79
    trivy-operator.resource.kind: Pod
    trivy-operator.resource.name: kube-apiserver-security-cluster-control-plane
    trivy-operator.resource.namespace: kube-system
  name: pod-kube-apiserver-security-cluster-control-plane
  namespace: kube-system
  ownerReferences:
  - apiVersion: v1
    blockOwnerDeletion: false
    controller: true
    kind: Pod
    name: kube-apiserver-security-cluster-control-plane
    uid: 76ac1b72-fdd8-4c1e-8d62-f522cedc401d
  resourceVersion: "812"
  uid: 1f49f463-cbd7-4a43-ae68-d4f2b3016f63
report:
  checks:
  - category: Kubernetes Security Check
    checkID: KSV0012
    description: Always pull images.
    messages:
    - Ensure that the admission control plugin AlwaysPullImages is set
    severity: LOW
    success: false
    title: Ensure that the admission control plugin AlwaysPullImages is set
  - category: Kubernetes Security Check
    checkID: KSV001
    description: A program inside the container can elevate its own privileges and
      run as root, which might give the program control over the container and node.
    messages:
    - Container 'kube-apiserver' of Pod 'kube-apiserver-security-cluster-control-plane'
      should set 'securityContext.allowPrivilegeEscalation' to false
    severity: MEDIUM
    success: false
    title: Can elevate its own privileges
  - category: Kubernetes Security Check
    checkID: KSV003
    description: The container should drop all default capabilities and add only those
      that are needed for its execution.
    messages:
    - Container 'kube-apiserver' of Pod 'kube-apiserver-security-cluster-control-plane'
      should add 'ALL' to 'securityContext.capabilities.drop'
    severity: LOW
    success: false
    title: 'Default capabilities: some containers do not drop all'
  - category: Kubernetes Security Check
    checkID: KSV009
    description: Sharing the host’s network namespace permits processes in the pod
      to communicate with processes bound to the host’s loopback adapter.
    messages:
    - Pod 'kube-apiserver-security-cluster-control-plane' should not set 'spec.template.spec.hostNetwork'
      to true
    severity: HIGH
    success: false
    title: Access to host network
  - category: Kubernetes Security Check
    checkID: KSV011
    description: Enforcing CPU limits prevents DoS via resource exhaustion.
    messages:
    - Container 'kube-apiserver' of Pod 'kube-apiserver-security-cluster-control-plane'
      should set 'resources.limits.cpu'
    severity: LOW
    success: false
    title: CPU not limited
  - category: Kubernetes Security Check
    checkID: KSV012
    description: Force the running image to run as a non-root user to ensure least
      privileges.
    messages:
    - Container 'kube-apiserver' of Pod 'kube-apiserver-security-cluster-control-plane'
      should set 'securityContext.runAsNonRoot' to true
    severity: MEDIUM
    success: false
    title: Runs as root user
  - category: Kubernetes Security Check
    checkID: KSV014
    description: An immutable root file system prevents applications from writing
      to their local disk. This can limit intrusions, as attackers will not be able
      to tamper with the file system or write foreign executables to disk.
    messages:
    - Container 'kube-apiserver' of Pod 'kube-apiserver-security-cluster-control-plane'
      should set 'securityContext.readOnlyRootFilesystem' to true
    severity: LOW
    success: false
    title: Root file system is not read-only
  - category: Kubernetes Security Check
    checkID: KSV016
    description: When containers have memory requests specified, the scheduler can
      make better decisions about which nodes to place pods on, and how to deal with
      resource contention.
    messages:
    - Container 'kube-apiserver' of Pod 'kube-apiserver-security-cluster-control-plane'
      should set 'resources.requests.memory'
    severity: LOW
    success: false
    title: Memory requests not specified
  - category: Kubernetes Security Check
    checkID: KSV018
    description: Enforcing memory limits prevents DoS via resource exhaustion.
    messages:
    - Container 'kube-apiserver' of Pod 'kube-apiserver-security-cluster-control-plane'
      should set 'resources.limits.memory'
    severity: LOW
    success: false
    title: Memory not limited
  - category: Kubernetes Security Check
    checkID: KSV020
    description: Force the container to run with user ID > 10000 to avoid conflicts
      with the host’s user table.
    messages:
    - Container 'kube-apiserver' of Pod 'kube-apiserver-security-cluster-control-plane'
      should set 'securityContext.runAsUser' > 10000
    severity: LOW
    success: false
    title: Runs with UID <= 10000
  - category: Kubernetes Security Check
    checkID: KSV021
    description: Force the container to run with group ID > 10000 to avoid conflicts
      with the host’s user table.
    messages:
    - Container 'kube-apiserver' of Pod 'kube-apiserver-security-cluster-control-plane'
      should set 'securityContext.runAsGroup' > 10000
    severity: LOW
    success: false
    title: Runs with GID <= 10000
  - category: Kubernetes Security Check
    checkID: KSV023
    description: According to pod security standard 'HostPath Volumes', HostPath volumes
      must be forbidden.
    messages:
    - Pod 'kube-apiserver-security-cluster-control-plane' should not set 'spec.template.volumes.hostPath'
    severity: MEDIUM
    success: false
    title: hostPath volumes mounted
  - category: Kubernetes Security Check
    checkID: KSV104
    description: A program inside the container can bypass Seccomp protection policies.
    messages:
    - container kube-apiserver of pod kube-apiserver-security-cluster-control-plane
      in kube-system namespace should specify a seccomp profile
    severity: MEDIUM
    success: false
    title: Seccomp policies disabled
  - category: Kubernetes Security Check
    checkID: KSV106
    description: Containers must drop ALL capabilities, and are only permitted to
      add back the NET_BIND_SERVICE capability.
    messages:
    - container should drop all
    severity: LOW
    success: false
    title: Container capabilities must only include NET_BIND_SERVICE
  - category: Kubernetes Security Check
    checkID: KSV116
    description: According to pod security standard 'Non-root groups', containers
      should be forbidden from running with a root primary or supplementary GID.
    messages:
    - pod kube-apiserver-security-cluster-control-plane in kube-system namespace should
      set spec.securityContext.runAsGroup, spec.securityContext.supplementalGroups[*]
      and spec.securityContext.fsGroup to integer greater than 0
    severity: LOW
    success: false
    title: Runs with a root primary or supplementary GID
  scanner:
    name: Trivy
    vendor: Aqua Security
    version: 0.16.4
  summary:
    criticalCount: 0
    highCount: 1
    lowCount: 10
    mediumCount: 4
  updateTimestamp: "2024-01-15T14:03:47Z"
```   





Now try to deploy your own vulnerable pod:  
```console
kubectl apply -f test/vulnerable-pod.yaml
```

If everything goes well, the operator should produce some `vulnerabilityreport` CR after some time.  
Retrieve the list of *vulnerabilityreports* in the default namespace:  
```console
kubectl get vulnerabilityreports -o wide

NAME                            REPOSITORY      TAG       SCANNER   AGE     CRITICAL   HIGH   MEDIUM   LOW   UNKNOWN
pod-nginx-pod-nginx-container   library/nginx   1.15.12   Trivy     3m19s   31         77     52       43    7
```  

this view already tells us something about the vulnerabilities that trivy found in our pod.  
To get a better understanding describe the resource:  
```console
kubectl describe vulnerabilityreport pod-nginx-pod-nginx-container

Name:         pod-nginx-pod-nginx-container
Namespace:    default
Labels:       resource-spec-hash=7c6df5b964
              trivy-operator.container.name=nginx-container
              trivy-operator.resource.kind=Pod
              trivy-operator.resource.name=nginx-pod
              trivy-operator.resource.namespace=default
Annotations:  trivy-operator.aquasecurity.github.io/report-ttl: 24h0m0s
API Version:  aquasecurity.github.io/v1alpha1
Kind:         VulnerabilityReport
Metadata:
  Creation Timestamp:  2024-01-15T08:59:39Z
  Generation:          2
  Owner References:
    API Version:           v1
    Block Owner Deletion:  false
    Controller:            true
    Kind:                  Pod
    Name:                  nginx-pod
    UID:                   928c3d90-4248-43f0-956a-e0998caed13e
  Resource Version:        2697
  UID:                     8b41f6aa-e168-4c98-87ec-77888a6c4275
Report:
  Artifact:
    Digest:      sha256:53f3fd8007f76bd23bf663ad5f5009c8941f63828ae458cef584b5f85dc0a7bf
    Repository:  library/nginx
    Tag:         1.15.12
  Registry:
    Server:  index.docker.io
  Scanner:
    Name:     Trivy
    Vendor:   Aqua Security
    Version:  0.45.1
  Summary:
    Critical Count:  31
    High Count:      77
    Low Count:       43
    Medium Count:    52
    None Count:      0
    Unknown Count:   7
  Update Timestamp:  2024-01-15T09:02:52Z
  Vulnerabilities:
    Fixed Version:       1.4.11
    Installed Version:   1.4.9
    Last Modified Date:  2022-10-29T02:41:36Z
    Links:
    Primary Link:        https://avd.aquasec.com/nvd/cve-2020-27350
    Published Date:      2020-12-10T04:15:11Z
    Resource:            apt
    Score:               5.7
    Severity:            MEDIUM
    Target:              
    Title:               apt: integer overflows and underflows while parsing .deb packages
    Vulnerability ID:    CVE-2020-27350
    Fixed Version:       1.4.10
    Installed Version:   1.4.9
    Last Modified Date:  2023-11-07T03:23:04Z
    Links:
    Primary Link:        https://avd.aquasec.com/nvd/cve-2020-3810
    Published Date:      2020-05-15T14:15:11Z
    Resource:            apt
    Score:               5.5
    Severity:            MEDIUM
    Target:              
    Title:               Missing input validation in the ar/tar implementations of APT before v ...
    Vulnerability ID:    CVE-2020-3810
    Fixed Version:       
    Installed Version:   1:2.29.2-1+deb9u1
    Last Modified Date:  2019-01-04T14:14:12Z
    Links:
    Primary Link:        https://avd.aquasec.com/nvd/cve-2016-2779
    Published Date:      2017-02-07T15:59:00Z
    Resource:            bsdutils
    Score:               7.8
    Severity:            HIGH
    Target:              
    Title:               util-linux: runuser tty hijack via TIOCSTI ioctl
    Vulnerability ID:    CVE-2016-2779
    Fixed Version:       
    Installed Version:   1:2.29.2-1+deb9u1
    Last Modified Date:  2024-01-07T09:15:08Z
    Links:
    Primary Link:        https://avd.aquasec.com/nvd/cve-2021-37600
    Published Date:      2021-07-30T14:15:18Z
    Resource:            bsdutils
    Score:               5.5
    Severity:            LOW
    Target:              
    Title:               util-linux: integer overflow can lead to buffer overflow in get_sem_elements() in sys-utils/ipcutils.c
    Vulnerability ID:    CVE-2021-37600
    Fixed Version:       
    Installed Version:   8.26-3
    Last Modified Date:  2023-11-07T02:32:03Z
    Links:
    Primary Link:        https://avd.aquasec.com/nvd/cve-2016-2781
    Published Date:      2017-02-07T15:59:00Z
    Resource:            coreutils
    Score:               6.5
    Severity:            LOW
    Target:              
    Title:               coreutils: Non-privileged session can escape to the parent session in chroot
    Vulnerability ID:    CVE-2016-2781
    Fixed Version:       2017.5+deb9u2
    Installed Version:   2017.5
    Last Modified Date:  
    Links:
    Published Date:      
    Resource:            debian-archive-keyring
    Severity:            UNKNOWN
    Target:              
    Title:               debian-archive-keyring - security update
    Vulnerability ID:    DLA-2948-1
    Fixed Version:       1.18.26
    Installed Version:   1.18.25
    Last Modified Date:  2022-12-03T02:19:32Z
    Links:
    Primary Link:        https://avd.aquasec.com/nvd/cve-2022-1664
    Published Date:      2022-05-26T14:15:08Z
    Resource:            dpkg
    Score:               9.8
    Severity:            CRITICAL
    Target:              
    Title:               Dpkg::Source::Archive in dpkg, the Debian package management system, b ...
    Vulnerability ID:    CVE-2022-1664
    Fixed Version:       
    Installed Version:   1.43.4-2
    Last Modified Date:  2023-11-07T03:41:53Z
    Links:
    Primary Link:        https://avd.aquasec.com/nvd/cve-2022-1304
    Published Date:      2022-04-14T21:15:08Z
    Resource:            e2fslibs
    Score:               7.8
    Severity:            HIGH
    Target:              
    Title:               e2fsprogs: out-of-bounds read/write via crafted filesystem
    Vulnerability ID:    CVE-2022-1304
    Fixed Version:       1.43.4-2+deb9u1
    Installed Version:   1.43.4-2
    Last Modified Date:  2023-11-07T03:11:26Z
    Links:
    Primary Link:        https://avd.aquasec.com/nvd/cve-2019-5094
    Published Date:      2019-09-24T22:15:13Z
    Resource:            e2fslibs
    Score:               6.7
    Severity:            MEDIUM
    Target:              
    Title:               e2fsprogs: Crafted ext4 partition leads to out-of-bounds write
    Vulnerability ID:    CVE-2019-5094
    Fixed Version:       1.43.4-2+deb9u2
    Installed Version:   1.43.4-2
    Last Modified Date:  2023-11-07T03:11:27Z
    Links:
    Primary Link:        https://avd.aquasec.com/nvd/cve-2019-5188
    Published Date:      2020-01-08T16:15:11Z
    Resource:            e2fslibs
    Score:               6.7
    Severity:            MEDIUM
    Target:              
    Title:               e2fsprogs: Out-of-bounds write in e2fsck/rehash.c
    Vulnerability ID:    CVE-2019-5188
    Fixed Version:       
    Installed Version:   1.43.4-2
    Last Modified Date:  2023-11-07T03:41:53Z
    Links:
    Primary Link:        https://avd.aquasec.com/nvd/cve-2022-1304
    Published Date:      2022-04-14T21:15:08Z
    Resource:            e2fsprogs
    Score:               7.8
    Severity:            HIGH
    Target:              
    Title:               e2fsprogs: out-of-bounds read/write via crafted filesystem
    Vulnerability ID:    CVE-2022-1304
    Fixed Version:       1.43.4-2+deb9u1
    Installed Version:   1.43.4-2
    Last Modified Date:  2023-11-07T03:11:26Z
    Links:
    Primary Link:        https://avd.aquasec.com/nvd/cve-2019-5094
    Published Date:      2019-09-24T22:15:13Z
    Resource:            e2fsprogs
    Score:               6.7
    Severity:            MEDIUM
    Target:              
    Title:               e2fsprogs: Crafted ext4 partition leads to out-of-bounds write
    Vulnerability ID:    CVE-2019-5094
    Fixed Version:       1.43.4-2+deb9u2
    Installed Version:   1.43.4-2
    Last Modified Date:  2023-11-07T03:11:27Z
    Links:
    Primary Link:        https://avd.aquasec.com/nvd/cve-2019-5188
    Published Date:      2020-01-08T16:15:11Z
    Resource:            e2fsprogs
    Score:               6.7
    Severity:            MEDIUM
    Target:              
    Title:               e2fsprogs: Out-of-bounds write in e2fsck/rehash.c
    Vulnerability ID:    CVE-2019-5188
    Fixed Version:       
    Installed Version:   6.3.0-18+deb9u1
    Last Modified Date:  2020-08-24T17:37:01Z
    Links:
    Primary Link:        https://avd.aquasec.com/nvd/cve-2018-12886
    Published Date:      2019-05-22T19:29:00Z
    Resource:            gcc-6-base
    Score:               8.1
    Severity:            HIGH
    Target:              
    Title:               gcc: spilling of stack protection address in cfgexpand.c and function.c leads to stack-overflow protection bypass
    Vulnerability ID:    CVE-2018-12886
    Fixed Version:       
    Installed Version:   2.1.18-8~deb9u4
    Last Modified Date:  2019-02-13T16:43:02Z
    Links:
    Primary Link:        https://avd.aquasec.com/nvd/cve-2018-1000858
    Published Date:      2018-12-20T17:29:00Z
    Resource:            gpgv
    Score:               8.8
    Severity:            HIGH
    Target:              
    Title:               gnupg2: Cross site request forgery in dirmngr resulting in an information disclosure or denial of service
    Vulnerability ID:    CVE-2018-1000858
    Fixed Version:       
    Installed Version:   2.1.18-8~deb9u4
    Last Modified Date:  2019-02-27T19:37:32Z
    Links:
    Primary Link:        https://avd.aquasec.com/nvd/cve-2018-9234
    Published Date:      2018-04-04T00:29:00Z

    ...... OUTPUT CONTINUES
```  



You can also [create custom policies via Rego (OPA)](https://aquasecurity.github.io/trivy-operator/latest/tutorials/writing-custom-configuration-audit-policies/) in order to customize your vulnerabilities reports.  

To delete the test cluster, launch the following command:  
```console
kind delete cluster --name security-cluster
```  


