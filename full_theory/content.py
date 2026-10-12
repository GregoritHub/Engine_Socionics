"""Paid references, receipt-gated uptake and exact native content handoffs.

The bridge is an adapter: native state remains authoritative. Labels never
instantiate semantic content. It does not add an operation or reprice one.
"""
from hle import model_a
from hle_unified.material import attrs
from hle_unified.records import ObjectRef, Occurrence, Account
from hle_unified.operation_records import OperationRequest
from hle_unified.particulars import Selector
from hle_unified.selection_records import dumps
from hashlib import sha256

FACETS = ("experience", "norms", "situation", "time")
PUBLIC = ("c2.message", "c3.message", "c4.message", "c7w.message")


def fingerprint(value):
    return sha256(dumps(value).encode()).hexdigest()


def facets_at(seat):
    return FACETS[:model_a.fields(seat)["dimensionality"]]


def inputs_of(request):
    values = getattr(request, "inputs", None)
    if values is not None:
        return tuple(values)
    single = getattr(request, "input", None)
    return () if single is None else (single,)


def semantic_scope(engine, job):
    """Native task referent; physical work may have a different target or none."""
    target = job["content_target"] if "content_target" in job else job.get("target")
    binding = job.get("binding")
    if binding is not None:
        account = engine.world.resolve(binding).facet(Account)
        if (account is None or account.holder != job["actor"]
                or account.referent != target or not account.content
                or any((p.subject, p.context) != (target, job["context"])
                       for p in account.content)):
            raise ValueError("native content scope differs from its typed result")
    return target


