import json
import unittest
from full_theory.historical import HistoricalController as H, digest, verify_reference


class HistoricalTests(unittest.TestCase):
    def test_reference_hashes(self):
        self.assertEqual(verify_reference(), 210)

    def test_interleaved_configuration(self):
        a = H("iee", "sli", firing="relay", gate=True)
        b = H("sli", "iee", firing="every_tick", gate=False)
        for _ in range(8):
            a.step(); b.step()
        aa = H("iee", "sli", firing="relay", gate=True); aa.run(8)
        bb = H("sli", "iee", firing="every_tick", gate=False); bb.run(8)
        self.assertEqual(a.checkpoint(), aa.checkpoint())
        self.assertEqual(b.checkpoint(), bb.checkpoint())

    def test_rehashed_forgery_rejected(self):
        a = H(); a.run(3)
        d = json.loads(a.checkpoint()); d["payload"]["inbox"] = {"dict": []}
        d["sha256"] = digest(d["payload"])
        with self.assertRaisesRegex(ValueError, "exact replay"):
            H.restore(json.dumps(d))

    def test_no_resource_model_overload(self):
        with self.assertRaises(TypeError):
            H(resource_model="grade-v1")
        with self.assertRaises(ValueError):
            H(window=2.0)

    def test_metadata_and_chord_controls(self):
        a = H("iee", "sli"); ordinary = a.run(80)
        erased = H("iee", "sli", erase_metadata=True).run(80)
        ablated = H("iee", "sli", no_chord=True).run(80)
        self.assertEqual(ordinary["semantic_hash"], erased["semantic_hash"])
        self.assertEqual((ordinary["output_counts"]["ne"], ablated["output_counts"]["ne"]), (78, 3))
