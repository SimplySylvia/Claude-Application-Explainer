"""Geometry warnings from engine/diagram.py."""
import sys, unittest

from helpers import ENGINE

sys.path.insert(0, ENGINE)
from diagram import Diagram, mid  # noqa: E402


def warnings(build):
    d = Diagram('t', 1200, 400)
    build(d)
    d.check()
    return d.warn


class DiagramTest(unittest.TestCase):
    def test_clean_layout_has_no_warnings(self):
        def build(d):
            a = d.node('a', 40, 40, 200, 'client', 'monitor', 'Web', ['React'])
            b = d.node('b', 400, 40, 200, 'run', 'server', 'API', ['Express'])
            d.edge([mid(a, 'r'), mid(b, 'l')], 'sync', label='HTTPS')
        self.assertEqual(warnings(build), [])

    def test_overlapping_nodes(self):
        def build(d):
            d.node('a', 40, 40, 200, 'client', 'monitor', 'A')
            d.node('b', 100, 60, 200, 'run', 'server', 'B')
        self.assertTrue(any('overlap' in w for w in warnings(build)))

    def test_diagonal_edge(self):
        def build(d):
            d.edge([(10, 10), (200, 300)], 'sync')
        self.assertTrue(any('diagonal' in w for w in warnings(build)))

    def test_edge_through_node(self):
        def build(d):
            d.node('mid', 300, 40, 200, 'data', 'db', 'DB')
            d.edge([(100, 65), (800, 65)], 'async')
        self.assertTrue(any('passes through mid' in w for w in warnings(build)))

    def test_text_overflow(self):
        def build(d):
            d.node('n', 40, 40, 120, 'ext', 'globe', 'A title that is far too long for this node',
                   ['and a line that is also much too long'])
        w = warnings(build)
        self.assertTrue(any('title overflow' in x for x in w))
        self.assertTrue(any('line overflow' in x for x in w))

    def test_node_outside_canvas(self):
        def build(d):
            d.node('n', 1100, 40, 200, 'ci', 'build', 'CI')
        self.assertTrue(any('outside canvas' in w for w in warnings(build)))


if __name__ == '__main__':
    unittest.main()
