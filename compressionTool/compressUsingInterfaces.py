import abc
import collections
import functools
import heapq
from functools import total_ordering


class HuffmanBaseNode(abc.ABC):
    def is_leaf(self) -> bool:
        pass

    @property
    @abc.abstractmethod
    def weight(self) -> int:
        pass


@total_ordering
class HuffmanLeafNode(HuffmanBaseNode):

    def __init__(self, element: str, weight: int):
        self.__element = element
        self.__weight = weight

    @property
    def weight(self) -> int:
        return self.__weight

    @property
    def element(self) -> str:
        return self.__element

    def is_leaf(self) -> bool:
        return True

    def __lt__(self, other: HuffmanBaseNode):
        return self.weight < other.weight


@total_ordering
class HuffmanInternalNode(HuffmanBaseNode):
    def __init__(self, left: HuffmanBaseNode, right: HuffmanBaseNode, weight: int):
        self.__left = left
        self.__right = right
        self.__weight = weight

    @property
    def weight(self) -> int:
        return self.__weight

    @property
    def left(self) -> HuffmanBaseNode:
        return self.__left

    @property
    def right(self) -> HuffmanBaseNode:
        return self.__right

    def is_leaf(self) -> bool:
        return False

    def __lt__(self, other: HuffmanBaseNode):
        return self.weight < other.weight


@total_ordering
class HuffmanTree:

    def __init__(self, weight: int, element: str = None):
        self.__root: HuffmanLeafNode = HuffmanLeafNode(element, weight)

    @functools.singledispatchmethod
    def __init__(self, weight: int, left: HuffmanBaseNode = None, right: HuffmanBaseNode = None):
        self.__root: HuffmanInternalNode = HuffmanInternalNode(left, right, weight)

    @property
    def root(self) -> HuffmanBaseNode:
        return self.__root

    @property
    def weight(self) -> int:
        return self.__root.weight

    def __eq__(self, other: HuffmanBaseNode):
        return self.weight == other.weight

    def __lt__(self, other: HuffmanBaseNode):
        return self.weight < other.weight


def build_tree(pq):
    temp3 = None
    while len(pq) > 1:
        temp1 = heapq.heappop(pq)
        temp2 = heapq.heappop(pq)
        temp3 = HuffmanTree(temp1.weight + temp2.weight, temp1, temp2)
        heapq.heappush(pq, temp3)
    return temp3


def traverse(root: HuffmanBaseNode, prefix="", indent=""):
    if not root:
        return

    if isinstance(root, HuffmanLeafNode):
        print(f"{indent}Leaf: {root.element} ({root.weight}) Code: ({prefix})")

    if isinstance(root, HuffmanInternalNode):
        traverse(root.left, prefix + "0", indent + "  ")
        traverse(root.right, prefix + "1", indent + "  ")

    if isinstance(root, HuffmanTree):
        traverse(root.root, prefix, indent)


def main():
    text = "aaabbcccccddeffffghhh"
    character_counts = collections.Counter(text)
    pq = []
    for character, count in character_counts.items():
        heapq.heappush(pq, HuffmanLeafNode(element=character, weight=count))
    root = build_tree(pq)
    traverse(root)


if __name__ == "__main__":
    main()
