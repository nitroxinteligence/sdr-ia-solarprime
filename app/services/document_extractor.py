"""
Document Extraction Service - Extrai texto de PDFs e outros documentos
"""
import pypdf
import pdfplumber
import docx2txt
import io
import base64
from typing import Dict, Optional, Any, List
from loguru import logger
from app.utils.logger import emoji_logger
import tempfile
import os

class DocumentExtractor:
    """
    Serviço de extração de texto de documentos.
    Suporta PDF, DOCX e outros formatos comuns.
    """
    
    def __init__(self):
        """Inicializa o extrator de documentos"""
        emoji_logger.system_info("DocumentExtractor inicializado com pypdf e pdfplumber")
        
    async def extract_from_pdf(
        self, 
        pdf_base64: str,
        max_chars: int = 10000
    ) -> Dict[str, Any]:
        """
        Extrai texto de um PDF codificado em base64
        
        Args:
            pdf_base64: PDF codificado em base64
            max_chars: Número máximo de caracteres a extrair
            
        Returns:
            Dict com texto extraído e metadados
        """
        if not pdf_base64:
            return {
                "text": "",
                "status": "error",
                "error": "PDF vazio ou não fornecido"
            }
            
        try:
            emoji_logger.system_info("Iniciando extração de texto do PDF")
            
            # 1. Decodificar base64
            try:
                pdf_bytes = base64.b64decode(pdf_base64)
                logger.debug(f"PDF decodificado: {len(pdf_bytes)} bytes")
            except Exception as e:
                logger.error(f"Erro ao decodificar base64: {e}")
                return {
                    "text": "",
                    "status": "error",
                    "error": f"Erro ao decodificar PDF: {str(e)}"
                }
            
            # 2. Criar BytesIO para leitura
            pdf_io = io.BytesIO(pdf_bytes)
            
            # 3. Tentar com pypdf primeiro (mais rápido)
            try:
                logger.debug("Tentando extração com pypdf...")
                
                reader = pypdf.PdfReader(pdf_io)
                num_pages = len(reader.pages)
                
                emoji_logger.system_info(f"PDF com {num_pages} página(s)")
                
                text = ""
                metadata = {}
                
                # Extrair metadados
                if reader.metadata:
                    metadata = {
                        "title": reader.metadata.get('/Title', ''),
                        "author": reader.metadata.get('/Author', ''),
                        "subject": reader.metadata.get('/Subject', ''),
                        "creator": reader.metadata.get('/Creator', ''),
                        "producer": reader.metadata.get('/Producer', ''),
                        "creation_date": str(reader.metadata.get('/CreationDate', ''))
                    }
                
                # Extrair texto de cada página
                for i, page in enumerate(reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text += f"\n--- Página {i+1} ---\n"
                            text += page_text
                            
                            # Verificar limite de caracteres
                            if len(text) > max_chars:
                                text = text[:max_chars]
                                logger.warning(f"Texto truncado em {max_chars} caracteres")
                                break
                    except Exception as e:
                        logger.debug(f"Erro ao extrair página {i+1}: {e}")
                        continue
                
                if text.strip():
                    emoji_logger.system_info(f"Texto extraído com pypdf: {len(text)} caracteres")
                    
                    # Analisar tipo de documento
                    doc_type = self._identify_document_type(text)
                    
                    return {
                        "text": text.strip(),
                        "pages": num_pages,
                        "status": "success",
                        "method": "pypdf",
                        "metadata": metadata,
                        "document_type": doc_type,
                        "char_count": len(text)
                    }
                else:
                    # Se pypdf não extraiu texto, tentar pdfplumber
                    raise Exception("pypdf não extraiu texto, tentando pdfplumber")
                    
            except Exception as pypdf_error:
                logger.debug(f"pypdf falhou ou não extraiu texto: {pypdf_error}")
                
                # 4. Fallback para pdfplumber (mais robusto)
                try:
                    logger.debug("Tentando extração com pdfplumber...")
                    
                    pdf_io.seek(0)  # Resetar o ponteiro
                    
                    with pdfplumber.open(pdf_io) as pdf:
                        num_pages = len(pdf.pages)
                        text = ""
                        tables_data = []
                        
                        for i, page in enumerate(pdf.pages):
                            try:
                                # Extrair texto
                                page_text = page.extract_text()
                                if page_text:
                                    text += f"\n--- Página {i+1} ---\n"
                                    text += page_text
                                
                                # Extrair tabelas se houver
                                tables = page.extract_tables()
                                if tables:
                                    for table in tables:
                                        tables_data.append({
                                            "page": i + 1,
                                            "data": table
                                        })
                                        # Adicionar tabela ao texto
                                        text += "\n[Tabela encontrada]\n"
                                        for row in table:
                                            text += " | ".join(str(cell) if cell else "" for cell in row) + "\n"
                                
                                # Verificar limite
                                if len(text) > max_chars:
                                    text = text[:max_chars]
                                    break
                                    
                            except Exception as e:
                                logger.debug(f"Erro ao processar página {i+1} com pdfplumber: {e}")
                                continue
                        
                        if text.strip():
                            emoji_logger.system_info(f"Texto extraído com pdfplumber: {len(text)} caracteres")
                            
                            doc_type = self._identify_document_type(text)
                            
                            return {
                                "text": text.strip(),
                                "pages": num_pages,
                                "status": "success",
                                "method": "pdfplumber",
                                "has_tables": len(tables_data) > 0,
                                "table_count": len(tables_data),
                                "document_type": doc_type,
                                "char_count": len(text)
                            }
                        else:
                            # PDF pode ser imagem (escaneado)
                            logger.warning("PDF parece ser escaneado (sem texto extraível)")
                            return {
                                "text": "",
                                "pages": num_pages,
                                "status": "no_text",
                                "error": "PDF parece ser escaneado. OCR necessário.",
                                "method": "none",
                                "suggestion": "Use análise de imagem para este documento"
                            }
                            
                except Exception as pdfplumber_error:
                    logger.error(f"pdfplumber também falhou: {pdfplumber_error}")
                    return {
                        "text": "",
                        "status": "error",
                        "error": f"Erro ao extrair texto: {str(pdfplumber_error)}"
                    }
                    
        except Exception as e:
            logger.exception(f"Erro crítico no DocumentExtractor: {e}")
            return {
                "text": "",
                "status": "error",
                "error": f"Erro crítico: {str(e)}"
            }
    
    async def extract_from_docx(
        self,
        docx_base64: str,
        max_chars: int = 10000
    ) -> Dict[str, Any]:
        """
        Extrai texto de um DOCX codificado em base64
        
        Args:
            docx_base64: DOCX codificado em base64
            max_chars: Número máximo de caracteres a extrair
            
        Returns:
            Dict com texto extraído e metadados
        """
        try:
            # Decodificar base64
            docx_bytes = base64.b64decode(docx_base64)
            
            # Criar arquivo temporário
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as temp_file:
                temp_file.write(docx_bytes)
                temp_path = temp_file.name
            
            try:
                # Extrair texto
                text = docx2txt.process(temp_path)
                
                if len(text) > max_chars:
                    text = text[:max_chars]
                
                doc_type = self._identify_document_type(text)
                
                return {
                    "text": text.strip(),
                    "status": "success",
                    "method": "docx2txt",
                    "document_type": doc_type,
                    "char_count": len(text)
                }
            finally:
                # Limpar arquivo temporário
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Erro ao extrair DOCX: {e}")
            return {
                "text": "",
                "status": "error",
                "error": f"Erro ao extrair DOCX: {str(e)}"
            }
    
    async def extract_from_document(
        self,
        document_base64: str,
        mimetype: str = "application/pdf",
        max_chars: int = 10000
    ) -> Dict[str, Any]:
        """
        Extrai texto de um documento baseado no mimetype
        
        Args:
            document_base64: Documento codificado em base64
            mimetype: Tipo MIME do documento
            max_chars: Número máximo de caracteres a extrair
            
        Returns:
            Dict com texto extraído e metadados
        """
        emoji_logger.system_info(f"Processando documento: {mimetype}")
        
        # Mapear mimetype para método de extração
        if "pdf" in mimetype.lower():
            return await self.extract_from_pdf(document_base64, max_chars)
        elif "word" in mimetype.lower() or "docx" in mimetype.lower():
            return await self.extract_from_docx(document_base64, max_chars)
        elif "text" in mimetype.lower() or "plain" in mimetype.lower():
            # Documento de texto simples
            try:
                text = base64.b64decode(document_base64).decode('utf-8', errors='ignore')
                if len(text) > max_chars:
                    text = text[:max_chars]
                    
                return {
                    "text": text,
                    "status": "success",
                    "method": "text",
                    "char_count": len(text)
                }
            except Exception as e:
                return {
                    "text": "",
                    "status": "error",
                    "error": f"Erro ao decodificar texto: {str(e)}"
                }
        else:
            return {
                "text": "",
                "status": "unsupported",
                "error": f"Tipo de documento não suportado: {mimetype}",
                "suggestion": "Suportamos PDF, DOCX e TXT"
            }
    
    def _identify_document_type(self, text: str) -> str:
        """
        Identifica o tipo de documento baseado no conteúdo
        
        Args:
            text: Texto extraído do documento
            
        Returns:
            Tipo identificado do documento
        """
        text_lower = text.lower()
        
        # Padrões para identificar tipos de documento
        patterns = {
            "conta_luz": ["conta de energia", "consumo kwh", "tarifa", "celpe", "light", "enel", "cpfl", "cemig"],
            "nota_fiscal": ["nota fiscal", "nf-e", "danfe", "cnpj", "icms", "cfop"],
            "boleto": ["boleto", "vencimento", "nosso número", "cedente", "sacado"],
            "contrato": ["contrato", "contratante", "contratado", "cláusula", "acordo"],
            "proposta": ["proposta", "orçamento", "valores", "condições", "validade"],
            "relatorio": ["relatório", "análise", "conclusão", "resultados", "gráfico"],
            "curriculo": ["currículo", "experiência profissional", "formação", "habilidades"],
            "receita": ["receita médica", "prescrição", "posologia", "medicamento"]
        }
        
        # Verificar cada padrão
        scores = {}
        for doc_type, keywords in patterns.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[doc_type] = score
        
        # Retornar tipo com maior score
        if scores:
            return max(scores, key=scores.get)
        
        return "documento_generico"

# Singleton global
document_extractor = DocumentExtractor()