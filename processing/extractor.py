import pymupdf
import pymupdf.layout
import pymupdf4llm
import docling 
# from docling.datamodel import pipeline_options, pipeline_options_vlm_model
from docling_core.types.doc.document import TextItem, CodeItem, FormulaItem
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, CodeFormulaVlmOptions, TableStructureOptions, TableFormerMode, RapidOcrOptions, OcrOptions, TesseractOcrOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
from docling.datamodel.pipeline_options import ThreadedPdfPipelineOptions
from docling.pipeline.threaded_standard_pdf_pipeline import ThreadedStandardPdfPipeline
import logging

# print(torch.__version__)



pipeline_options = ThreadedPdfPipelineOptions(
    # accelerator_options=AcceleratorOptions(
    #     device=AcceleratorDevice.CUDA,
    #     cuda_use_flash_attention2=True
        
    # ),
    
    do_ocr=False,
    # table_structure_options=TableStructureOptions(mode=TableFormerMode.ACCURATE, do_cell_matching=False),
    # code_formula_options=CodeFormulaVlmOptions.from_preset('codeformulav2'),
    # do_formula_enrichment=True,
    do_table_structure=False,

    # ocr_batch_size=4,
    # layout_batch_size=4,
    # table_batch_size=4,

)

doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options,
        )
    }
)

# 3. Initialize the pipeline
doc_converter.initialize_pipeline(InputFormat.PDF)

# 4. Convert your document

# with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
result = doc_converter.convert("docling-preview/1706.03762v7.pdf")

with open('docling-preview/list.txt', 'w', encoding='utf-8') as f:
    f.write(str(result.document.texts))

# for item, level in result.document.iterate_items():

#     if isinstance(item, TextItem):
#         print(item.get_ref())
#         print(f'Label {item.label} Page no: {item.prov[0].page_no}')
#         print(item.hyperlink)
#         print('*' * 45)

# Access the converted content
# with open('docling-preview/docling-test-5.md', 'w', encoding='utf-8') as f:
    # f.write(result.document.export_to_markdown())




class PdfProcessor:
    ...
