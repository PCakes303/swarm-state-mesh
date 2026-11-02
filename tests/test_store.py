import threading
import unittest

from swarm_state_mesh import StateConflict, StateEvent, StateStore


def event(event_id, task="task.1", revision=0, refs=()):
    return StateEvent(event_id, task, "principal.writer", "task.updated", f"artifact://events/{event_id}", revision, refs)


class StoreTests(unittest.TestCase):

    def test_total_event_capacity_is_bounded(self):
        store = StateStore(max_total_events=1)
        store.append(event("event.1", task="task.1"))
        with self.assertRaises(StateConflict):
            store.append(event("event.2", task="task.2"))

    def test_context_limit_cannot_exceed_schema_bound(self):
        with self.assertRaises(ValueError):
            StateStore(max_context_refs=65)

    def test_append_increments_revision_and_snapshots_refs(self):
        store = StateStore()
        first = store.append(event("event.1", refs=("artifact://ctx/a",)))
        second = store.append(event("event.2", revision=1, refs=("artifact://ctx/a", "artifact://ctx/b")))
        self.assertEqual(first.revision, 1)
        self.assertEqual(second.revision, 2)
        self.assertEqual(second.context_refs, ("artifact://ctx/a", "artifact://ctx/b"))
        self.assertEqual(len(second.events), 2)

    def test_identical_event_id_is_idempotent(self):
        store = StateStore()
        original = event("event.1")
        first = store.append(original)
        again = store.append(original)
        self.assertEqual(first, again)
        self.assertEqual(store.get("task.1").revision, 1)

    def test_conflicting_event_id_reuse_rejected(self):
        store = StateStore()
        store.append(event("event.1"))
        with self.assertRaises(StateConflict):
            store.append(StateEvent("event.1", "task.1", "principal.writer", "task.updated", "artifact://different", 1))

    def test_event_ids_are_unique_across_tasks(self):
        store = StateStore()
        store.append(event("event.1", task="task.1"))
        with self.assertRaises(StateConflict):
            store.append(event("event.1", task="task.2"))

    def test_stale_revision_rejected(self):
        store = StateStore()
        store.append(event("event.1"))
        with self.assertRaises(StateConflict):
            store.append(event("event.2", revision=0))

    def test_task_capacity_is_bounded(self):
        store = StateStore(max_tasks=1)
        store.append(event("event.1", task="task.1"))
        with self.assertRaises(StateConflict):
            store.append(event("event.2", task="task.2"))

    def test_per_task_event_capacity_is_bounded(self):
        store = StateStore(max_events_per_task=1)
        store.append(event("event.1"))
        with self.assertRaises(StateConflict):
            store.append(event("event.2", revision=1))

    def test_audit_failure_prevents_commit(self):
        def broken(record):
            raise RuntimeError("audit unavailable")
        store = StateStore(audit_sink=broken)
        with self.assertRaises(RuntimeError):
            store.append(event("event.1"))
        with self.assertRaises(KeyError):
            store.get("task.1")

    def test_concurrent_same_revision_only_one_append_wins(self):
        store = StateStore()
        barrier = threading.Barrier(2)
        results = []
        def writer(event_id):
            barrier.wait()
            try:
                store.append(event(event_id, revision=0))
                results.append("committed")
            except StateConflict:
                results.append("conflict")
        threads = [threading.Thread(target=writer, args=(name,)) for name in ("event.a", "event.b")]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertCountEqual(results, ["committed", "conflict"])
        self.assertEqual(store.get("task.1").revision, 1)

    def test_unknown_task_raises_key_error(self):
        with self.assertRaises(KeyError):
            StateStore().get("task.unknown")


if __name__ == "__main__":
    unittest.main()
