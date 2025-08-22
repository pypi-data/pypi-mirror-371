"""
Writer-side UMAA decorators:

- :class:`GenSpecWriter` — path-aware generalization/specialization (UMAA 3.9).
- :class:`LargeSetWriter` — publish sets and update metadata markers (UMAA 3.8).
- :class:`LargeListWriter` — publish lists, link nextElementID, update markers (UMAA 3.8).

These decorators automatically allocate IDs (when missing) using :func:`generate_guid`
and spawn child builders per element so arbitrary nesting continues to work.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence, Tuple, List

from umaapy.util.multi_topic_support import (
    CombinedBuilder,
    get_at_path,
    path_for_set_element,
    path_for_list_element,
)
from umaapy.util.multi_topic_writer import WriterDecorator, WriterNode

from umaapy.util.umaa_utils import topic_from_type

from umaapy.util.uuid_factory import generate_guid, NIL_GUID


class GenSpecWriter(WriterDecorator):
    """
    Path-aware UMAA Generalization/Specialization writer.

    Parameters
    ----------
    attr_path : Sequence[str], optional
        Where the generalization object lives inside the base (e.g., ``('objective',)``).
    resolve_child_by_topic_name : Callable[[str], str], optional
        Optional mapping hook to resolve child names when specialization topics differ.
    """

    def __init__(self, attr_path: Sequence[str] = ()):
        super().__init__()
        self.attr_path: Tuple[str, ...] = tuple(attr_path)
        self._children: Dict[str, WriterNode] = {}

    def attach_children(self, **children: WriterNode) -> None:
        super().attach_children(**children)
        self._children = getattr(self, "_children", {})

    @staticmethod
    def _spec_identity(spec: Any):
        return getattr(spec, "specializationReferenceID"), getattr(spec, "specializationReferenceTimestamp")

    @staticmethod
    def _spec_topic_name(spec: Any) -> str:
        return topic_from_type(type(spec))

    @staticmethod
    def _bind_generalization(gen: Any, topic: str, spec_id: Any, spec_ts: Optional[Any]) -> None:
        setattr(gen, "specializationTopic", topic)
        setattr(gen, "specializationID", spec_id)
        if spec_ts is not None:
            setattr(gen, "specializationTimestamp", spec_ts)

    def publish(self, node: WriterNode, builder: CombinedBuilder) -> None:

        spec = builder.overlays_by_path.get(self.attr_path)
        gen_obj = get_at_path(builder.base, self.attr_path)

        if spec is None:
            return

        topic = self._spec_topic_name(spec)
        child = self._children.get(topic)
        if child is None:
            raise RuntimeError(f"GenSpecWriter: no child WriterNode for specialization topic '{topic}'")

        # Ensure specialization ID/topic exist
        if getattr(spec, "specializationReferenceID") == NIL_GUID:
            setattr(spec, "specializationReferenceID", generate_guid())

        # child.publish(CombinedBuilder(base=spec, collections_by_path=builder.collections_by_path))
        print(f"Gen/Spec attr_path: {self.attr_path}")
        child.publish(builder.spawn_child(spec, self.attr_path))

        sid, sts = self._spec_identity(spec)
        self._bind_generalization(gen_obj, topic, sid, sts)

        # Best-effort propagate common simple fields from specialization to generalization
        # Copy any scalar attributes that exist on both objects (e.g., 'name') so reads resolve properly.
        try:
            # Prefer attributes defined on the generalization; take values from spec when present
            candidate_attrs = []
            try:
                candidate_attrs = list(getattr(gen_obj, "__dict__", {}).keys())
            except Exception:
                candidate_attrs = []
            if not candidate_attrs:
                candidate_attrs = [a for a in dir(gen_obj) if not a.startswith("_")]
            for attr in candidate_attrs:
                if attr in {"specializationTopic", "specializationID", "specializationTimestamp"}:
                    continue
                if hasattr(spec, attr):
                    sval = getattr(spec, attr)
                    if isinstance(sval, (str, int, float, bool)):
                        try:
                            setattr(gen_obj, attr, sval)
                        except Exception:
                            continue
        except Exception:
            pass


class LargeSetWriter(WriterDecorator):
    def __init__(
        self,
        set_name: str,
        attr_path: Tuple[str, ...] = (),
    ) -> None:
        super().__init__()
        self.set_name = set_name
        self.attr_path = tuple(attr_path)
        self._children: Dict[str, WriterNode] = {}

    def attach_children(self, **children: "WriterNode") -> None:
        super().attach_children(**children)
        self._children = getattr(self, "_children", {})

    def _meta_struct(self, parent: Any) -> Any:
        metadata = get_at_path(parent, self.attr_path)
        if metadata is None:
            raise RuntimeError(f"Cannot get get metadata at {self.attr_path} on {type(parent).__name__}")
        return metadata

    def _get_set_id(self, meta: Any) -> Any:
        return getattr(meta, "setID")

    @staticmethod
    def _set_update_marker(meta: Any, elem_id: Any, elem_ts: Optional[Any]) -> None:
        setattr(meta, "updateElementID", elem_id)
        if elem_ts is not None:
            setattr(meta, "updateElementTimestamp", elem_ts)

    @staticmethod
    def _elem_identity(elem: Any):
        return getattr(elem, "elementID"), getattr(elem, "elementTimestamp", None)

    @staticmethod
    def _ensure_elem_set_id(elem: Any, set_id: Any) -> None:
        setattr(elem, "setID", set_id)

    def publish(self, node: "WriterNode", builder: "CombinedBuilder") -> None:
        meta = self._meta_struct(builder.base)

        current_id = getattr(meta, "setID", None)
        if current_id is None or current_id == NIL_GUID:
            new_id = generate_guid()
            setattr(meta, "setID", new_id)

        set_id = getattr(meta, "setID")

        print(f"Dump builder: {builder.collections_by_path.items()}")

        # Prefer collections bag at the parent of the metadata field; fall back to current node
        parent_path = tuple(self.attr_path[:-1])
        items = builder.collections_at(parent_path).get(self.set_name, None)
        used_parent_path = items is not None
        if items is None:
            items = builder.collections_at().get(self.set_name, None)

        if items is None:
            return

        items = items.to_runtime()
        print(f"Large Set Publish Items: {items}")
        setattr(meta, "size", int(len(items)))

        if len(self._children) != 1:
            RuntimeError(f"LargeSetWriter Decorator only expects one child, but has {self._children.keys()}")
        child = next(iter(self._children.values()))

        last_id = last_ts = None
        for idx, e in enumerate(items):
            self._ensure_elem_set_id(e, set_id)
            elem_id, elem_ts = getattr(e, "elementID"), getattr(e, "elementTimestamp", None)
            # If items were attached at the parent-of-metadata path, prefix element node path with it
            elem_prefix: Tuple[str, ...] = parent_path if used_parent_path else ()
            elem_path = elem_prefix + path_for_set_element(self.set_name, elem_id)
            child_b = builder.spawn_child(e, elem_path)
            child.publish(child_b)
            last_id, last_ts = elem_id, elem_ts

        setattr(meta, "updateElementID", last_id)
        if last_ts is not None:
            setattr(meta, "updateElementTimestamp", last_ts)


class LargeListWriter(WriterDecorator):
    def __init__(
        self,
        list_name: str,
        attr_path: Tuple[str, ...] = (),
    ) -> None:
        super().__init__()
        self.list_name = list_name
        self.attr_path = tuple(attr_path)
        self._children: Dict[str, WriterNode] = {}

    def attach_children(self, **children: "WriterNode") -> None:
        super().attach_children(**children)
        self._children = getattr(self, "_children", {})

    def _meta_struct(self, parent: Any) -> Any:
        metadata = get_at_path(parent, self.attr_path)
        if metadata is None:
            raise RuntimeError(f"Cannot get metadata at {self.attr_path} on {type(parent).__name__}")
        return metadata

    def _get_list_id(self, meta: Any) -> Any:
        return getattr(meta, "listID")

    @staticmethod
    def _set_starting(meta: Any, first_id: Any) -> None:
        setattr(meta, "startingElementID", first_id)

    @staticmethod
    def _set_update_marker(meta: Any, last_id: Any, last_ts: Optional[Any]) -> None:
        setattr(meta, "updateElementID", last_id)
        if last_ts is not None:
            setattr(meta, "updateElementTimestamp", last_ts)

    @staticmethod
    def _elem_id(elem: Any) -> Any:
        return getattr(elem, "elementID")

    @staticmethod
    def _elem_ts(elem: Any) -> Optional[Any]:
        return getattr(elem, "elementTimestamp", None)

    @staticmethod
    def _set_next(elem: Any, next_id: Optional[Any]) -> None:
        setattr(elem, "nextElementID", next_id)

    @staticmethod
    def _ensure_elem_list_id(elem: Any, list_id: Any) -> None:
        setattr(elem, "listID", list_id)

    def publish(self, node: "WriterNode", builder: "CombinedBuilder") -> None:
        meta = self._meta_struct(builder.base)

        if getattr(meta, "listID", None) in (None, NIL_GUID):
            new_id = generate_guid()
            setattr(meta, "listID", new_id)

        list_id = getattr(meta, "listID")

        print(f"List name: {self.list_name}")
        print(f"List attr_path: {self.attr_path}")
        print(f"Dump builder: {builder.collections_by_path.items()}")

        # Prefer collections bag at the parent of the metadata field; fall back to current node
        items = builder.collections_at(self.attr_path[:-1]).get(self.list_name, None)
        if items is None:
            items = builder.collections_at().get(self.list_name, None)

        if items is None:
            print("Large List Items is None")
            return

        items = items.to_runtime()
        print(f"Large List Publish Items: {items}")

        # Handle empty list explicitly
        if not items:
            setattr(meta, "size", 0)
            # Use NIL_GUID for required GUID fields; None for optional timestamp
            try:
                setattr(meta, "startingElementID", NIL_GUID)
            except Exception:
                pass
            try:
                setattr(meta, "updateElementID", NIL_GUID)
                setattr(meta, "updateElementTimestamp", None)
            except Exception:
                pass
            return

        setattr(meta, "size", int(len(items)))
        if len(self._children) != 1:
            RuntimeError(f"LargeListWriter Decorator only expects one child, but has {self._children.keys()}")
        child = next(iter(self._children.values()))

        # link chain
        for i, e in enumerate(items):
            setattr(e, "listID", list_id)
            nxt = getattr(items[i + 1], "elementID") if i + 1 < len(items) else None
            setattr(e, "nextElementID", nxt)
        for e in items:
            elem_id = getattr(e, "elementID")
            # Element nodes live under the parent of the metadata field; prefix that path
            parent_path = tuple(self.attr_path[:-1])
            elem_path = parent_path + path_for_list_element(self.list_name, elem_id)
            child_b = builder.spawn_child(e, elem_path)
            child.publish(child_b)

        first_id = getattr(items[0], "elementID")
        last_id = getattr(items[-1], "elementID")
        last_ts = getattr(items[-1], "elementTimestamp", None)
        setattr(meta, "startingElementID", first_id)
        setattr(meta, "updateElementID", last_id)
        if last_ts is not None:
            setattr(meta, "updateElementTimestamp", last_ts)
