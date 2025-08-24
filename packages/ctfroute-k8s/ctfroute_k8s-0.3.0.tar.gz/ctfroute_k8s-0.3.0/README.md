# ctfroute-k8s

This package exposes a lightweight interface to ctfroute via Kubernetes [CRDs](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/).
Specifically, it allows to create gate instances in Kubernetes via CRDs that will be handled by the ctfroute operator.

## Installation

The package can be installed from pypi:

```shell
uv add ctfroute-k8s
```

## Managing gates

To create instances, you can either use the models or the wrapper functions which should allow for more intuitive gate declaration.

```py
from ctfroute_k8s import add_connection_gate

await add_connection_gate(
    namespace=NAMESPACE,
    name="close-network",
    conn_src="any-team",
    conn_dst="any-team",
)
```

If you want to remove gates, fall back to the functionality provided by cloudcoil via the `Gate` model.

```py
from ctfroute_k8s import Gate
gate = await Get.async_get(namespace="myctf", name="close-network")
await gate.async_delete()
```
