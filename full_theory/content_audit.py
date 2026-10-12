"""Independent reconstruction over raw records. No runtime adapter imports."""
from hle import model_a
from hle_unified.material import attrs
from hle_unified.records import Account


def audit_content(transactions, events):
    versions = {v.ref:v for tx in transactions for v in tx.versions}
    heads = {}
    for tx in transactions:
        for v in tx.versions:
            heads[v.ref.identity] = v
    packets = {}; receipts = {}; checked = []
    def fail(reason):
        raise ValueError("FT content audit: " + reason)
    def paid(ref):
        if ref not in versions:
            fail("missing paid record")
        d = attrs(versions[ref])
        if d.get("completed") != d.get("required") or not d.get("required") or d.get("spent",0) < d["required"]:
            fail("unpaid record")
        if d.get("status", "succeeded") != "succeeded":
            fail("unsuccessful operation")
        return d
    def realization(ref):
        d = paid(ref)
        count = d.get("route_count",0)
        if not count or d.get("steps_completed") != count:
            fail("missing realized route")
        steps = sorted((v for v in versions.values() if attrs(v).get("operation") is not None
            and getattr(attrs(v)["operation"],"identity",None) == ref.identity
            and "paid_threshold" in attrs(v)), key=lambda v:attrs(v)["index"])
        if len(steps) != count:
            fail("missing or duplicate native intermediate")
        previous = None
        for i,v in enumerate(steps):
            s = attrs(v)
            if s["index"] != i or s["paid_threshold"] > d["completed"]:
                fail("unpaid semantic step")
            if previous is not None and s["predecessor"] != previous:
                fail("broken semantic predecessor")
            if not v.facet(Account) or s["predecessor"] not in v.facet(Account).sources:
                fail("content does not cite actual predecessor")
            previous = v.ref
        if previous != d["last_step"]:
            fail("incorrect final semantic step")
        return d
    for event in events:
        kind = event["kind"]
        if kind == "native_work":
            d = attrs(versions[event["operation"]])
            if d["actor"] != event["actor"] or d["status"] != event["status"]:
                fail("wrong native owner or status")
            if any(x not in event["inputs"] for x in event["consumed"]):
                fail("claimed input not consumed")
            if d.get("route_count") and d["status"] == "succeeded":
                realization(event["operation"])
        elif kind == "emit":
            p = event["packet"]
            if p["key"] in packets:
                fail("duplicate packet")
            d = realization(p["operation"])
            outputs = [v for k,v in d.items() if k in ("binding","result") or k.startswith("public.")]
            if p["output"] not in outputs or p["sender"] != d["actor"]:
                fail("labels without realized content")
            target = d["content_target"] if "content_target" in d else d.get("target")
            if (p["context"],p["target"]) != (d["context"],target):
                fail("forged packet scope")
            if d.get("binding") is not None:
                account = versions[d["binding"]].facet(Account)
                if (account is None or account.holder != d["actor"] or account.referent != target
                        or not account.content or any((x.subject,x.context)!=(target,d["context"])
                                                     for x in account.content)):
                    fail("typed result disagrees with semantic scope")
            aspect = d[f"route.{d['route_count']-1}.element"]
            cap = ("experience","norms","situation","time")[:model_a.fields(model_a.position_of(d["tim"],aspect))["dimensionality"]]
            if p["aspect"] != aspect or tuple(p["facets"]) != cap:
                fail("forged aspect or facet capacity")
            packets[p["key"]] = p
        elif kind == "uptake":
            key = event["packet"]
            if key not in packets or key in receipts:
                fail("missing or duplicate receipt")
            p = packets[key]; d = paid(event["receipt"])
            if event["actor"] != p["receiver"] or event["source"] != p["output"] or d["actor"] != event["actor"]:
                fail("receipt authority mismatch")
            if event["delivery"] is not None and d.get("delivery") != event["delivery"]:
                fail("receipt does not read this delivery")
            if not event["facets"]:
                fail("empty content cap")
            receipts[key] = event
        elif kind == "composition":
            d = realization(event["operation"])
            inputs = [v for k,v in d.items() if k.startswith("input.")]
            if event["retained"] == event["supplied"] or any(x not in inputs for x in (event["retained"],event["supplied"])):
                fail("composition missing essential operand")
            element = d[f"route.{d['route_count']-1}.element"]
            if element != event["aspect"] or model_a.position_of(d["tim"],element) != 1:
                fail("composition does not preserve actual Ego aspect")
        checked.append(kind)
    return dict(passed=True,events=len(checked),packets=len(packets),paid_uptakes=len(receipts),
                compositions=checked.count("composition"),independent=True)