class ContentBridge:
    VERSION = "paid-references-v1"

    def __init__(self, engine):
        self.engine = engine
        self.events = []
        self.packets = {}
        self.receipts = {}
        self.kept = {}
        self.charge = {}

    def tim(self, actor):
        return attrs(self.engine.world.resolve(self.engine._profiles[actor]))["tim"]

    def execute(self, request, *, quantum=1000000, consumed=()):
        """One bounded paid native job; partial work cannot produce a payload."""
        e = self.engine
        available = inputs_of(request)
        if any(ref not in available for ref in consumed):
            raise ValueError("each claimed content handoff must be a native input")
        for ref in consumed:
            view = e.participant_view(request.actor)
            if ref not in view._bindings and not view.resolve(ref):
                raise ValueError("claimed handoff lacks paid owned access")
        before = {k:e.wallet(request.actor)[k] for k in ("energy", "time")}
        cid = "ft:process:" + request.actor.key + ":" + request.key
        if (request.actor, request.key) not in e._jobs:
            e.start(cid + ":start", request)
        d = e.job_status(request.actor, request.key)
        if d["status"] not in ("ready", "succeeded", "failed", "cancelled"):
            e.advance(cid + ":advance:" + str(d["completed"]), request.actor, request.key, quantum)
        d = e.job_status(request.actor, request.key)
        if d["status"] == "ready":
            e.commit(cid + ":commit", request.actor, request.key)
        d = e.job_status(request.actor, request.key)
        row = dict(kind="native_work", actor=request.actor, key=request.key,
            operation=e._jobs[request.actor,request.key], status=d["status"],
            inputs=available, consumed=tuple(consumed), before=before,
            after={k:e.wallet(request.actor)[k] for k in ("energy", "time")},
            output=d.get("binding") or d.get("result"))
        self.events.append(row)
        return row

    def completed(self, actor, key):
        e = self.engine; d = e.job_status(actor, key)
        if d["status"] != "succeeded" or d["completed"] != d["required"] or d["spent"] < d["required"]:
            raise ValueError("completed paid operation required")
        if not d.get("route_count") or d.get("steps_completed",0) != d["route_count"]:
            raise ValueError("realized native content route required")
        last = d["route_count"]-1
        aspect = d[f"route.{last}.element"]
        seat = model_a.position_of(d["tim"], aspect)
        outputs = tuple(dict.fromkeys([v for k,v in d.items()
            if k in ("binding","result") or k.startswith("public.")]))
        return dict(actor=actor, key=key, operation=e._jobs[actor,key],
            aspect=aspect, seat=seat, facets=facets_at(seat), outputs=outputs,
            steps=d["steps_completed"], last_step=d["last_step"],
            origin=d["origin"], destination=d["destination"], context=d["context"],
            target=semantic_scope(e,d), physical_target=d.get("target"), spent=d["spent"])

    def emit(self, key, sender, operation_key, receiver, output=None, *, provenance=()):
        if key in self.packets:
            raise ValueError("packet identity already emitted")
        row = self.completed(sender, operation_key)
        if output is None:
            output = row["outputs"][0]
        if output not in row["outputs"]:
            raise ValueError("payload must name an actual exact operation output")
        value = self.engine.world.resolve(output)
        if sender != receiver and value.occurrence != Occurrence.ACTUAL_EVENT and output.identity.namespace not in PUBLIC:
            raise ValueError("private binding cannot be transmitted as receiver knowledge")
        # Actual events are delivered only to their native participants.
        d = attrs(value)
        if value.occurrence == Occurrence.ACTUAL_EVENT:
            members = tuple(v for k,v in d.items() if k.startswith("participant."))
            if receiver not in members:
                raise ValueError("event is outside recipient authority")
        elif output.identity.namespace in PUBLIC:
            from hle_unified.self_content import decode
            body = decode(d["payload"])
            parties = body.get("participants", ()) or (body.get("speaker"), body.get("receiver"))
            if receiver not in parties:
                raise ValueError("public payload is outside recipient scope")
        packet = dict(version=self.VERSION, key=key, sender=sender, receiver=receiver,
            operation=row["operation"], operation_key=operation_key, output=output,
            aspect=row["aspect"], facets=row["facets"], context=row["context"],
            target=row["target"], provenance=tuple(provenance))
        self.packets[key] = packet
        self.events.append(dict(kind="emit", packet=packet))
        return packet

    def receive(self, key, receiver, *, quantum=1000000):
        if key not in self.packets:
            raise ValueError("unknown content packet")
        if key in self.receipts:
            raise ValueError("duplicate packet cannot grant new uptake")
        p = self.packets[key]; e = self.engine
        if receiver != p["receiver"]:
            raise ValueError("wrong packet recipient")
        actual = self.completed(p["sender"], p["operation_key"])
        if (actual["operation"] != p["operation"] or actual["aspect"] != p["aspect"]
                or p["output"] not in actual["outputs"] or p["facets"] != actual["facets"]
                or (p["context"],p["target"]) != (actual["context"],actual["target"])):
            raise ValueError("packet differs from realized native content")
        source = p["output"]; v = e.world.resolve(source)
        before = {k:e.wallet(receiver)[k] for k in ("energy", "time")}
        delivery = "ft:uptake:" + receiver.key + ":" + key
        if v.occurrence == Occurrence.ACTUAL_EVENT:
            content = e.deliver_event(delivery, source, receiver)
        elif source.identity.namespace in PUBLIC:
            selectors = tuple(Selector(a.name,"detail",("attributes",str(i),"value"))
                for i,a in enumerate(v.attributes) if a.name == "payload")
            e.disclose(delivery,receiver,source,selectors,source)
            content = source
        elif p["sender"] == receiver and source in e.participant_view(receiver)._bindings:
            # Own realization is already paid. Successor recall still pays normally.
            binding = e.participant_view(receiver)._bindings[source]
            read = attrs(e.world.resolve(binding.receipt))
            if read["completed"] != read["required"]:
                raise ValueError("incomplete owned realization")
            content = source; delivery = None
        else:
            raise ValueError("no lawful native delivery for payload")
        read_key = "ft:read:" + key
        if delivery is not None:
            self.execute(OperationRequest(read_key,receiver,"read",p["context"],delivery=delivery),quantum=quantum)
            d = e.job_status(receiver,read_key)
            if d["status"] != "succeeded":
                self.events.append(dict(kind="uptake_partial",packet=key,actor=receiver))
                return None
            receipt = e._jobs[receiver,read_key]
        else:
            receipt = binding.receipt
        seat = model_a.position_of(self.tim(receiver),p["aspect"])
        kept = tuple(f for f in facets_at(seat) if f in p["facets"])
        if not kept:
            raise ValueError("empty facet intersection grants no kept content")
        row = dict(kind="uptake",packet=key,actor=receiver,source=source,content=content,
            receipt=receipt,delivery=delivery,seat=seat,facets=kept,
            before=before,after={k:e.wallet(receiver)[k] for k in ("energy","time")})
        self.receipts[key] = row
        self.kept[receiver,seat] = (content,kept,receipt)
        self.charge[receiver,seat] = kept
        self.events.append(row)
        return row

    def compose(self, request, retained, supplied, *, quantum=1000000):
        if retained == supplied or any(x not in inputs_of(request) for x in (retained,supplied)):
            raise ValueError("composition needs two distinct exact native operands")
        e = self.engine
        recipe = e._recipe_for(request)
        last = (request.elements or recipe.elements)[-1]
        if last != model_a.element_at(self.tim(request.actor),1):
            raise ValueError("Ego composition cannot relabel the actual output aspect")
        row = self.execute(request,quantum=quantum,consumed=(retained,supplied))
        if row["status"] == "succeeded":
            actual = self.completed(request.actor,request.key)
            self.events.append(dict(kind="composition",policy="paid-compatible-composition-v1",
                actor=request.actor,operation=actual["operation"],retained=retained,supplied=supplied,
                output=row["output"],aspect=actual["aspect"],facets=actual["facets"],seat=1))
        return row
