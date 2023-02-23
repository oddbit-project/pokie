from io import BytesIO

from rick.resource.stream import MultiPartReader, FileSlice


class FilePart(FileSlice):
    pass


class FileReader(MultiPartReader):

    def __init__(self, parts: list, name='', content_type='application/unknown', attributes: dict = None):
        if attributes is None:
            attributes = {}

        self.name = name
        self.content_type = content_type
        self.attributes = attributes
        super().__init__(parts=parts)

    def read_block(self, offset=0, limit=-1) -> BytesIO:
        result = BytesIO()
        for r in self.read(offset, limit):
            result.write(r)
        return result

    def read_chunked(self, block_size: int) -> BytesIO:
        blocks, reminder = divmod(self.size, block_size)
        ofs = 0
        while blocks > 0:
            buf = self.read_block(ofs, block_size)
            buf.seek(0)
            yield buf
            ofs += block_size
            blocks -= 1

        if reminder > 0:
            buf = self.read_block(ofs, reminder)
            buf.seek(0)
            yield buf
