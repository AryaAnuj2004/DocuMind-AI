import re
import io
from dataclasses import dataclass
from typing import List, Optional
import pypdf

@dataclass
class DocumentChunk:
    chunk_id: int
    text: str
    page_num: int
    paragraph_num: int
    section_title: str
    citation_label: str

    def to_dict(self):
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "page_num": self.page_num,
            "paragraph_num": self.paragraph_num,
            "section_title": self.section_title,
            "citation_label": self.citation_label
        }

class DocumentParser:
    """
    Parses PDF and TXT documents into structured, indexed chunks with precise page,
    paragraph, and section citation metadata.
    """
    
    @staticmethod
    def parse_txt(file_content: str, filename: str = "Document") -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        # Split text into paragraphs by double newlines or single newlines with indent/headers
        raw_paragraphs = [p.strip() for p in re.split(r'\n\s*\n', file_content) if p.strip()]
        
        current_section = "General Content"
        chunk_id = 1
        
        for idx, para in enumerate(raw_paragraphs, start=1):
            # Detect section heading heuristic (short line, ending with colon or uppercase/bold pattern)
            lines = para.split('\n')
            first_line = lines[0].strip()
            if len(first_line) < 80 and (first_line.isupper() or first_line.endswith(':') or re.match(r'^(Section|Chapter|\d+\.|\#+)\s+', first_line, re.IGNORECASE)):
                current_section = re.sub(r'^\#+\s*', '', first_line).strip(' :')
            
            # Normalize paragraph internal whitespace
            clean_text = " ".join(para.split())
            if not clean_text:
                continue
                
            citation = f"Section '{current_section}', Paragraph {idx}" if current_section != "General Content" else f"Paragraph {idx}"
            
            chunks.append(DocumentChunk(
                chunk_id=chunk_id,
                text=clean_text,
                page_num=1,
                paragraph_num=idx,
                section_title=current_section,
                citation_label=citation
            ))
            chunk_id += 1
            
        return chunks

    @staticmethod
    def parse_pdf(file_bytes: bytes, filename: str = "Document") -> List[DocumentChunk]:
        chunks: List[DocumentChunk] = []
        pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        chunk_id = 1
        current_section = "General Content"
        
        for page_idx, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text() or ""
            if not text.strip():
                continue

            # Attempt splitting by double newlines first
            raw_paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]
            
            # If no double newline split found, group lines logically into paragraphs
            if len(raw_paragraphs) <= 1:
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                grouped_paras = []
                current_para_lines = []
                
                for line in lines:
                    # Ignore pure page numbers like "1", "Page 2"
                    if re.match(r'^(page\s+)?\d+$', line, re.IGNORECASE):
                        continue
                    
                    # Detect paragraph boundary: heading, question, or numbered section
                    is_new_header = (
                        len(line) < 80 and (
                            line.isupper() or 
                            line.endswith(':') or 
                            line.endswith('?') or
                            re.match(r'^(Q\d+[\.:]?|Section|Chapter|\d+[\.:]|\#+)\s+', line, re.IGNORECASE)
                        )
                    )
                    
                    if is_new_header and current_para_lines:
                        grouped_paras.append(" ".join(current_para_lines))
                        current_para_lines = [line]
                    else:
                        current_para_lines.append(line)
                
                if current_para_lines:
                    grouped_paras.append(" ".join(current_para_lines))
                
                raw_paragraphs = grouped_paras if grouped_paras else [text.strip()]
            
            para_in_page = 1
            for para in raw_paragraphs:
                clean_text = " ".join(para.split())
                if not clean_text or len(clean_text) < 3 or re.match(r'^(page\s+)?\d+$', clean_text, re.IGNORECASE):
                    continue  # skip empty or pure page number noise

                lines = para.split('\n')
                first_line = lines[0].strip()
                if len(first_line) < 80 and (first_line.isupper() or first_line.endswith(':') or re.match(r'^(Section|Chapter|\d+\.|\#+)\s+', first_line, re.IGNORECASE)):
                    current_section = re.sub(r'^\#+\s*', '', first_line).strip(' :')

                citation = f"Page {page_idx}, Paragraph {para_in_page}"
                if current_section != "General Content":
                    citation += f" ({current_section})"

                chunks.append(DocumentChunk(
                    chunk_id=chunk_id,
                    text=clean_text,
                    page_num=page_idx,
                    paragraph_num=para_in_page,
                    section_title=current_section,
                    citation_label=citation
                ))
                chunk_id += 1
                para_in_page += 1

        return chunks

    @classmethod
    def parse_file(cls, file_bytes: bytes, filename: str) -> List[DocumentChunk]:
        if filename.lower().endswith('.pdf'):
            return cls.parse_pdf(file_bytes, filename)
        else:
            # Assume text/plain or markdown
            try:
                text_content = file_bytes.decode('utf-8')
            except UnicodeDecodeError:
                text_content = file_bytes.decode('latin-1', errors='replace')
            return cls.parse_txt(text_content, filename)
