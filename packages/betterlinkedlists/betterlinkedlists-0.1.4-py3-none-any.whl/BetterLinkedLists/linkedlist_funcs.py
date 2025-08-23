from .LinkedList import LinkedListType
from .DoubleLoopedLinkedList import DoubleLoopedLinkedList


def jump[T](
    ll: DoubleLoopedLinkedList[T],
    start_value: DoubleLoopedLinkedList.DoubleLoopedNode[T] | T,
    jumps: int,
) -> DoubleLoopedLinkedList.DoubleLoopedNode[T]:
    node = ll.find(start_value)
    if jumps >= 0:
        for _ in range(jumps):
            if node is None:
                return None
            node = node.next
    else:
        for _ in range(-jumps):
            if node is None:
                return None
            node = node.before
    return node


def has_duplicates[T](linkedlist: LinkedListType[T]) -> bool:
    seen = set()
    for value in linkedlist:
        if value in seen:
            return True
        seen.add(value)
    return False


def reverse[T](linkedlist: LinkedListType[T]) -> LinkedListType[T]:
    new_ll = type(linkedlist)()
    node = linkedlist.head
    nodes = []
    while node:
        nodes.append(node.data)
        node = node.next
        if node == linkedlist.head or node is None:
            break
    for data in reversed(nodes):
        new_ll.append(data)
    return new_ll
