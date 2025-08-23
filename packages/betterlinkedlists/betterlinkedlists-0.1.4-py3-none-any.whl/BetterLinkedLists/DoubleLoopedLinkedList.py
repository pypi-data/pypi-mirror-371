from .LoopedLinkedList import LoopedLinkedList
from .DoubleLinkedList import DoubleLinkedList


class DoubleLoopedLinkedList[T](DoubleLinkedList, LoopedLinkedList):
    class DoubleLoopedNode[N_T](
        DoubleLinkedList.DoubleNode, LoopedLinkedList.LoopedNode
    ):
        def __init__(self, data: N_T) -> None:
            self.data: N_T = data
            self.next: DoubleLoopedLinkedList.DoubleLoopedNode[N_T] | None = None
            self.before: DoubleLoopedLinkedList.DoubleLoopedNode[N_T] | None = None

    head: DoubleLoopedNode[T]

    def append(self, data: DoubleLoopedNode[T]):
        new_node = (
            DoubleLoopedLinkedList.DoubleLoopedNode(data)
            if type(data) is not DoubleLoopedLinkedList.DoubleLoopedNode
            else data
        )
        if not self.head:
            self.head = new_node
            new_node.before = self.head
            new_node.next = self.head
            return
        last = self.head
        while last.next is not None and last.next != self.head:
            last = last.next
        last.next = new_node
        new_node.before = last
        new_node.next = self.head
        self.head.before = new_node

    def remove(self, data: DoubleLoopedNode[T]):
        self.find(data)
        for _ in range(len(self.findall(data))):
            if self.head.data == data:
                last = self.head
                while last.next != self.head:
                    last = last.next
                last.next = self.head.next
                self.head = self.head.next
                self.head.before = last
                continue
            last = self.head
            while last.next:
                if last.next.data == data:
                    break
                last = last.next
            last.next = last.next.next
            last.next.next.before = last

    def insert(
        self,
        data: DoubleLoopedNode[T],
        where: bool,
        value: DoubleLoopedNode[T],
    ):
        """
        where = True: insert before
        where = False: insert after
        """
        new_node = (
            DoubleLoopedLinkedList.DoubleLoopedNode(data)
            if type(data) is not DoubleLoopedLinkedList.DoubleLoopedNode
            else data
        )

        if where:
            if self.head == value:
                last = self.head
                while last.next != self.head:
                    last = last.next
                new_node.next = self.head
                new_node.before = last
                last.next = new_node
                self.head = new_node
                new_node.next.before = new_node
                return
            last = self.head
            while last.next:
                if last.next == value:
                    break
                last = last.next
            new_node.next = last.next
            new_node.before = last
            last.next.before = new_node
            last.next = new_node
        else:
            last = self.head
            while last.next:
                if last == value:
                    break
                last = last.next
            last.next.before = new_node
            new_node.next = last.next
            new_node.before = last
            last.next = new_node

    def find(self, value: DoubleLoopedNode[T]) -> DoubleLoopedNode[T]:  # type: ignore[override]
        return super().find(value)

    def findall(self, value: DoubleLoopedNode[T]) -> list[DoubleLoopedNode[T]]:  # type: ignore[override]
        return super().findall(value)

    def __repr__(self):
        r = "DoubleLoopedLinkedList{\n"
        node = self.head
        if node is None:
            return r + "    empty\n}"
        r += (
            f"     (head) data: {node.data}, next: {node.next.data}, before: (tail) {node.before.data}\n"
            if not node.next == self.head
            else f"    (tail) (head) data: {node.data}"
        )
        node = node.next
        if node == self.head:
            r += "\n}"
            return r
        r += (
            f"     data: {node.data}, next: {node.next.data if not node.next.next == self.head else '(tail) ' + node.next.data}, before: {node.before.data if not node.before == self.head else '(head) ' + node.before.data}\n"
            if not node.next == self.head
            else f"     (tail) data: {node.data}, next: (head) {node.next.data}, before: {node.before.data if not node.before == self.head else '(head) ' + node.before.data}"
        )
        while node != self.head:
            node = node.next
            if node == self.head or node is None:
                break
            r += (
                f"     data: {node.data}, next: {node.next.data if not node.next.next == self.head else '(tail) ' + node.next.data}, before: {node.before.data}\n"
                if not node.next == self.head
                else f"     (tail) data: {node.data}, next: (head) {node.next.data}, before: {node.before.data}"
            )
        r += "\n}"
        return r
