from typing import Any, Iterator, Iterable, List

from docling_core.types.doc import DoclingDocument, DocItemLabel
from docling_core.transforms.chunker import DocChunk, BaseChunk
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker


class CustomHybridChunker(HybridChunker):
    def _move_suffix_chunks_to_heading_end(
        self, chunks: Iterable[DocChunk]
    ) -> Iterable[DocChunk]:
        """Reorders document chunks so that any chunk containing a Table or Picture is moved to the end of its respective heading section.
        This function processes a sequence of DocChunk objects, grouping them by their heading metadata. Within each heading group, it ensures that chunks containing images (DocItemLabel.PICTURE) or tables (DocItemLabel.TABLE) are placed after all other chunks for that heading. This helps maintain the semantic flow of the document by preventing non-textual elements from interrupting the main content.

        Args:
            chunks (Iterable[DocChunk]): An iterable of DocChunk objects to be reordered."""

        chunks = list(chunks)
        if not chunks:
            return []
        new_chunks = []
        suffix_chunks = []
        prev_heading = (
            "\n".join(chunks[0].meta.headings) if chunks[0].meta.headings else "None"
        )

        for chunk in chunks:
            is_suffix = False
            current_heading = (
                "\n".join(chunk.meta.headings) if chunk.meta.headings else "None"
            )
            if current_heading != prev_heading:
                new_chunks.extend(suffix_chunks)
                suffix_chunks = []
                prev_heading = current_heading

            for item in chunk.meta.doc_items:
                if (
                    item.label == DocItemLabel.PICTURE
                    or item.label == DocItemLabel.TABLE
                ):
                    is_suffix = True
                    suffix_chunks.append(chunk)
                    break

            if not is_suffix:
                new_chunks.append(chunk)

        new_chunks.extend(suffix_chunks)
        return new_chunks

    def _filter_by_doc_item_labels(
        self,
        chunks: Iterable[DocChunk],
        labels: List[DocItemLabel] = [DocItemLabel.FOOTNOTE],
    ) -> Iterable[DocChunk]:
        filtered_chunks = []
        for chunk in chunks:
            new_doc_items = []
            for item in chunk.meta.doc_items:
                if item.label in labels:
                    continue
                new_doc_items.append(item)
            if len(new_doc_items) == 0:
                continue
            chunk.meta.doc_items = new_doc_items
            filtered_chunks.append(chunk)

        return iter(filtered_chunks)

    def chunk(self, dl_doc: DoclingDocument, **kwargs: Any) -> Iterator[BaseChunk]:
        my_doc_ser = self.serializer_provider.get_serializer(doc=dl_doc)
        res: Iterable[DocChunk]
        res = self._inner_chunker.chunk(
            dl_doc=dl_doc,
            doc_serializer=my_doc_ser,
            **kwargs,
        )
        res = self._filter_by_doc_item_labels(res)
        res = self._move_suffix_chunks_to_heading_end(res)
        res = [
            x
            for c in res
            for x in self._split_by_doc_items(c, doc_serializer=my_doc_ser)
        ]
        res = [x for c in res for x in self._split_using_plain_text(c)]
        if self.merge_peers:
            res = self._merge_chunks_with_matching_metadata(res)
        return iter(res)
        return res
