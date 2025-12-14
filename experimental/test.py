from docx2md import Converter, DocxFile, DocxMedia

docx_file = "НИР_Косов Андрей Сергеевич — 08.12.2025.docx"

docx = DocxFile(docx_file)
media = DocxMedia(docx)
media.save("media")
converter = Converter(docx.document(), media, use_md_table=True)
md_text = converter.convert()

print(md_text)
