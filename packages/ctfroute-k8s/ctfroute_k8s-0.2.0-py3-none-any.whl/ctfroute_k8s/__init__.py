from cloudcoil.apimachinery import ObjectMeta

# cloudcoil generated models from crds.yaml
from .models.v1 import Gate
from .models.v1 import GateSpec as RawGateSpec  # Spec for raw gates
from .models.v1 import GateSpecModel as ConnGateSpec  # Spec for conn gates
from .models.v1 import GateSpecModel1 as GateSpec  # Actual gate spec


async def add_raw_gate(
    namespace: str,
    name: str,
    conn_src: str,
    conn_dst: str,
    rule: str,
):
    spec = RawGateSpec(
        type="raw",
        conn_src=conn_src,
        conn_dst=conn_dst,
        rule=rule,
    )
    gate = Gate(
        metadata=ObjectMeta(
            name=name,
            namespace=namespace,
        ),
        spec=GateSpec(spec),
    )
    await gate.async_create()


async def add_connection_gate(
    namespace: str,
    name: str,
    conn_src: str,
    conn_dst: str,
    expression: str | None = None,
):
    spec = ConnGateSpec(
        type="connection",
        conn_src=conn_src,
        conn_dst=conn_dst,
        expression=expression,
    )
    gate = Gate(
        metadata=ObjectMeta(
            name=name,
            namespace=namespace,
        ),
        spec=GateSpec(spec),
    )
    await gate.async_create()
