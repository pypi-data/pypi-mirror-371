from datetime import datetime

from cloudcoil.apimachinery import ObjectMeta

# cloudcoil generated models from crds.yaml
from .models.v1 import Gate, Period
from .models.v1 import GateSpec as RawGateSpec  # Spec for raw gates
from .models.v1 import GateSpecModel as ConnGateSpec  # Spec for conn gates
from .models.v1 import GateSpecModel1 as GateSpec  # Actual gate spec


async def add_raw_gate(
    namespace: str,
    name: str,
    conn_src: str,
    conn_dst: str,
    rule: str,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
):
    if from_time and from_time.tzinfo is None:
        raise ValueError("from_time must be timezone-aware")
    if to_time and to_time.tzinfo is None:
        raise ValueError("to_time must be timezone-aware")
    spec = RawGateSpec(
        type="raw",
        conn_src=conn_src,
        conn_dst=conn_dst,
        rule=rule,
        period=Period(
            from_time=str(from_time) if from_time else None,
            to_time=str(to_time) if to_time else None,
        ),
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
    from_time: datetime | None = None,
    to_time: datetime | None = None,
):
    if from_time and from_time.tzinfo is None:
        raise ValueError("from_time must be timezone-aware")
    if to_time and to_time.tzinfo is None:
        raise ValueError("to_time must be timezone-aware")

    spec = ConnGateSpec(
        type="connection",
        conn_src=conn_src,
        conn_dst=conn_dst,
        expression=expression,
        period=Period(
            from_time=str(from_time) if from_time else None,
            to_time=str(to_time) if to_time else None,
        ),
    )
    gate = Gate(
        metadata=ObjectMeta(
            name=name,
            namespace=namespace,
        ),
        spec=GateSpec(spec),
    )
    await gate.async_create()
