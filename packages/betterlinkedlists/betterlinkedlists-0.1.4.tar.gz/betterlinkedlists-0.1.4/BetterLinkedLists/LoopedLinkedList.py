from .LinkedList import LinkedList


class LoopedLinkedList[T](LinkedList):
    class LoopedNode[N_T](LinkedList.Node):
        def __init__(self, data: N_T) -> None:
            self.data: N_T = data
            self.next: LoopedLinkedList.LoopedNode[N_T] | None

    head: LoopedNode[T]

    def append(self, data: LoopedNode[T]):
        new_node = (
            LoopedLinkedList.LoopedNode(data)
            if type(data) is not LoopedLinkedList.LoopedNode
            else data
        )
        if not self.head:
            self.head = new_node
            new_node.next = self.head
            return
        last = self.head
        while last.next is not self.head:
            last = last.next
        last.next = new_node
        new_node.next = self.head

    def remove(self, data: LoopedNode[T]):
        self.find(data)
        for _ in range(len(self.findall(data))):
            if self.head == data:
                last = self.head
                while last.next != self.head:
                    last = last.next
                last.next = self.head.next
                self.head = self.head.next
                continue
            last = self.head
            while last.next:
                if last.next == data:
                    break
                last = last.next
            last.next = last.next.next

    def insert(self, data: LoopedNode[T], where: bool, value: LoopedNode[T]):
        """
        where = True: insert before
        where = False: insert after
        """
        new_node = (
            LoopedLinkedList.LoopedNode(data)
            if type(data) is not LoopedLinkedList.LoopedNode
            else data
        )

        if where:
            if self.head == value:
                last = self.head
                while last.next != self.head:
                    last = last.next
                new_node.next = self.head
                last.next = new_node
                self.head = new_node
                return
            last = self.head
            while last.next:
                if last.next == value:
                    break
                last = last.next
            new_node.next = last.next
            last.next = new_node
        else:
            last = self.head
            while last.next:
                if last == value:
                    break
                last = last.next
            new_node.next = last.next
            last.next = new_node

    def find(self, value: LoopedNode[T]) -> LoopedNode[T]:  # type: ignore[override]
        return super().find(value)

    def findall(self, value: LoopedNode[T]) -> list[LoopedNode[T]]:  # type: ignore[override]
        return super().findall(value)

    def __repr__(self):
        r = "LoopedLinkedList{\n"
        node = self.head
        if node is None:
            return r + "    empty\n}"
        r += (
            f"     (head) data: {node.data}, next: {node.next.data if not node.next.next == self.head else '(tail) ' + node.next.data}\n"
            if not node.next == self.head
            else f"    (tail) (head) data: {node.data}"
        )
        node = node.next
        if node.next == self.head:
            r += "\n}"
            return r
        r += (
            f"     data: {node.data}, next: {node.next.data if not node.next.next == self.head else '(tail) ' + node.next.data}\n"
            if not node.next == self.head
            else f"     (tail) data: {node.data}, next: (head) {node.next.data}"
        )
        while node != self.head:
            node = node.next
            if node == self.head or node is None:
                break
            r += (
                f"     data: {node.data}, next: {node.next.data if not node.next.next == self.head else '(tail) ' + node.next.data}\n"
                if not node.next == self.head
                else f"     (tail) data: {node.data}, next: (head) {node.next.data}"
            )
        r += "\n}"
        return r
