# KUBERNETES TRIVY OPERATOR

The [trivy-operator](https://github.com/aquasecurity/trivy-operator), by Aquasecurity, is a kubernetes operator to enhance cluster security via continuous scans.  

## Prerequisites

- Docker
- KinD
- Helm

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

Now deploy a vulnerable pod:  
```console
kubectl apply -f test/vulnerable-pod.yaml
```

If everything goes well, the operator should produce some `vulnerabilityreport` CR after some time (not just for our custom pod but also for kubernetes components pod in kube-system).  
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

