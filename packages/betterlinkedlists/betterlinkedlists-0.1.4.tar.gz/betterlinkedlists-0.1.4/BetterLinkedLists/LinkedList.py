from typing import Any, Self

BEFORE = True
AFTER = False


class ItemNotFoundError(Exception):
    """
    Item does not appear in the LinkedList.
    """

    pass


class LinkedListType[T]:
    class NodeType[N_T]:
        def __init__(self, data: N_T) -> None:
            self.data: N_T
            self.next: LinkedListType.NodeType[N_T]
            self.before: LinkedListType.NodeType[N_T]

        def __eq__(self, other):
            if isinstance(other, LinkedListType.NodeType[N_T]):
                return self.data == other.data
            else:
                return self.data == other

        def __str__(self):
            return str(self.data)

    head: NodeType[T] | None = None

    def find(self, item: Any | NodeType[T]) -> NodeType[T]:
        return LinkedListType.NodeType()

    def findall(self, item: Any | NodeType[T]) -> list[NodeType[T]]:
        return [LinkedListType.NodeType()]

    def append(self, item: Any | NodeType[T]):
        pass

    def remove(self, item: Any | NodeType[T]):
        pass

    def insert(self, data: Any | NodeType[T], where: bool, value: Any | NodeType[T]):
        pass

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> Any:
        raise TypeError(f"{self} is not subscriptable")

    def __len__(self) -> int:
        return -1

    def __getitem__(self, n) -> NodeType[T]:
        raise TypeError(f"{self} is not subscriptable")

    def __eq__(self, other) -> bool:
        return False

    def __repr__(self) -> str:
        return f"<{__name__}.LinkedListType object at {id(self)}>"


class LinkedList[T](LinkedListType):
    class Node[N_T](LinkedListType.NodeType):
        def __init__(self, data: N_T) -> None:
            self.data: N_T = data
            self.next: LinkedList.Node[N_T] = None

    head: Node[T]

    def __init__(self, *args) -> None:
        self._iter_node = None
        if len(args) == 1 and isinstance(args[0], (tuple, list)):
            if len(args[0]) == 0:
                self.head = None
                return
            self.head = LinkedList.Node(args[0][0])
            for item in iter(args[0]):
                self.append(item)
        else:
            if len(args) == 0:
                self.head = None
                return
            self.head = LinkedList.Node(args[0])
            for item in args:
                self.append(item)

    def append(self, data: Any | Node[T]):
        new_node = LinkedList.Node(data) if type(data) is not LinkedList.Node else data
        if not self.head:
            self.head = new_node
            return
        last = self.head
        while last.next:
            last = last.next
        last.next = new_node

    def insert(self, data: Any | Node[T], where: bool, value: Any | Node[T]):
        """
        where = True: insert before
        where = False: insert after
        """
        try:
            self.find(value)
            assert self.head is not None
        except (ItemNotFoundError, AssertionError):
            raise ItemNotFoundError(
                f"Cannot insert {'before' if where else 'after'} '{str(value)}': '{str(value)}' is not a member of the LinkedList."
            )
        new_node = LinkedList.Node(data) if type(data) is not LinkedList.Node else data

        if where:
            if self.head == value:
                new_node.next = self.head
                self.head = new_node
                return
            last = self.head
            while last.next is not None:
                if last.next == value or last.next.next is None:
                    break
                last = last.next
            new_node.next = last.next
            last.next = new_node
            return
        else:
            last = self.head
            while last.next is not None:
                if last == value or last.next is None:
                    break
                last = last.next
            new_node.next = last.next
            last.next = new_node
            return

    def remove(self, data: Any | Node[T]):
        for _ in range(len(self.findall(data))):
            try:
                self.find(data)
                assert self.head is not None
            except (ItemNotFoundError, AssertionError):
                raise ItemNotFoundError("The item was not found in the LinkedList.")
            if data == self.head:
                self.head = self.head.next
                continue
            last = self.head
            while last.next is not None:
                if data == last.next or last.next is None:
                    break
                last = last.next
            if last.next is not None:
                last.next = last.next.next
        return

    def __iter__(self):
        self._iter_node = self.head
        self._iter_started = False
        return self

    def __next__(self):
        if self._iter_node is None or (
            self._iter_node == self.head and self._iter_started
        ):
            self._iter_node = self.head
            self._iter_started = False
            raise StopIteration
        data = self._iter_node.data
        self._iter_node = self._iter_node.next
        self._iter_started = True
        return data

    def __len__(self):
        count = 0
        for _ in self:
            count += 1
        return count

    def __getitem__(self, n):
        if n < 0:
            n = len(self) + n
        node = self.head
        idx = 0
        while node:
            if idx == n:
                return node
            node = node.next
            idx += 1
            if node == self.head or node is None:
                break
        raise IndexError("LinkedList index out of range")

    def find(self, value: Any | Node[T]) -> Node[T]:
        node = self.head
        while node:
            if node == value:
                return node
            node = node.next
            if node is self.head or node is None:
                break
        raise ItemNotFoundError("The item was not found in the LinkedList.")

    def findall(self, value: Any | Node[T]) -> list[Node[T]]:
        self.find(value)
        nodes = []
        node = self.head
        while node is not None:
            if node == value:
                nodes.append(node)
            node = node.next
            if node is self.head or node is None:
                break
        return nodes

    def __eq__(self, other):
        if not isinstance(other, LinkedListType):
            return False

        if len(self) != len(other):
            return False

        return all([self[i] == other[i] for i in range(len(self))])

    def __repr__(self):
        r = "LinkedList{\n"
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
                f"     data: {node.data}, next: {node.next.data if node.next.next is not None else '(tail) ' + node.next.data}\n"
                if node.next is not None
                else f"     (tail) data: {node.data}"
            )
        r += "\n}"
        return r
