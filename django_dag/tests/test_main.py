from django.core.exceptions import ValidationError
from django.test import TestCase
from . import *

class ConcreteNodeTestCase(TestCase):

    def name_num(self, name, num):
        return "%s_%d" % (name, num)

    def create(self, name, num):
        return ConcreteNode.objects.create(name=self.name_num(name, num))

    def create_many(self, name, num):
        return [self.create(name, i) for i in range(0, num)]

    def create_graph(self, name):
        nodes = self.create_many(name, 9)

        nodes[0].add_child(nodes[4])
        nodes[4].add_child(nodes[6])
        nodes[0].add_child(nodes[5])
        nodes[1].add_child(nodes[5])
        nodes[2].add_child(nodes[6])
        nodes[5].add_child(nodes[6])
        nodes[5].add_child(nodes[7])
        nodes[5].add_parent(nodes[3])
        nodes[8].add_parent(nodes[2])
        nodes[8].add_parent(nodes[5])
        return nodes

    def test_descendants(self):
        name = "descendants"
        nodes = self.create_many(name, 3)

        # Descendants tree
        nodes[0].add_child(nodes[1])
        nodes[0].add_child(nodes[2])

        self.assert_(nodes[0].descendants_tree(), [nodes[1], nodes[2]])

        # Descendants sort
        l = [p.name for p in nodes[0].descendants_set()]
        l.sort()
        self.assert_(l, [self.name_num(name, 1), self.name_num(name, 2)])

    def test_ancestors(self):
        name = "ancestors"
        nodes = self.create_many(name, 5)
        
        nodes[0].add_child(nodes[4])
        nodes[1].add_child(nodes[2])
        nodes[2].add_child(nodes[3])
        nodes[3].add_child(nodes[4])

        self.assert_(nodes[4].ancestors_set, [nodes[0], nodes[1], nodes[2], nodes[3]])

        nodes[0].remove_child(nodes[4])
        self.assert_(nodes[4].ancestors_set, [nodes[1], nodes[2], nodes[3]])

    def test_circular_dependencies(self):
        name = "circular"
        nodes = self.create_many(name, 3)

        nodes[0].add_child(nodes[1])
        nodes[1].add_child(nodes[2])

        # Descendants
        with self.assertRaisesRegexp(ValidationError, 'descendant'):
            nodes[0].add_child(nodes[2])

        # Check that it wasn't added
        l = [p.name for p in nodes[0].descendants_set()]
        l.sort()
        self.assert_(l, [self.name_num(name, 1), self.name_num(name, 2)])

        # Ancestors
        with self.assertRaisesRegexp(ValidationError, 'ancestor'):
            nodes[2].add_child(nodes[0])

    def test_complicated_descendants(self):
        name = "complicated_descendants"
        nodes = self.create_graph(name)

        self.assert_(nodes[0].descendants_tree(), [nodes[4], nodes[6], nodes[5], nodes[7], nodes[8], nodes[6]])
        self.assert_(nodes[0].distance(nodes[7]), 2)

    def test_edges(self):
        name = "edges"
        nodes = self.create_graph(name)
        nodes.append(self.create(name, 9))
        nodes[8].add_child(nodes[9], name='test_name')
        self.assert_(nodes[8].children.through.objects.filter(child=nodes[9])[0].name, 'test_name')

        self.assert_(nodes[0].path(nodes[6]), [nodes[5], nodes[6]])
        self.assert_(nodes[0].path(nodes[9]), [nodes[5], nodes[8], nodes[9]])
        self.assert_(nodes[0].distance(nodes[6]), 2)

    def test_root_leaf(self):
        name = "root_leaf"
        nodes = self.create_graph(name)
        nodes.append(self.create(name, 9))
        nodes[8].add_child(nodes[9])

        self.assert_(nodes[0].get_leaves(), set([nodes[7], nodes[9], nodes[6]]))
        self.assert_(nodes[7].get_roots(), set([nodes[0], nodes[1], nodes[3]]))

        self.assertTrue(nodes[0].is_root())
        self.assertFalse(nodes[0].is_leaf())
        self.assertFalse(nodes[9].is_root())
        self.assertTrue(nodes[9].is_leaf())
        self.assertFalse(nodes[5].is_root())
        self.assertFalse(nodes[5].is_leaf())

    def test_self_parent(self):
        name = "self_parent"
        node = self.create(name, 1)
        
        with self.assertRaisesRegexp(ValidationError, 'Self links'):
            node.add_child(node)

        with self.assertRaisesRegexp(ValidationError, 'Self links'):
            node.add_parent(node)

    def test_island(self):
        name = "island"
        nodes = self.create_many(name, 3)

        nodes[0].add_child(nodes[1])
        nodes[1].add_child(nodes[2])
        nodes[2].remove_parent(nodes[1])

        self.assertFalse(nodes[2] in nodes[1].descendants_set())
        self.assertTrue(nodes[2].is_island())

    def test_manager(self):
        name = "manager"
        nodes = self.create_graph(name)

        self.assert_(ConcreteNode.objects.get_roots(), [nodes[0], nodes[1], nodes[2]])
        self.assert_(ConcreteNode.objects.get_leaves(), [nodes[6], nodes[7], nodes[8]])
