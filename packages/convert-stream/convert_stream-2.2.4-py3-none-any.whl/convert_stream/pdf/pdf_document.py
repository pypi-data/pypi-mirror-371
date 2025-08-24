#!/usr/bin/env python3
#
"""
    Módulo para trabalhar com imagens
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from io import BytesIO
from soup_files import File, Directory, LibraryDocs, InputFiles, ProgressBarAdapter
from convert_stream.enum_libs.enums import LibPDF
from convert_stream.enum_libs.modules import (
    DEFAULT_LIB_PDF, ModuleDocPdf, ModulePagePdf, PdfWriter, PdfReader, PageObject, fitz,
)
from convert_stream.image.img_object import get_hash_from_bytes
from convert_stream.pdf.pdf_page import PageDocumentPdf


class ABCDocument(ABC):

    def __init__(self, mod_doc_pdf: ModuleDocPdf, name: str):
        self.mod_doc_pdf: ModuleDocPdf = mod_doc_pdf
        self.lib_pdf: LibPDF = DEFAULT_LIB_PDF
        self.name: str = name

    @abstractmethod
    def get_first_page(self) -> PageDocumentPdf:
        pass

    @abstractmethod
    def get_last_page(self) -> PageDocumentPdf:
        pass

    @abstractmethod
    def get_page(self, idx: int) -> PageDocumentPdf | None:
        pass

    @abstractmethod
    def get_number_pages(self) -> int:
        pass

    @abstractmethod
    def add_page(self, page: PageDocumentPdf):
        pass

    @abstractmethod
    def add_pages(self, pages: list[PageDocumentPdf]):
        pass

    @abstractmethod
    def to_file(self, file: File):
        pass

    @abstractmethod
    def to_bytes(self) -> BytesIO:
        pass

    @abstractmethod
    def to_pages(self) -> list[PageDocumentPdf]:
        pass

    @abstractmethod
    def to_list(self, separator: str = '\n') -> list[str]:
        pass

    @abstractmethod
    def to_dict(self, separator: str = '\n') -> dict[str, list[str]]:
        pass

    @classmethod
    def create_from_file(cls, file: File) -> ABCDocument:
        pass

    @classmethod
    def create_from_bytes(cls, bt: BytesIO) -> ABCDocument:
        pass


class ImplementDocumentFitz(ABCDocument):

    def __init__(self, mod_doc_pdf: ModuleDocPdf, name: str):
        super().__init__(mod_doc_pdf, name)
        self.mod_doc_pdf: fitz.Document = mod_doc_pdf
        self.lib_pdf: LibPDF = LibPDF.FITZ

    def get_first_page(self) -> PageDocumentPdf:
        return self.get_page(0)

    def get_last_page(self) -> PageDocumentPdf:
        last_idx = self.mod_doc_pdf.page_count - 1
        return self.get_page(last_idx)

    def get_page(self, idx: int) -> PageDocumentPdf | None:
        _page_pdf = None
        if 0 <= idx < self.mod_doc_pdf.page_count:
            pg = self.mod_doc_pdf.load_page(idx)  # retorna fitz.Page
            if pg is not None:
                _page_pdf = PageDocumentPdf.create_from_page_fitz(pg, idx)
        return _page_pdf

    def get_number_pages(self) -> int:
        return self.mod_doc_pdf.page_count

    def add_page(self, page: PageDocumentPdf):
        # Assume que page.mod_page é fitz.Page
        # temp_doc = fitz.open()
        self.mod_doc_pdf.insert_pdf(
            page.implement_page_pdf.mod_page.parent,
            from_page=page.implement_page_pdf.mod_page.number,
            to_page=page.implement_page_pdf.mod_page.number
        )

    def add_pages(self, pages: list[PageDocumentPdf]):
        for page in pages:
            self.add_page(page)

    def to_file(self, file: File):
        self.mod_doc_pdf.save(file.path)

    def to_bytes(self) -> BytesIO:
        buf = BytesIO()
        self.mod_doc_pdf.save(buf)
        buf.seek(0)
        return buf

    def to_pages(self) -> list[PageDocumentPdf]:
        pages = []
        for pg in self.mod_doc_pdf:
            page_pdf = PageDocumentPdf.create_from_page_fitz(pg)
            pages.append(page_pdf)
        return pages

    def to_list(self, separator: str = '\n') -> list[str]:
        pages: list[PageDocumentPdf] = self.to_pages()
        values = []
        for pg in pages:
            values.extend(pg.to_list(separator))
        return values

    def to_dict(self, separator: str = '\n') -> dict[str, list[str]]:
        pages_pdf = self.to_pages()
        document_dict = PageDocumentPdf.DEFAULT_DICT
        for pg in pages_pdf:
            page_dict = pg.to_dict(separator)
            document_dict['TEXTO'].extend(page_dict['TEXTO'])
            document_dict['NUM_PAGE'].extend(page_dict['NUM_PAGE'])
            document_dict['NUM_LINHA'].extend(page_dict['NUM_LINHA'])
        return document_dict

    @classmethod
    def create_from_bytes(cls, bt: BytesIO) -> ImplementDocumentFitz:
        # Cria documento a partir de BytesIO
        doc = fitz.open(stream=bt.getvalue(), filetype="pdf")
        name = get_hash_from_bytes(bt)
        return cls(doc, name)

    @classmethod
    def create_from_file(cls, file: File) -> ImplementDocumentFitz:
        # Cria documento a partir de caminho no disco
        doc = fitz.open(file.path)
        return cls(doc, file.name())

    @classmethod
    def create_from_pages(cls, pages: list[PageDocumentPdf]) -> ImplementDocumentFitz:
        pdf_document = fitz.Document()  # Criar novo documento PDF.
        for page in pages:
            # Verifica se a página é do tipo fitz.Page
            if not isinstance(page.implement_page_pdf.mod_page, fitz.Page):
                raise TypeError(f"Todas as páginas devem ser do tipo [fitz.Page]")
            # Insere as páginas no novo documento
            pdf_document.insert_pdf(
                page.implement_page_pdf.mod_page.parent,
                from_page=page.implement_page_pdf.mod_page.number,
                to_page=page.implement_page_pdf.mod_page.number
            )

        bt = BytesIO(pdf_document.write())
        return cls.create_from_bytes(bt)


class ImplementDocumentPyPdf(ABCDocument):

    def __init__(self, mod_doc_pdf: PdfWriter, name: str):
        super().__init__(mod_doc_pdf, name)
        self.mod_doc_pdf: PdfWriter = mod_doc_pdf  # ou PdfReader
        self.lib_pdf: LibPDF = LibPDF.PYPDF

    def get_first_page(self) -> PageDocumentPdf:
        """
        Retorna a primeira página do documento.
        """
        # O índice da primeira página em PyPDF2 é 0.
        return self.get_page(0)

    def get_last_page(self) -> PageDocumentPdf:
        """
        Retorna a última página do documento.
        """
        # O índice da última página é o número total de páginas menos um.
        last_page_idx = len(self.mod_doc_pdf.pages) - 1
        return self.get_page(last_page_idx)

    def get_page(self, idx: int) -> PageDocumentPdf | None:
        """
        Retorna uma página específica pelo seu índice.
        Se o índice for inválido, retorna None.
        """
        if 0 <= idx < len(self.mod_doc_pdf.pages):
            # Acessa a página pela lista self.mod_doc_pdf.pages
            pg = self.mod_doc_pdf.pages[idx]
            # O número da página é idx + 1
            return PageDocumentPdf.create_from_page_pypdf(pg, idx + 1)
        return None

    def get_number_pages(self) -> int:
        return len(self.mod_doc_pdf.pages)

    def add_page(self, page: PageDocumentPdf):
        self.mod_doc_pdf.add_page(page.implement_page_pdf.mod_page)

    def add_pages(self, pages: list[PageDocumentPdf]):
        for page in pages:
            self.add_page(page)

    def to_file(self, file: File):
        with open(file.path, 'wb') as f:
            self.mod_doc_pdf.write(f)

    def to_bytes(self) -> BytesIO:
        buf = BytesIO()
        self.mod_doc_pdf.write(buf)
        buf.seek(0)
        return buf

    def to_pages(self) -> list[PageDocumentPdf]:
        pages_pdf: list[PageDocumentPdf] = []
        for num, page in enumerate(self.mod_doc_pdf.pages):
            pg = PageDocumentPdf.create_from_page_pypdf(page)
            pages_pdf.append(pg)
        return pages_pdf

    def to_list(self, separator: str = '\n') -> list[str]:
        pages: list[PageDocumentPdf] = self.to_pages()
        values = []
        for pg in pages:
            values.extend(pg.to_list(separator))
        return values

    def to_dict(self, separator: str = '\n') -> dict[str, list[str]]:
        pages_pdf = self.to_pages()
        document_dict = PageDocumentPdf.DEFAULT_DICT
        for pg in pages_pdf:
            page_dict = pg.to_dict(separator)
            document_dict['TEXTO'].extend(page_dict['TEXTO'])
            document_dict['NUM_PAGE'].extend(page_dict['NUM_PAGE'])
            document_dict['NUM_LINHA'].extend(page_dict['NUM_LINHA'])
        return document_dict

    @classmethod
    def create_from_bytes(cls, bt: BytesIO) -> ImplementDocumentPyPdf:
        # Usa PdfReader diretamente de BytesIO
        bt.seek(0)
        reader = PdfReader(bt)
        bt.seek(0)
        name = get_hash_from_bytes(bt)
        pdf_writer = PdfWriter()
        for page in reader.pages:
            pdf_writer.add_page(page)

        bt.close()
        del bt
        del reader
        return cls(pdf_writer, name)

    @classmethod
    def create_from_file(cls, file: File) -> ImplementDocumentPyPdf:
        # Usa PdfReader diretamente de arquivo
        reader = PdfReader(file.absolute())
        pdf_writer = PdfWriter()
        for p in reader.pages:
            pdf_writer.add_page(p)
        del reader
        return cls(pdf_writer, file.name())

    @classmethod
    def create_from_pages(cls, pages: list[PageDocumentPdf]) -> ImplementDocumentPyPdf:
        pdf_writer = PdfWriter()
        for page_obj in pages:
            # Obtém o objeto de página da implementação da lib
            pdf_writer.add_page(page_obj.implement_page_pdf.mod_page)

        output_bytes = BytesIO()
        pdf_writer.write(output_bytes)
        pdf_bytes = output_bytes
        return cls.create_from_bytes(pdf_bytes)


class DocumentPdf(object):
    def __init__(self, doc_pdf: ABCDocument):
        self.doc_pdf: ABCDocument = doc_pdf
        self.lib_pdf: LibPDF = doc_pdf.lib_pdf
        self.name: str = doc_pdf.name

    def get_real_document(self) -> ModuleDocPdf:
        return self.doc_pdf.mod_doc_pdf

    def get_first_page(self) -> PageDocumentPdf:
        """
        Retorna a primeira página do documento.
        """
        # O índice da primeira página em PyPDF2 é 0.
        return self.doc_pdf.get_first_page()

    def get_last_page(self) -> PageDocumentPdf:
        """
        Retorna a última página do documento.
        """
        return self.doc_pdf.get_last_page()

    def get_page(self, idx: int) -> PageDocumentPdf | None:
        """
        Retorna uma página específica pelo seu índice.
        Se o índice for inválido, retorna None.
        """
        return self.doc_pdf.get_page(idx)

    def get_number_pages(self) -> int:
        return self.doc_pdf.get_number_pages()

    def add_page(self, page: PageDocumentPdf):
        self.doc_pdf.add_page(page)

    def add_pages(self, pages: list[PageDocumentPdf]):
        self.doc_pdf.add_pages(pages)

    def to_file(self, file: File):
        self.doc_pdf.to_file(file)

    def to_bytes(self) -> BytesIO:
        return self.doc_pdf.to_bytes()

    def to_pages(self) -> list[PageDocumentPdf]:
        return self.doc_pdf.to_pages()

    def to_list(self, separator: str = '\n') -> list[str]:
        return self.doc_pdf.to_list(separator)

    def to_dict(self, separator: str = '\n') -> dict[str, list[str]]:
        return self.doc_pdf.to_dict(separator)

    def find(self, text_find: str, *, separator: str = '\n', iqual: bool = False, case: bool = False) -> str | None:
        _find_item = None
        pages = self.to_pages()
        for pg in pages:
            page_text_str = pg.find(text_find, separator=separator, iqual=iqual, case=case)
            if page_text_str is not None:
                _find_item = page_text_str
                break
        pages.clear()
        del pages
        return _find_item

    def find_all(self, text: str, *, separator: str = '\n', iqual: bool = False, case: bool = True) -> list[str]:
        if text is None:
            raise ValueError(f'{__class__.__name__}: o texto de pesquisa {text} é nulo!')
        elements = []
        pages = self.to_pages()
        for pg in pages:
            page_text_str = pg.find(text, separator=separator, iqual=iqual, case=case)
            if page_text_str is not None:
                elements.append(text)
                break
        pages.clear()
        del pages
        return elements

    @classmethod
    def create_from_bytes(cls, bt: BytesIO, *, lib_pdf: LibPDF = LibPDF.FITZ) -> DocumentPdf:
        if lib_pdf == LibPDF.FITZ:
            mod_pdf = ImplementDocumentFitz.create_from_bytes(bt)
            return cls(mod_pdf)
        elif lib_pdf == LibPDF.PYPDF:
            mod_pdf = ImplementDocumentPyPdf.create_from_bytes(bt)
            return cls(mod_pdf)
        else:
            raise NotImplementedError(f'Módulo PDF não implementado: {lib_pdf}')

    @classmethod
    def create_from_file(cls, file: File, *, lib_pdf: LibPDF = DEFAULT_LIB_PDF) -> DocumentPdf:
        if lib_pdf == LibPDF.FITZ:
            mod_pdf = ImplementDocumentFitz.create_from_file(file)
            return cls(mod_pdf)
        elif lib_pdf == LibPDF.PYPDF:
            mod_pdf = ImplementDocumentPyPdf.create_from_file(file)
            return cls(mod_pdf)
        else:
            raise NotImplementedError(f'Módulo PDF não implementado: {lib_pdf}')

    @classmethod
    def create_from_pages(
                cls,
                pages: list[PageDocumentPdf], *,
                lib_pdf: LibPDF = DEFAULT_LIB_PDF
            ) -> DocumentPdf:
        if lib_pdf == LibPDF.FITZ:
            mod_pdf = ImplementDocumentFitz.create_from_pages(pages)
            return cls(mod_pdf)
        elif lib_pdf == LibPDF.PYPDF:
            mod_pdf = ImplementDocumentPyPdf.create_from_pages(pages)
            return cls(mod_pdf)
        else:
            raise NotImplementedError(f'Módulo PDF não implementado: {lib_pdf}')


class CollectionPagePdf(object):

    def __init__(self, pages: list[PageDocumentPdf] = list()) -> None:
        self.pages: list[PageDocumentPdf] = pages
        self.__count: int = 0
        self.__max_num_pages: int = len(self.pages)
        self.pbar: ProgressBarAdapter = ProgressBarAdapter()

    @property
    def name(self) -> str | None:
        if self.is_null:
            return None
        return self.pages[0].__hash__()

    @property
    def length(self) -> int:
        return len(self.pages)

    @property
    def is_null(self) -> bool:
        return self.length == 0

    def clear(self):
        self.pages.clear()
        self.__count = 0
        self.__max_num_pages = 0

    def set_pbar(self, p: ProgressBarAdapter):
        self.pbar = p

    def add_page(self, page: PageDocumentPdf) -> None:
        self.__count += 1
        self.pbar.update_text(f'Adicionando página PDF {self.__count}')
        self.__max_num_pages += 1
        page.number_page = self.__max_num_pages
        self.pages.append(page)

    def add_pages(self, pages: list[PageDocumentPdf]) -> None:
        for n, pg in enumerate(pages):
            self.__max_num_pages += 1
            pg.number_page = self.__max_num_pages
            self.pages.append(pg)

    def add_file_pdf(self, file: File, *, lib_pdf: LibPDF = DEFAULT_LIB_PDF) -> None:
        self.pbar.update_text(f'Adicionando arquivo PDF {file.basename()}')
        doc_pdf = DocumentPdf.create_from_file(file, lib_pdf=lib_pdf)
        self.add_pages(doc_pdf.to_pages())

    def add_files_pdf(self, files: list[File], lib_pdf: LibPDF = DEFAULT_LIB_PDF) -> None:
        max_num: int = len(files)
        for num, f in enumerate(files):
            self.pbar.update(
                ((num + 1) / max_num) * 100,
                f'Adicionando arquivo: [{num+1} de {max_num}] {f.basename()}'
            )
            _doc_pdf = DocumentPdf.create_from_file(f, lib_pdf=lib_pdf)
            _pages_pdf = _doc_pdf.to_pages()
            for _page in _pages_pdf:
                self.__max_num_pages += 1
                _page.number_page = self.__max_num_pages
                self.pages.append(_page)
            del _doc_pdf
            del _pages_pdf

    def add_document(self, doc: DocumentPdf) -> None:
        self.add_pages(doc.to_pages())

    def add_directory_pdf(self, d: Directory, *, max_files: int = 4000):
        input_files = InputFiles(d, maxFiles=max_files)
        self.add_files_pdf(input_files.get_files(file_type=LibraryDocs.PDF))

    def set_land_scape(self):
        for p in self.pages:
            p.set_land_scape()

    def to_files_pdf(
                self,
                output_dir: Directory, *,
                replace: bool = False,
                prefix: str = None,
            ) -> None:
        max_num = self.length
        self.pbar.start()
        print()
        for n, page in enumerate(self.pages):
            _doc_pdf = DocumentPdf.create_from_pages([page])
            if prefix is None:
                file_path = output_dir.join_file(f'{page.number_page}-{_doc_pdf.name}.pdf')
            else:
                file_path = output_dir.join_file(f'{prefix}-{page.number_page}.pdf')

            if (not replace) and (file_path.exists()):
                continue
            self.pbar.update(
                ((n+1) / max_num) * 100,
                f'Exportando: [{n+1} de {max_num}] {file_path.basename()}'
            )
            try:
                _doc_pdf.to_file(file_path)
            except Exception as e:
                self.pbar.update_text(f'{e}')
            del _doc_pdf
        print()
        self.pbar.stop()


