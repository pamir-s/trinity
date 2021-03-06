import asyncio

import pytest

from trinity.tools.bcc_factories import NodeFactory


@pytest.mark.parametrize("num_nodes", (1,))
@pytest.mark.asyncio
async def test_node(nodes):
    node = nodes[0]
    expected_addrs = [node.listen_maddr_with_peer_id]
    assert node.host.get_addrs() == expected_addrs


@pytest.mark.parametrize("num_nodes", (3,))
@pytest.mark.asyncio
async def test_node_dial_peer_maddr(nodes):
    # Test: 0 <-> 1
    await nodes[0].dial_peer_maddr(nodes[1].listen_maddr, nodes[1].peer_id)
    assert nodes[0].peer_id in nodes[1].host.get_network().connections
    assert nodes[1].peer_id in nodes[0].host.get_network().connections
    # Test: Second dial to a connected peer does not open a new connection
    original_conn = nodes[1].host.get_network().connections[nodes[0].peer_id]
    await nodes[0].dial_peer_maddr(nodes[1].listen_maddr, nodes[1].peer_id)
    assert nodes[1].host.get_network().connections[nodes[0].peer_id] is original_conn
    # Test: 0 <-> 1 <-> 2
    await nodes[1].dial_peer_maddr(nodes[2].listen_maddr, nodes[2].peer_id)
    await nodes[1].dial_peer_maddr(nodes[0].listen_maddr, nodes[0].peer_id)
    assert nodes[1].peer_id in nodes[2].host.get_network().connections
    assert nodes[2].peer_id in nodes[1].host.get_network().connections
    assert nodes[1].peer_id in nodes[0].host.get_network().connections
    assert nodes[0].peer_id in nodes[1].host.get_network().connections


@pytest.mark.parametrize("num_nodes", (2,))
@pytest.mark.asyncio
async def test_node_connect_preferred_nodes(nodes):
    new_node = NodeFactory(
        preferred_nodes=[node.listen_maddr_with_peer_id for node in nodes]
    )
    asyncio.ensure_future(new_node.run())
    await new_node.events.started.wait()
    assert len(new_node.host.get_network().connections) == 0
    await new_node.connect_preferred_nodes()
    assert len(new_node.host.get_network().connections) == len(nodes)
