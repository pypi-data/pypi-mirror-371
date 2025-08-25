"""
This module contains the event to run the aggregate program in the simulator
"""
from abc import ABC

from phyelds.internal import MutableEngine

from phyelds import engine
from phyelds.abstractions import NodeContext
from phyelds.data import State
from phyelds.simulator import Simulator, Node


class SimulatorNodeContext(NodeContext, ABC):
    """
    A class to represent the context of a node in the simulator.
    This class is used to pass the node's data and messages to the aggregate program.
    """

    @staticmethod
    def from_node(node: Node):
        """
        Create a SimulatorNodeContext from a Node.
        :param node: The node to create the context from.
        :return: The SimulatorNodeContext.
        """
        sensors = {
            "position": node.position,
            **node.data,
        }
        return SimulatorNodeContext(node.id, sensors)


def aggregate_program_runner(
    simulator: Simulator, time_delta: float, node: Node, program: callable, **kwargs
):
    """
    Run the program for a node.
    """
    if node.id not in simulator.environment.nodes.keys():
        # If the node is not in the environment, do not run the program
        return
    # get neighbors
    all_neighbors = simulator.environment.get_neighbors(node)
    # take the messages from the neighbors, create a dict like id -> messages (that is a dict)
    neighbors_messages = {
        neighbor.id: neighbor.data.get("messages", {}) for neighbor in all_neighbors
    }
    engine.set(MutableEngine())
    engine.get().setup(
        SimulatorNodeContext.from_node(node),
        neighbors_messages,
        node.data.get("state", {})
    )
    result = program(**kwargs)
    if isinstance(result, State):
        result = result.value
    node.data["result"] = result
    node.data["messages"] = engine.get().cooldown()
    node.data["state"] = engine.get().state_trace()
    node.data["outputs"] = engine.get().node_context.outputs
    simulator.schedule_event(
        time_delta, aggregate_program_runner, simulator, time_delta, node, program, **kwargs
    )


def schedule_program_for_all(simulator: Simulator, frequency: float, program: callable, **kwargs):
    """
    Schedule the program for all nodes in the simulator.
    :param simulator: The simulator to schedule the program for.
    :param frequency: The frequency to run the program.
    :param program: The program to run.
    """
    for node in simulator.environment.nodes.values():
        simulator.schedule_event(
            frequency, aggregate_program_runner, simulator, frequency, node, program, **kwargs
        )
