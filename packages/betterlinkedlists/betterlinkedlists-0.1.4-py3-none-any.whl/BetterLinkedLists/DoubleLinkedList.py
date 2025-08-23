from .LinkedList import LinkedList


class DoubleLinkedList[T](LinkedList):
    class DoubleNode[N_T](LinkedList.Node):
        def __init__(self, data: N_T) -> None:
            self.data: N_T = data
            self.before: DoubleLinkedList.DoubleNode[N_T] | None = None
            self.next: DoubleLinkedList.DoubleNode[N_T] | None = None

    head: DoubleNode[T]

    def append(self, data: DoubleNode[T]):
        new_node = (
            DoubleLinkedList.DoubleNode(data)
            if type(data) is not DoubleLinkedList.DoubleNode
            else data
        )
        if not self.head:
            self.head = new_node
            return
        last = self.head
        while last.next:
            last = last.next
        last.next = new_node
        new_node.before = last

    def remove(self, data: DoubleNode[T]):
        self.find(data)
        for _ in range(len(self.findall(data))):
            if self.head == data:
                del self.head.next.before
                self.head = self.head.next
                continue
            last = self.head
            while last.next:
                if last.next == data:
                    break
                last = last.next
            if last.next.next is not None:
                last.next.next.before = last
            last.next = last.next.next

    def insert(self, data: DoubleNode[T], where: bool, value: DoubleNode[T]):
        """
        where = True: insert before
        where = False: insert after
        """
        new_node = (
            DoubleLinkedList.DoubleNode(data)
            if type(data) is not DoubleLinkedList.DoubleNode
            else data
        )

        if where:
            last = self.head
            while last.next:
                if last.next == value:
                    break
                last = last.next
            new_node.next = last.next
            new_node.next.before = new_node
            new_node.before = last
            last.next = new_node
        else:
            last = self.head
            while last.next:
                if last == value:
                    break
                last = last.next
            new_node.next = last.next
            new_node.next.before = new_node
            new_node.before = last
            last.next = new_node

    def find(self, value: DoubleNode[T]) -> DoubleNode[T]:  # type: ignore[override]
        return super().find(value)

    def findall(self, value: DoubleNode[T]) -> list[DoubleNode[T]]:  # type: ignore[override]
        return super().findall(value)

    def __repr__(self):
        r = "DoubleLinkedList{\n"
        node = self.head
        if node is None:
            return r + "    empty\n}"
        r += (
            f"     (head) data: {node.data}, next: {node.next.data if node.next.next is not None else '(tail) ' + node.next.data}\n"
            if node.next is not None
            else f"    (tail) (head) data: {node.data}"
        )
        while node:
            node = node.next
            if node == self.head or node is None:
                break
            r += (
                f"     data: {node.data}, next: {node.next.data if node.next.next is not None else '(tail) ' + node.next.data}, before: {node.before.data if not node.before == self.head else '(head) ' + node.before.data}\n"
                if node.next is not None
                else f"     (tail) data: {node.data}, before: {node.before.data}"
            )
        r += "\n}"
        return r
