from pprint import pprint
from typing import List, Tuple, TypeVar, Set, Dict

import numpy as np

T = TypeVar('T')


class BaseTraversalException(ValueError):
    """Base exception for traversal"""


class NoPathException(BaseTraversalException):
    """Throw when no path can be found"""


class RevisitingNodeException(BaseTraversalException):
    """Throw when visiting a node that was already visited"""


class Matrix:
    def __init__(
            self,
            connections: List[Tuple[T, T]],
            is_bidirectional: bool = True):
        self._is_bidirectional = is_bidirectional
        elements = self._get_unique_elements(connections)
        self._elements: Dict[T, int] = {e: i for i, e in enumerate(elements)}
        self._index_to_elements = {i: e for e, i in self._elements.items()}

        self.connections = connections
        self._size = len(self._elements)
        self._matrix = np.zeros((self._size, self._size), dtype=bool)
        self._insert_connections()
        pprint(self._elements.keys())
        pprint(self._matrix)

    @staticmethod
    def _get_unique_elements(connections: List[Tuple[T, T]]) -> Set[T]:
        elements = set()
        for connection in connections:
            elements.add(connection[0])
            elements.add(connection[1])
        return elements

    def _insert_connections(self):
        for i in range(self._size):
            self._matrix[i][i] = True
        for connection in self.connections:
            from_element_index = self._elements[connection[0]]
            to_element_index = self._elements[connection[1]]
            self._matrix[from_element_index][to_element_index] = True
            if self._is_bidirectional:
                self._matrix[to_element_index][from_element_index] = True

    def _check_membership(self, a: T):
        if a not in self._elements.keys():
            raise ValueError("'%s' not in the matrix" % a)

    def are_connected(self, a: T, b: T) -> bool:
        path = self.find_path_from_to(a, b)
        if path:
            return True
        else:
            return False

    def find_path_from_to(self, a: T, b: T) -> List[T]:
        self._check_membership(a)
        self._check_membership(b)
        try:
            path = self._get_path_from_to(a, b, None, None)
        except NoPathException:
            print("No path found")
            raise NoPathException("No path: '%s' to '%s'" % (a, b)) from None
        return path

    def _get_path_from_to(
            self, a: T, b: T,
            path: List[T] = None,
            already_visited: Set[T] = None
    ) -> List[T]:
        print("Trying to find from '%s' to '%s', path: '%s'" % (a, b, path))
        if path is None:
            path = []
        path.append(a)
        if a == b:
            print("Returning same")
            return path

        if already_visited is not None and a in already_visited:
            print("Already visited: '%s', path is: '%s'" % (a, path))
            raise RevisitingNodeException("Visiting '%s' again" % a)

        if already_visited is None:
            already_visited = set()
        already_visited.add(a)

        new_to_visits = self._find_next_steps(a, already_visited)
        print("Checking '%s', visited: '%s'" % (new_to_visits, already_visited))
        for new_to in new_to_visits:
            try:
                path = self._get_path_from_to(new_to, b, path, already_visited)
            except BaseTraversalException as e:
                print("Some error: '%s'" % e)
                continue
            if path:
                return path
        raise NoPathException("No path from '%s' to '%s'" % (a, b))

    def _find_next_steps(self, a: T, already_visited: Set[T]) -> Set[T]:
        index = self._elements[a]
        new_to_visits = set()
        for i, value in enumerate(self._matrix[index]):
            if bool(value) is True:
                new_to = self._index_to_elements[i]
                if new_to == a:
                    continue
                new_to_visits.add(new_to)
        new_to_visits = new_to_visits.difference(already_visited)

        return new_to_visits

    def are_connected_bfs(self, a: T, b: T) -> bool:
        self._check_membership(a)
        self._check_membership(b)
        to_visit = []
        already_visited = set(a)
        new_to_visits = self._find_next_steps(a, already_visited)
        to_visit.extend(new_to_visits)
        while to_visit:
            new_to = to_visit.pop(0)
            already_visited.add(new_to)
            new_to_visits = self._find_next_steps(new_to, already_visited)
            if b in new_to_visits:
                return True
            to_visit.extend(new_to_visits)
        return False

