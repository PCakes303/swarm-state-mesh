import json
import unittest
from dataclasses import asdict
from pathlib import Path

from jsonschema import Draft202012Validator
from swarm_state_mesh import StateEvent, StateValidationError


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas" / "state-event.schema.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(SCHEMA)
SCHEMA_VALIDATOR = Draft202012Validator(SCHEMA)


def valid_event():
    return StateEvent("event.1", "task.1", "principal.1", "task.created", "artifact://event/1", 0, ())


def document(event):
    value = asdict(event)
    value["context_refs"] = list(value["context_refs"])
    return value


class ModelTests(unittest.TestCase):

    def test_event_type_length_is_bounded(self):
        with self.assertRaises(StateValidationError):
            StateEvent("event.1", "task.1", "principal.1", "a" * 65, "artifact://event/1", 0).validate()

    def test_context_limit_argument_cannot_exceed_schema_bound(self):
        with self.assertRaises(ValueError):
            valid_event().validate(max_context_refs=65)

    def test_valid_event_and_schema_agree(self):
        event = valid_event()
        event.validate()
        self.assertEqual(list(SCHEMA_VALIDATOR.iter_errors(document(event))), [])

    def test_negative_revision_rejected_by_model_and_schema(self):
        event = StateEvent("event.1", "task.1", "principal.1", "task.created", "artifact://event/1", -1)
        with self.assertRaises(StateValidationError):
            event.validate()
        self.assertTrue(list(SCHEMA_VALIDATOR.iter_errors(document(event))))

    def test_boolean_revision_rejected_by_model_and_schema(self):
        event = StateEvent("event.1", "task.1", "principal.1", "task.created", "artifact://event/1", True)
        with self.assertRaises(StateValidationError):
            event.validate()
        self.assertTrue(list(SCHEMA_VALIDATOR.iter_errors(document(event))))

    def test_context_references_must_be_tuple_in_model_and_array_in_schema(self):
        with self.assertRaises(StateValidationError):
            StateEvent("event.1", "task.1", "principal.1", "task.created", "artifact://event/1", 0, ["artifact://context/1"]).validate()
        invalid = document(valid_event())
        invalid["context_refs"] = "artifact://context/1"
        self.assertTrue(list(SCHEMA_VALIDATOR.iter_errors(invalid)))

    def test_invalid_event_type_rejected_by_model_and_schema(self):
        event = StateEvent("event.1", "task.1", "principal.1", "Task Created", "artifact://event/1", 0)
        with self.assertRaises(StateValidationError):
            event.validate()
        self.assertTrue(list(SCHEMA_VALIDATOR.iter_errors(document(event))))

    def test_identifier_length_boundaries_match_schema(self):
        event = StateEvent("e" * 129, "task.1", "principal.1", "task.created", "artifact://event/1", 0)
        with self.assertRaises(StateValidationError):
            event.validate()
        self.assertTrue(list(SCHEMA_VALIDATOR.iter_errors(document(event))))

    def test_whitespace_only_references_rejected_by_both(self):
        event = StateEvent("event.1", "task.1", "principal.1", "task.created", "   ", 0)
        with self.assertRaises(StateValidationError):
            event.validate()
        self.assertTrue(list(SCHEMA_VALIDATOR.iter_errors(document(event))))
        event = StateEvent("event.1", "task.1", "principal.1", "task.created", "artifact://event/1", 0, ("   ",))
        with self.assertRaises(StateValidationError):
            event.validate()
        self.assertTrue(list(SCHEMA_VALIDATOR.iter_errors(document(event))))

    def test_context_count_and_length_bounds_match_schema(self):
        too_many = StateEvent("event.1", "task.1", "principal.1", "task.created", "artifact://event/1", 0, tuple(f"ref:{i}" for i in range(65)))
        with self.assertRaises(StateValidationError):
            too_many.validate()
        self.assertTrue(list(SCHEMA_VALIDATOR.iter_errors(document(too_many))))
        too_long = StateEvent("event.1", "task.1", "principal.1", "task.created", "artifact://event/1", 0, ("x" * 513,))
        with self.assertRaises(StateValidationError):
            too_long.validate()
        self.assertTrue(list(SCHEMA_VALIDATOR.iter_errors(document(too_long))))

    def test_schema_rejects_unknown_properties(self):
        candidate = document(valid_event())
        candidate["unexpected"] = True
        self.assertTrue(list(SCHEMA_VALIDATOR.iter_errors(candidate)))


if __name__ == "__main__":
    unittest.main()
