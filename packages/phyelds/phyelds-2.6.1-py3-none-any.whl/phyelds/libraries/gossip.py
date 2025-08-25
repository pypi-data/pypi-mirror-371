"""
Gossip Library.
Set of operation in order to gossip information between nodes in the network.
"""
from phyelds.libraries.distances import hops_distance
from phyelds.libraries.spreading import cast_from

from phyelds.calculus import aggregate, remember, neighbors, align
from phyelds.libraries.device import local_id


@aggregate
def gossip_max(value: float) -> float:
    """
    Gossip the maximum value among the all system
    :param value: The value to gossip.
    :return: The maximum value among the all system.
    """
    return gossip(value, max)


@aggregate
def gossip_min(value: float) -> float:
    """
    Gossip the minimum value among the all system
    :param value: The value to gossip.
    :return: The minimum value among the all system.
    """
    return gossip(value, min)


@aggregate
def gossip(value: any, callback: callable) -> any:
    """
    Gossip a value in the network using a callable function to choice the value to gossip.
    :param value: The value to gossip.
    :param callback: The callback function to apply on the value.
    :return: The gossiped value.
    """
    gossip_value = remember(value)
    neighborhood_value = neighbors(gossip_value)
    # Apply the callback function to the value
    new_value = callback(value, *neighborhood_value)
    return gossip_value.update(new_value)


@aggregate
def stabilizing_gossip(value: any, max_diameter: int, callback: callable) -> any:
    """
    Gossip a value in the network using a callable function to choice the value to gossip.
    This function will stabilize the gossip value by applying the callback function until
    no changes are made.
    :param value: The value to gossip.
    :param max_diameter: The maximum diameter to consider for gossiping.
    :param callback: The callback function to apply on the value.
    :return: The stabilized gossiped value.
    """
    all_ids = gossip({local_id()}, set.union)
    all_data = {}
    for node_id in all_ids:
        with align(node_id):
            # Gossip the value from the node with the given id
            all_data[node_id] = cast_from(
                local_id() == node_id,
                (value, 0),
                lambda x: (x[0], x[1] + 1),
                hops_distance()
            )
    # filter the data with the maximum diameter
    filtered_data = {k: v for k, v in all_data.items() if v[1] <= max_diameter}
    # get only the values
    filtered_values = [v[0] for v in filtered_data.values()]
    # Apply the callback function to the value
    return callback(value, *filtered_values)
