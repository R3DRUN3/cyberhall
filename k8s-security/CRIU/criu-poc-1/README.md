# KUBERNETES CONTAINER CHECKPOINT WITH CRIU POC

## Abstract
This readme contains step-by-step instructions to demonstrate the usage of [CRIU](https://criu.org/Main_Page) on kubernetes in order to generate snapshot of running containers.    
This can be usefull for incident-response and forensic analysis activities.  


## Prerequisites
- *docker*
- *minikube*


## Instructions
Spin up a local test cluster:  
```console
minikube start \
--profile criupoc \
--container-runtime=crio \
--feature-gates=ContainerCheckpoint=true
```   

Review configuration to make sure that the required [kubelet feature gate](https://kubernetes.io/blog/2022/12/05/forensic-container-checkpointing-alpha/#how-do-i-use-container-checkpointing)  is setup correctly:  

```console
cat ~/.minikube/profiles/criupoc/config.json | grep ContainerCheckpoint
```  

This should show  `"FeatureGates": "ContainerCheckpoint=true"`  

run a test pod:  
```console
kubectl apply -f pod.yaml
```  


ssh inside the cluster:  
```console
minikube ssh -p criupoc
```  

Become the root user:  
```console
sudo su - root
```  

Now we need to update the `cri-o` version.  
export required env vars:  
```console
export OS=xUbuntu_20.04 \
&& export VERSION=1.28 \
&& echo $OS && echo $VERSION
```  

run the following command to install the required version of cri-o:  
```console
echo "deb [signed-by=/usr/share/keyrings/libcontainers-archive-keyring.gpg] https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS/ /" > /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list \
&& echo "deb [signed-by=/usr/share/keyrings/libcontainers-crio-archive-keyring.gpg] https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/$VERSION/$OS/ /" > /etc/apt/sources.list.d/devel:kubic:libcontainers:stable:cri-o:$VERSION.list \
&& mkdir -p /usr/share/keyrings \
&& curl -L https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS/Release.key | gpg --dearmor -o /usr/share/keyrings/libcontainers-archive-keyring.gpg \
&& curl -L https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/$VERSION/$OS/Release.key | gpg --dearmor -o /usr/share/keyrings/libcontainers-crio-archive-keyring.gpg \
&& apt-get update \
&& apt-get install -y cri-o cri-o-runc \
&& crio -v
```  

Now we need to enable the criu support for cri-o:  
```console
systemctl stop crio \
&& crio --enable-criu-support=true
```
This command is blocking as it shows the crio log for better understanding of what is going on and identify possible errors.  
Leave the terminal open and continue to input the below commands from a new terminal.  


Inside the minikube node create 2 files, `client.crt` and `client.key` with the contents that you find in:
1. *~/.minikube/profiles/criupoc/client.crt*
2. *~/.minikube/profiles/criupoc/client.key*  

Once you have done this, you are ready to call the kubelet api to request asnapshot of our running container:  
```console
curl --insecure --cert client.crt --key client.key -X POST "https://localhost:10250/checkpoint/default/nginx/nginx"
```  

Output:  
```json
{"items":["/var/lib/kubelet/checkpoints/checkpoint-nginx_default-nginx-2023-12-07T11:23:16Z.tar"]}
```  

Good, our snapshot is located at `var/lib/kubelet/checkpoints/`  
Now we can ispect it with [checkpointctl](https://github.com/checkpoint-restore/checkpointctl) but first we need to install `git`, `wget`, `make` and `go` on the minikube node.  
```console
apt install git -y \
&& apt install wget -y \
&& apt install make -y \
&& wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz \
&&  rm -rf /usr/local/go && tar -C /usr/local -xzf go1.21.5.linux-amd64.tar.gz \
&& export PATH=$PATH:/usr/local/go/bin \
&& go version
```  
Now we can clone the tool's repository and build it from source:  
```console
mkdir temp \
&& cd temp \
&& git clone https://github.com/checkpoint-restore/checkpointctl.git \
&&  cd checkpointctl \
&& make
```  

Now we are ready to inspect our snapshot!  
For example we can retrieve the process tree:  
```console
./checkpointctl inspect /var/lib/kubelet/checkpoints/checkpoint-nginx_default-nginx-2023-12-07T11:23:16Z.tar --ps-tree
```  

Output:  
```console
Displaying container checkpoint tree view from /var/lib/kubelet/checkpoints/checkpoint-nginx_default-nginx-2023-12-07T11:23:16Z.tar

nginx
├── Image: docker.io/library/nginx:1.14.2
├── ID: cc6b57efab63a55a1835a31847ff3cd2d1abb4e5d024f84aa32a5d54d14fe937
├── Runtime: runc
├── Created: 2023-12-07T11:17:27.152825798Z
├── Engine: CRI-O
├── IP: 10.244.0.4
├── Checkpoint size: 2.1 MiB
│   └── Memory pages size: 2.0 MiB
├── Root FS diff size: 6.0 KiB
└── Process tree
    └── [1]  nginx
        └── [7]  nginx
```  

Or we can perform memory analysis:  
```console
./checkpointctl memparse /var/lib/kubelet/checkpoints/checkpoint-nginx_default-nginx-2023-12-07T11:23:16Z.tar  --pid=1 | more
```   
Output:  
```console
Displaying memory pages content for process ID 1 from checkpoint: /var/lib/kubelet/checkpoints/checkpoint-nginx_default-nginx-2023-12-07T11:23:16Z.tar

Address           Hexadecimal                                       ASCII            
-------------------------------------------------------------------------------------
0000558d1de00000  7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00  |.ELF............|
0000558d1de00010  03 00 3e 00 01 00 00 00 20 7c 02 00 00 00 00 00  |..>..... |......|
0000558d1de00020  40 00 00 00 00 00 00 00 58 d1 13 00 00 00 00 00  |@.......X.......|
0000558d1de00030  00 00 00 00 40 00 38 00 09 00 40 00 1c 00 1b 00  |....@.8...@.....|
0000558d1de00040  06 00 00 00 05 00 00 00 40 00 00 00 00 00 00 00  |........@.......|
0000558d1de00050  40 00 00 00 00 00 00 00 40 00 00 00 00 00 00 00  |@.......@.......|
0000558d1de00060  f8 01 00 00 00 00 00 00 f8 01 00 00 00 00 00 00  |................|
*
0000558d1de00080  38 02 00 00 00 00 00 00 38 02 00 00 00 00 00 00  |8.......8.......|
0000558d1de00090  38 02 00 00 00 00 00 00 1c 00 00 00 00 00 00 00  |8...............|
0000558d1de000a0  1c 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00  |................|
*
0000558d1de000d0  44 ae 11 00 00 00 00 00 44 ae 11 00 00 00 00 00  |D.......D.......|
0000558d1de000e0  00 00 20 00 00 00 00 00 01 00 00 00 06 00 00 00  |.. .............|
0000558d1de000f0  c8 b8 11 00 00 00 00 00 c8 b8 31 00 00 00 00 00  |..........1.....|
0000558d1de00100  c8 b8 31 00 00 00 00 00 58 17 02 00 00 00 00 00  |..1.....X.......|
0000558d1de00110  f0 0e 04 00 00 00 00 00 00 00 20 00 00 00 00 00  |.......... .....|
0000558d1de00120  02 00 00 00 06 00 00 00 80 c2 11 00 00 00 00 00  |................|
0000558d1de00130  80 c2 31 00 00 00 00 00 80 c2 31 00 00 00 00 00  |..1.......1.....|
0000558d1de00140  30 02 00 00 00 00 00 00 30 02 00 00 00 00 00 00  |0.......0.......|
0000558d1de00150  08 00 00 00 00 00 00 00 04 00 00 00 04 00 00 00  |................|
0000558d1de00160  54 02 00 00 00 00 00 00 54 02 00 00 00 00 00 00  |T.......T.......|
0000558d1de00170  54 02 00 00 00 00 00 00 44 00 00 00 00 00 00 00  |T.......D.......|
0000558d1de00180  44 00 00 00 00 00 00 00 04 00 00 00 00 00 00 00  |D...............|
0000558d1de00190  50 e5 74 64 04 00 00 00 58 cf 0f 00 00 00 00 00  |P.td....X.......|
0000558d1de001a0  58 cf 0f 00 00 00 00 00 58 cf 0f 00 00 00 00 00  |X.......X.......|
--More--
```  
To get an overview of process memory sizes within the checkpoint, run checkpointctl memparse without arguments:  
```console
./checkpointctl memparse /var/lib/kubelet/checkpoints/checkpoint-nginx_default-nginx-2023-12-07T11:23:16Z.tar
```   
Output:  
```console
Displaying processes memory sizes from /var/lib/kubelet/checkpoints/checkpoint-nginx_default-nginx-2023-12-07T11:23:16Z.tar

+-----+--------------+-------------+--------------------+
| PID | PROCESS NAME | MEMORY SIZE | SHARED MEMORY SIZE |
+-----+--------------+-------------+--------------------+
|   1 | nginx        | 824.0 KiB   | 4.0 KiB            |
+-----+--------------+-------------+--------------------+
|   7 | nginx        | 1.2 MiB     | 8.0 KiB            |
+-----+--------------+-------------+--------------------+
```  

Now let's go and inspect our snapshot structure.  
Let's untar our snapshot archive:  
```console
mkdir nginx_restore \
&& tar -xf /var/lib/kubelet/checkpoints/checkpoint-nginx_default-nginx-2023-12-07T11:23:16Z.tar -C nginx_restore \
&& cd nginx_restore \
&& ls
```  

Output:  
```console
bind.mounts  checkpoint  config.dump  dump.log  io.kubernetes.cri-o.LogPath  rootfs-diff.tar  spec.dump  stats-dump
```  
These are all the files and directories that we need in order to inspect our container snapshot.  
For example we can cat the config dump:  
```console
cat config.dump
```  
Output:  
```json
{
  "id": "571dd9eb9f1d11cc26a683ce1c898dbafc001fc5c930c2dbcd5180eb83ca53d8",
  "name": "k8s_nginx_nginx_default_56e12ebd-b2fb-46b4-b083-169e19c9b554_1",
  "rootfsImage": "295c7be079025306c4f1d65997fcf7adb411c88f139ad1d34b537164aa060369",
  "rootfsImageRef": "295c7be079025306c4f1d65997fcf7adb411c88f139ad1d34b537164aa060369",
  "rootfsImageName": "docker.io/library/nginx:1.14.2",
  "runtime": "runc",
  "createdTime": "2023-12-11T14:27:20.998153919Z",
  "checkpointedTime": "2023-12-11T14:29:55.396005457Z",
  "restoredTime": "0001-01-01T00:00:00Z",
  "restored": false
}
```  

Or investigate network bind mounts:  
```console
cat bind.mounts
```  

Output:  
```json
[
  {
    "source": "/run/containers/storage/overlay-containers/60f45dcb6460a442e7768a7db18fe54277afc6e90b81d1f831a18220b7c92e78/userdata/resolv.conf",
    "destination": "/etc/resolv.conf",
    "file_type": "file",
    "permissions": 420
  },
  {
    "source": "/run/containers/storage/overlay-containers/60f45dcb6460a442e7768a7db18fe54277afc6e90b81d1f831a18220b7c92e78/userdata/hostname",
    "destination": "/etc/hostname",
    "file_type": "file",
    "permissions": 420
  },
  {
    "source": "/var/lib/kubelet/pods/56e12ebd-b2fb-46b4-b083-169e19c9b554/etc-hosts",
    "destination": "/etc/hosts",
    "file_type": "file",
    "permissions": 420
  },
  {
    "source": "/var/lib/kubelet/pods/56e12ebd-b2fb-46b4-b083-169e19c9b554/containers/nginx/a4d8fc6f",
    "destination": "/dev/termination-log",
    "file_type": "file",
    "permissions": 438
  },
  {
    "source": "/var/lib/kubelet/pods/56e12ebd-b2fb-46b4-b083-169e19c9b554/volumes/kubernetes.io~projected/kube-api-access-wjlb8",
    "destination": "/var/run/secrets/kubernetes.io/serviceaccount",
    "file_type": "directory",
    "permissions": 511
  }
]
```  
Or check the cgroups:  
```console
sudo crit decode -i checkpoint/cgroup.img --pretty
```   
Output:  
```json
{
    "magic": "CGROUP",
    "entries": [
        {
            "sets": [
                {
                    "id": 2,
                    "ctls": [
                        {
                            "name": "",
                            "path": "/crio/crio-571dd9eb9f1d11cc26a683ce1c898dbafc001fc5c930c2dbcd5180eb83ca53d8",
                            "cgns_prefix": 75
                        }
                    ]
                },
                {
                    "id": 3,
                    "ctls": [
                        {
                            "name": "",
                            "path": "/crio/crio-571dd9eb9f1d11cc26a683ce1c898dbafc001fc5c930c2dbcd5180eb83ca53d8",
                            "cgns_prefix": 75
                        }
                    ]
                }
            ],
            "controllers": [
                {
                    "cnames": [
                        ""
                    ],
                    "dirs": [
                        {
                            "dir_name": "crio/crio-571dd9eb9f1d11cc26a683ce1c898dbafc001fc5c930c2dbcd5180eb83ca53d8",
                            "properties": [
                                {
                                    "name": "cgroup.procs",
                                    "value": "",
                                    "perms": {
                                        "mode": 33188,
                                        "uid": 0,
                                        "gid": 0
                                    }
                                }
                            ],
                            "dir_perms": {
                                "mode": 16877,
                                "uid": 0,
                                "gid": 0
                            }
                        }
                    ]
                }
            ]
        }
    ]
}
```  


Note that, once you have this snapshot available, you can restore this into a docker container and exec into it/use tool to do further analysis!  



