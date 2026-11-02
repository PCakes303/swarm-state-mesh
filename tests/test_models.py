import unittest
from swarm_state_mesh import StateEvent, StateValidationError


class ModelTests(unittest.TestCase):

    def test_event_type_length_is_bounded(self):
        with self.assertRaises(StateValidationError):
            StateEvent("event.1", "task.1", "principal.1", "a" * 65, "artifact://event/1", 0).validate()

    def test_context_limit_argument_cannot_exceed_schema_bound(self):
        with self.assertRaises(ValueError):
            StateEvent("event.1", "task.1", "principal.1", "task.created", "artifact://event/1", 0).validate(max_context_refs=65)

    def test_valid_event(self):
        StateEvent("event.1", "task.1", "principal.1", "task.created", "artifact://event/1", 0).validate()

    def test_negative_revision_rejected(self):
        with self.assertRaises(StateValidationError):
            StateEvent("event.1", "task.1", "principal.1", "task.created", "artifact://event/1", -1).validate()

    def test_boolean_revision_rejected(self):
        with self.assertRaises(StateValidationError):
            StateEvent("event.1", "task.1", "principal.1", "task.created", "artifact://event/1", True).validate()

    def test_context_references_must_be_tuple(self):
        with self.assertRaises(StateValidationError):
            StateEvent("event.1", "task.1", "principal.1", "task.created", "artifact://event/1", 0, ["artifact://context/1"]).validate()

    def test_invalid_event_type_rejected(self):
        with self.assertRaises(StateValidationError):
            StateEvent("event.1", "task.1", "principal.1", "Task Created", "artifact://event/1", 0).validate()


if __name__ == "__main__":
    unittest.main()
