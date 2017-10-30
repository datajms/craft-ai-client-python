import craftai

from nose.tools import assert_is_instance, assert_not_equal, assert_raises, with_setup

from . import settings
from .data import valid_data
from .data import invalid_data

CLIENT = craftai.Client(settings.CRAFT_CFG)
AGENT_ID = "test_get_decision_tree_" + settings.RUN_ID

def setup_agent_w_operations():
  CLIENT.delete_agent(AGENT_ID)
  CLIENT.create_agent(valid_data.VALID_CONFIGURATION, AGENT_ID)
  CLIENT.add_operations(AGENT_ID, valid_data.VALID_OPERATIONS_SET)

def teardown():
  CLIENT.delete_agent(AGENT_ID)

@with_setup(setup_agent_w_operations, teardown)
def test_get_decision_tree_with_correct_input():
  decision_tree = CLIENT.get_decision_tree(
    AGENT_ID,
    valid_data.VALID_TIMESTAMP)

  assert_is_instance(decision_tree, dict)
  assert_not_equal(decision_tree.get("_version"), None)
  assert_not_equal(decision_tree.get("configuration"), None)
  assert_not_equal(decision_tree.get("trees"), None)

@with_setup(setup_agent_w_operations, teardown)
def test_get_decision_tree_with_invalid_id():
  """get_decision_tree should fail when given a non-string/empty string ID

  It should raise an error upon request for retrieval of an agent's
  decision tree with an ID that is not of type string, since agent IDs
  should always be strings.
  """
  for empty_id in invalid_data.UNDEFINED_KEY:
    assert_raises(
      craftai.errors.CraftAiBadRequestError,
      CLIENT.get_decision_tree,
      invalid_data.UNDEFINED_KEY[empty_id],
      valid_data.VALID_TIMESTAMP)

@with_setup(setup_agent_w_operations, teardown)
def test_get_decision_tree_with_unknown_id():
  """get_decision_tree should fail when given an unknown agent ID

  It should raise an error upon request for the retrieval of an agent
  that doesn't exist.
  """
  assert_raises(
    craftai.errors.CraftAiNotFoundError,
    CLIENT.get_decision_tree,
    invalid_data.UNKNOWN_ID,
    valid_data.VALID_TIMESTAMP)

@with_setup(setup_agent_w_operations, teardown)
def test_get_decision_tree_with_invalid_timestamp():
  for inv_ts in invalid_data.INVALID_TIMESTAMPS:
    assert_raises(
      craftai.errors.CraftAiBadRequestError,
      CLIENT.get_decision_tree,
      AGENT_ID,
      invalid_data.INVALID_TIMESTAMPS[inv_ts])
