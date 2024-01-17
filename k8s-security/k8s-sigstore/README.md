# SIGSTORE POLICY CONTROLLER

This folder contains a step-by-step tutorial to get you started with [sigstore policy controller](https://github.com/sigstore/policy-controller).  
The tool is a Kubernetes admission controller that can be used to enforce policies based on verifiable supply-chain metadata from [cosign](https://docs.sigstore.dev/signing/quickstart/).  

## Prerequisites
- Docker
- Helm
- KinD
- Kubectl

## Instructions

Launch a local cluster with *KinD*

```console
kind create cluster --name sigstore-cluster --config test/cluster-config.yaml
```   

Create a namespace for the installation:  
```console
kubectl create namespace cosign-system
```   



Install the `sigstore policy controller` via helm:  
```console
helm repo add sigstore https://sigstore.github.io/helm-charts
helm repo update
helm install policy-controller -n cosign-system sigstore/policy-controller --devel
```  

The `--devel` flag will include any *alpha*, *beta*, or *release candidate* versions of a chart.  
You can specify a particular version with the `--version` flag if you prefer.  


It may take a few minutes for your cluster to deploy all of the manifests needed for the Policy Controller.  
Check the status of your cluster using the kubectl wait command like this:
```console
kubectl -n cosign-system wait --for=condition=Available deployment/policy-controller-webhook && \
kubectl -n cosign-system wait --for=condition=Available deployment/policy-controller-policy-webhook
```  



Once the Policy Controller deployments are done you will receive output like the following:
```console
deployment.apps/policy-controller-webhook condition met
deployment.apps/policy-controller-policy-webhook condition met
```  

> **Note**  
> If you get an error on `policy-controller-policy-webhook` you can still continue with the tutorial.  


Now that you have the Policy Controller installed into your cluster, the next step is to decide which namespaces should use it.  
By default, namespaces must enroll into enforcement, so you will need to label any namespace that you will use with the Policy Controller.  


Run the following command to include the default namespace in image validation and policy enforcement:  
```console
kubectl label namespace default policy.sigstore.dev/include=true
```  
Apply the same label to any other namespace that you want to use with the Policy Controller.  

Now you can test enforcement by running a sample pod:  
```console
kubectl run --image nginx:latest nginx
```  
The Policy Controller will deny the admission request with a message like the following:  
```console
Error from server (BadRequest): admission webhook "policy.sigstore.dev" denied the request: validation failed: no matching policies: spec.containers[0].image
index.docker.io/library/nginx@sha256:4c0fdaa8b6341bfdeca5f18f7837462c80cff90527ee35ef185571e1c327beac
```  


The image is not admitted into the cluster because there are no `ClusterImagePolicy` (CIP) definitions that match it.  
In the next step you apply policy that allows specific images and apply it to your cluster.  

Review the following manifest:  
```yaml
apiVersion: policy.sigstore.dev/v1alpha1
kind: ClusterImagePolicy
metadata:
  name: custom-key-attestation-sbom-spdxjson
spec:
  images:
  - glob: "**"
  authorities:
  - name: custom-key
    key:
      data: |
        -----BEGIN PUBLIC KEY-----
        MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE2ZobFTItyOXob9pKspR0aDSaXjVj
        DEp8brDskB6OnMUx7GQEblD2RDBBmP5TAKvspay2syp4Z+5s2V69vS8OKg==
        -----END PUBLIC KEY-----
    ctlog:
      url: https://rekor.sigstore.dev
    attestations:
    - name: must-have-spdxjson
      predicateType: spdxjson
      policy:
        type: cue
        data: |
          predicateType: "https://spdx.dev/Document"
```  

The purpose of this policy is to verify image attestations before admitting an image into a Kubernetes cluster.  
The policy checks the existence of a SBOM attestation (in [SPDX](https://spdx.github.io/spdx-spec/v2.3/) format) attached to a container image and deny the admission if it does not find one or the key does not match.  
Apply the policy:  
```console
kubectl apply -f test/cluster-image-policy.yaml
```   

Now try to run a simple pod without that attestation:  
```console
kubectl run --image nginx:1.21.6 noattestedimage
```  

Output:  
```console
Error from server (BadRequest): admission webhook "policy.sigstore.dev" denied the request: validation failed: failed policy: custom-key-attestation-sbom-spdxjson: spec.containers[0].image
index.docker.io/library/nginx@sha256:2bcabc23b45489fb0885d69a06ba1d648aeda973fae7bb981bafbb884165e514 attestation key validation failed for authority custom-key for index.docker.io/library/nginx@sha256:2bcabc23b45489fb0885d69a06ba1d648aeda973fae7bb981bafbb884165e514: no matching attestations
```  

As we expected the policy controller denied our image.  
Let's now try with an image that has SBOM (SPDX) attestations (from [this repo](https://github.com7r3drun3/immunize)):  
```console
kubectl run --image ghcr.io/r3drun3/immunize/docker.io/library/nginx:1.21.6-immunized attestedimage
```  

Output:  
```console
pod/attestedimage created
```  

Retrieve the pod and check if it is healthy:  
```console
kubectl get pod attestedimage

NAME            READY   STATUS    RESTARTS   AGE
attestedimage   1/1     Running   0          44s
```  

The policy controller behaved as we expected.  
It verified the attestation by relying on the SBOM predicate associated with the image and validating it with the public key specified in the CRD.  

In order to better understand attestations, take a look at the [in-toto attestation framework spec](https://github.com/in-toto/attestation/blob/main/spec/README.md#in-toto-attestation-framework-spec).  
In ordert to understand how in-toto verifies an attestation, take a look at the [in-toto validation model](https://github.com/in-toto/attestation/blob/main/docs/validation.md).  

If you want to learn more about this admission controller, please read the [official documentation](https://docs.sigstore.dev/policy-controller/overview/).  





To delete the test cluster, launch the following command:  
```console
kind delete cluster --name sigstore-cluster
```  