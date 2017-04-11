import unittest

from . import settings
from .data import valid_data
from .data import invalid_data
from craftai.client import CraftAIClient
from craftai import errors as craft_err


class TestListAgents(unittest.TestCase):
    """Checks that the client succeeds when getting an agent with OK input"""
    @classmethod
    def setUpClass(self):
        self.client = CraftAIClient(settings.CRAFT_CFG)
        self.n_agents = 5
        self.agents_id = ['{}_{}_{}'.format(valid_data.VALID_ID, i, settings.RUN_ID) for i in range(self.n_agents)]

    def setUp(self):
        for agent_id in self.agents_id:
            self.client.delete_agent(agent_id)
            self.client.create_agent(valid_data.VALID_CONFIGURATION, agent_id)

    def tearDown(self):
        # Makes sure that no agent with the standard ID remains
        for agent_id in self.agents_id:
            self.client.delete_agent(agent_id)

    def test_list_agents(self):
        """list_agents should returns the list of agents in the current project."""
        agents_list = self.client.list_agents()
        self.assertIsInstance(agents_list, list)
        self.assertTrue(len(agents_list) == self.n_agents)
        for agent_id in self.agents_id:
            self.assertTrue(agent_id in agents_list)
