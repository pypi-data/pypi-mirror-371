#!/usr/bin/env python3
#
"""
    Módulo para trabalhar com imagens
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from soup_files import File, Directory, ProgressBarAdapter, CreatePbar
from convert_stream.enum_libs.enums import LibPdfToImage
from convert_stream.enum_libs.modules import DEFAULT_LIB_PDF_TO_IMG, DEFAULT_LIB_IMAGE
from convert_stream.image.img_object import ImageObject, LibImage, CollectionImages
from convert_stream.pdf.pdf_page import PageDocumentPdf, fitz
from convert_stream.pdf.pdf_document import DocumentPdf


class ABCConvertPdf(ABC):

    def __init__(self, document: DocumentPdf):
        self.document: DocumentPdf = document
        self.lib_pdf_to_image: LibPdfToImage = DEFAULT_LIB_PDF_TO_IMG
        self.pbar: ProgressBarAdapter = CreatePbar().get()

    def set_pbar(self, pbar: ProgressBarAdapter):
        self.pbar = pbar

    @abstractmethod
    def to_images(
                self, *,
                dpi: int = 150,
                lib_image: LibImage = DEFAULT_LIB_IMAGE,
            ) -> list[ImageObject]:
        """
            Converte as páginas PDF do documento em lista de objetos imagem ImageObject

        :param dpi: DPI do documento, resolução da renderização.
        :param lib_image: Biblioteca para manipular imagens PIL/OpenCv
        """
        pass

    @abstractmethod
    def to_files_image(
            self,
            output_dir: Directory, *,
            replace: bool = False,
            gaussian_filter: bool = False,
            dpi: int = 300,
            lib_image: LibImage = DEFAULT_LIB_IMAGE,
            ) -> None:
        """
            Converte todas as páginas do documento em objeto de imagem e salva no disco
        em formato de imagem PNG.
        """
        pass


class ImplementConvertPdfFitz(ABCConvertPdf):

    def __init__(self, document: DocumentPdf):
        super().__init__(document)
        self.lib_pdf_to_image: LibPdfToImage = LibPdfToImage.PDF_TO_IMG_FITZ
        self.__collection_imgs: CollectionImages = CollectionImages()
        self.__collection_imgs.set_pbar(self.pbar)

    def __extract_images(
                self, *,
                dpi: int = 300,
                lib_image: LibImage = DEFAULT_LIB_IMAGE,
            ) -> None:
        """
            Extrair as imagens do documento e salvar na propriedade CollectionImages()
        """
        if not self.__collection_imgs.is_empty:
            return

        self.pbar.start()
        print()
        zoom = dpi / 72  # fator de escala para o fitz.Matrix
        matrix = fitz.Matrix(zoom, zoom)
        pages_pdf: list[PageDocumentPdf] = self.document.to_pages()
        max_num: int = len(pages_pdf)
        for num, current_page in enumerate(pages_pdf):
            self.pbar.update(
                ((num + 1) / max_num) * 100,
                f'Convertendo imagem: {num + 1} de {max_num}',
            )
            page: fitz.Page = current_page.implement_page_pdf.mod_page
            pix: fitz.Pixmap = page.get_pixmap(matrix=matrix, alpha=False)  # sem canal alpha
            img_bytes = pix.tobytes("png")
            img_obj = ImageObject.create_from_bytes(img_bytes, lib_image=lib_image)
            #img_obj = ImageObject.create_from_pil(pix.pil_image())
            self.__collection_imgs.add_image(img_obj)
        print()
        self.pbar.stop()

    def to_images(
                self, *,
                dpi: int = 300,
                lib_image: LibImage = DEFAULT_LIB_IMAGE,
            ) -> list[ImageObject]:
        self.__extract_images(dpi=dpi, lib_image=lib_image)
        return self.__collection_imgs.images

    def to_files_image(
                self,
                output_dir: Directory, *,
                replace: bool = False,
                gaussian_filter: bool = False,
                dpi: int = 300,
                lib_image: LibImage = DEFAULT_LIB_IMAGE,
            ) -> None:
        """
            Renderiza as páginas e salva como PNG.
        """
        self.__extract_images(dpi=dpi, lib_image=lib_image)
        if self.__collection_imgs.is_empty:
            return
        self.__collection_imgs.to_files_image(
            output_dir=output_dir,
            replace=replace,
            gaussian_filter=gaussian_filter,
        )


class ConvertPdfToImages(object):

    def __init__(self, mod_convert_to_image: ABCConvertPdf):
        self.mod_convert_to_image: ABCConvertPdf = mod_convert_to_image

    def set_pbar(self, pbar: ProgressBarAdapter):
        self.mod_convert_to_image.set_pbar(pbar)

    def to_images(
                self, *, dpi: int = 300, lib_image: LibImage = DEFAULT_LIB_IMAGE
            ) -> list[ImageObject]:
        return self.mod_convert_to_image.to_images(dpi=dpi, lib_image=lib_image)

    def to_files_image(
            self,
            output_dir: Directory, *,
            replace: bool = False,
            gaussian_filter: bool = False,
            dpi: int = 300,
            lib_image: LibImage = DEFAULT_LIB_IMAGE,
            ) -> None:
        self.mod_convert_to_image.to_files_image(
            dpi=dpi,
            lib_image=lib_image,
            replace=replace,
            output_dir=output_dir,
            gaussian_filter=gaussian_filter
        )

    @classmethod
    def create(cls, doc: DocumentPdf) -> ConvertPdfToImages:
        _mod = ImplementConvertPdfFitz(doc)
        return cls(_mod)

