# 03. Sistema RAG com Supabase - Base de Conhecimento

Este documento detalha a implementação do sistema RAG (Retrieval Augmented Generation) usando Supabase com pgvector para criar uma base de conhecimento especializada em energia solar.

## 📋 Índice

1. [Visão Geral do RAG](#1-visão-geral-do-rag)
2. [Configuração do Supabase](#2-configuração-do-supabase)
3. [Setup do pgvector](#3-setup-do-pgvector)
4. [Sistema de Embeddings](#4-sistema-de-embeddings)
5. [Base de Conhecimento Solar](#5-base-de-conhecimento-solar)
6. [Integração com AGnO](#6-integração-com-agno)
7. [Pipeline de Ingestão](#7-pipeline-de-ingestão)
8. [Busca e Recuperação](#8-busca-e-recuperação)
9. [Otimização e Performance](#9-otimização-e-performance)
10. [Manutenção e Atualização](#10-manutenção-e-atualização)

---

## 1. Visão Geral do RAG

### 1.1 O que é RAG?

RAG (Retrieval Augmented Generation) combina:
- **Retrieval**: Busca de informações relevantes em uma base de conhecimento
- **Augmented**: Enriquecimento do contexto do LLM
- **Generation**: Geração de respostas precisas e contextualizadas

### 1.2 Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────┐
│                  FLUXO RAG                          │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Pergunta → Embedding → Busca Vetorial → Contexto  │
│                              ↓                      │
│                         Gemini 2.5 Pro              │
│                              ↓                      │
│                    Resposta Contextualizada         │
│                                                     │
├─────────────────────────────────────────────────────┤
│                   COMPONENTES                       │
├─────────────────────────────────────────────────────┤
│  • Supabase (PostgreSQL)                           │
│  • pgvector (Busca Vetorial)                       │
│  • OpenAI Embeddings / Gemini Embeddings           │
│  • AGnO Knowledge Base                             │
└─────────────────────────────────────────────────────┘
```

---

## 2. Configuração do Supabase

### 2.1 Criar Projeto no Supabase

```bash
# 1. Acesse https://supabase.com e crie uma conta
# 2. Crie um novo projeto
# 3. Anote as credenciais:
#    - Project URL
#    - Anon Key
#    - Service Role Key
#    - Database Password
```

### 2.2 Configurar Cliente Python

```python
# config/supabase_config.py
from supabase import create_client, Client
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class SupabaseConfig:
    """Configuração do Supabase"""
    
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not all([self.url, self.anon_key]):
            raise ValueError("Credenciais Supabase não configuradas")
        
        # Cliente com anon key (cliente)
        self.client: Client = create_client(self.url, self.anon_key)
        
        # Cliente com service key (admin)
        self.admin_client: Client = create_client(self.url, self.service_key)
    
    def get_client(self, admin: bool = False) -> Client:
        """Retorna cliente Supabase"""
        return self.admin_client if admin else self.client

# Instância global
supabase_config = SupabaseConfig()
```

---

## 3. Setup do pgvector

### 3.1 Habilitar Extensão pgvector

```sql
-- migrations/001_enable_pgvector.sql

-- Habilitar extensão pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar instalação
SELECT * FROM pg_extension WHERE extname = 'vector';
```

### 3.2 Criar Tabelas para RAG

```sql
-- migrations/002_create_knowledge_tables.sql

-- Tabela principal de documentos
CREATE TABLE IF NOT EXISTS documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL,
    source TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de chunks (pedaços de documentos)
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536), -- Dimensão para OpenAI embeddings
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índice para busca vetorial
    CONSTRAINT unique_document_chunk UNIQUE(document_id, chunk_index)
);

-- Criar índice para busca por similaridade
CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx 
ON document_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Tabela de categorias de conhecimento
CREATE TABLE IF NOT EXISTS knowledge_categories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    parent_id UUID REFERENCES knowledge_categories(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de perguntas frequentes
CREATE TABLE IF NOT EXISTS faq_entries (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category_id UUID REFERENCES knowledge_categories(id),
    embedding vector(1536),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para FAQs
CREATE INDEX IF NOT EXISTS faq_entries_embedding_idx 
ON faq_entries 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 50);

-- Tabela de feedback
CREATE TABLE IF NOT EXISTS knowledge_feedback (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    chunk_id UUID REFERENCES document_chunks(id),
    query TEXT NOT NULL,
    was_helpful BOOLEAN NOT NULL,
    feedback_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Função para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_faq_entries_updated_at BEFORE UPDATE ON faq_entries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 3.3 Executar Migrações

```python
# scripts/run_migrations.py
import os
from pathlib import Path
from config.supabase_config import supabase_config
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def run_migrations():
    """Executa migrações SQL"""
    
    # Conectar diretamente ao PostgreSQL
    conn_string = os.getenv("SUPABASE_DB_URL")
    conn = psycopg2.connect(conn_string)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Executar migrações
    migrations_dir = Path("migrations")
    
    for migration_file in sorted(migrations_dir.glob("*.sql")):
        print(f"Executando {migration_file.name}...")
        
        with open(migration_file, 'r') as f:
            sql = f.read()
            
        try:
            cursor.execute(sql)
            print(f"✅ {migration_file.name} executada com sucesso")
        except Exception as e:
            print(f"❌ Erro em {migration_file.name}: {e}")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_migrations()
```

---

## 4. Sistema de Embeddings

### 4.1 Configurar Embeddings

```python
# services/embeddings/embedding_service.py
from typing import List, Optional, Union
import openai
from abc import ABC, abstractmethod
import numpy as np
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

class EmbeddingService(ABC):
    """Interface base para serviços de embedding"""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Gera embedding para um texto"""
        pass
    
    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para múltiplos textos"""
        pass

class OpenAIEmbeddings(EmbeddingService):
    """Serviço de embeddings usando OpenAI"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        openai.api_key = api_key
        self.model = model
        self.dimension = 1536  # Dimensão do modelo
    
    async def embed_text(self, text: str) -> List[float]:
        """Gera embedding para um texto"""
        try:
            response = openai.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            raise
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para múltiplos textos"""
        try:
            response = openai.embeddings.create(
                model=self.model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Erro ao gerar embeddings em batch: {e}")
            raise

class GeminiEmbeddings(EmbeddingService):
    """Serviço de embeddings usando Google Gemini"""
    
    def __init__(self, api_key: str, model: str = "models/text-embedding-004"):
        genai.configure(api_key=api_key)
        self.model = model
        self.dimension = 768  # Dimensão do modelo Gemini
    
    async def embed_text(self, text: str) -> List[float]:
        """Gera embedding para um texto"""
        try:
            result = genai.embed_content(
                model=self.model,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Erro ao gerar embedding Gemini: {e}")
            raise
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Gera embeddings para múltiplos textos"""
        embeddings = []
        
        # Gemini não suporta batch nativo, processar um por vez
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        
        return embeddings
```

### 4.2 Chunking de Documentos

```python
# services/embeddings/text_chunker.py
from typing import List, Dict, Any
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

class TextChunker:
    """Divide textos em chunks otimizados para embeddings"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        separators: Optional[List[str]] = None
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        if separators is None:
            # Separadores em português
            separators = [
                "\n\n",  # Parágrafos
                "\n",    # Linhas
                ". ",    # Sentenças
                "! ",
                "? ",
                "; ",
                ": ",
                " ",     # Palavras
                ""       # Caracteres
            ]
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=self._token_length
        )
        
        # Encoder para contar tokens
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def _token_length(self, text: str) -> int:
        """Conta tokens usando tiktoken"""
        return len(self.encoding.encode(text))
    
    def split_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Divide texto em chunks com metadados"""
        
        # Limpar texto
        text = self._clean_text(text)
        
        # Dividir em chunks
        chunks = self.text_splitter.split_text(text)
        
        # Adicionar metadados
        chunk_docs = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = {
                "chunk_index": i,
                "chunk_size": len(chunk),
                "token_count": self._token_length(chunk)
            }
            
            if metadata:
                chunk_metadata.update(metadata)
            
            chunk_docs.append({
                "content": chunk,
                "metadata": chunk_metadata
            })
        
        return chunk_docs
    
    def _clean_text(self, text: str) -> str:
        """Limpa e normaliza texto"""
        # Remover múltiplos espaços
        text = re.sub(r'\s+', ' ', text)
        
        # Remover espaços no início e fim
        text = text.strip()
        
        # Normalizar quebras de linha
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text
    
    def split_markdown(self, markdown_text: str) -> List[Dict[str, Any]]:
        """Divide markdown preservando estrutura"""
        
        # Separadores específicos para markdown
        md_separators = [
            "\n## ",   # Seções H2
            "\n### ",  # Seções H3
            "\n#### ", # Seções H4
            "\n\n",    # Parágrafos
            "\n",      # Linhas
            ". ",      # Sentenças
            " "        # Palavras
        ]
        
        md_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=md_separators,
            length_function=self._token_length
        )
        
        chunks = md_splitter.split_text(markdown_text)
        
        # Extrair títulos e criar metadados
        chunk_docs = []
        current_section = ""
        
        for i, chunk in enumerate(chunks):
            # Tentar extrair seção do chunk
            section_match = re.search(r'^#+\s+(.+)$', chunk, re.MULTILINE)
            if section_match:
                current_section = section_match.group(1)
            
            chunk_docs.append({
                "content": chunk,
                "metadata": {
                    "chunk_index": i,
                    "section": current_section,
                    "format": "markdown",
                    "token_count": self._token_length(chunk)
                }
            })
        
        return chunk_docs
```

---

## 5. Base de Conhecimento Solar

### 5.1 Conteúdo Especializado

```python
# data/solar_knowledge.py
"""
Base de conhecimento sobre energia solar
"""

SOLAR_KNOWLEDGE = {
    "conceitos_basicos": {
        "title": "Conceitos Básicos de Energia Solar",
        "content": """
# Energia Solar Fotovoltaica

## O que é?
A energia solar fotovoltaica é a conversão direta da luz do sol em eletricidade através de painéis solares.

## Como funciona?
1. Os painéis solares captam a luz do sol
2. As células fotovoltaicas convertem a luz em corrente contínua (CC)
3. O inversor converte CC em corrente alternada (CA)
4. A energia é distribuída para uso ou injetada na rede

## Benefícios principais:
- Economia de até 95% na conta de luz
- Energia limpa e renovável
- Valorização do imóvel em até 10%
- Proteção contra aumentos tarifários
- Retorno do investimento em 3-5 anos
- Vida útil de 25-30 anos

## Tipos de sistemas:
1. **On-Grid (Conectado à rede)**: Mais comum, permite compensação de energia
2. **Off-Grid (Isolado)**: Com baterias, para locais sem rede elétrica
3. **Híbrido**: Combina on-grid com baterias para backup
        """,
        "category": "basico"
    },
    
    "economia_solar": {
        "title": "Economia com Energia Solar",
        "content": """
# Economia e Retorno do Investimento

## Cálculo de Economia
A economia depende de vários fatores:
- Consumo mensal (kWh)
- Tarifa de energia local
- Incidência solar da região
- Tipo e eficiência do sistema

## Exemplo prático:
- Conta mensal: R$ 500
- Sistema recomendado: 3.5 kWp
- Investimento: R$ 15.000
- Economia mensal: R$ 450 (90%)
- Payback: 33 meses

## Valorização do imóvel
Estudos mostram que imóveis com energia solar valorizam:
- Residências: 4-8%
- Comércios: 6-10%
- Indústrias: 5-12%

## Incentivos fiscais
- Isenção de ICMS sobre a energia compensada
- Financiamentos com juros reduzidos
- Linhas especiais para pessoa física e jurídica
        """,
        "category": "economia"
    },
    
    "processo_instalacao": {
        "title": "Processo de Instalação",
        "content": """
# Como é feita a instalação?

## Etapas do processo:

### 1. Análise e Projeto (1-2 dias)
- Visita técnica
- Análise do local e consumo
- Dimensionamento do sistema
- Projeto elétrico

### 2. Aprovação (15-30 dias)
- Documentação
- Aprovação na distribuidora
- Solicitação de acesso

### 3. Instalação (2-3 dias)
- Montagem da estrutura
- Instalação dos painéis
- Conexões elétricas
- Instalação do inversor

### 4. Vistoria e Ativação (7-15 dias)
- Vistoria da distribuidora
- Troca do medidor
- Ativação do sistema
- Início da geração

## Requisitos do local:
- Área disponível no telhado ou solo
- Boa incidência solar
- Estrutura adequada
- Acesso para manutenção
        """,
        "category": "instalacao"
    },
    
    "tipos_cliente": {
        "title": "Soluções por Tipo de Cliente",
        "content": """
# Soluções Personalizadas

## Residencial
- Sistemas de 2 a 10 kWp
- Economia de 50-95% na conta
- Instalação em telhado
- Monitoramento via app

## Comercial
- Sistemas de 10 a 100 kWp
- Redução de custos operacionais
- Melhoria da imagem sustentável
- Proteção contra bandeira tarifária

## Industrial
- Sistemas acima de 100 kWp
- Contratos de longo prazo
- Análise de demanda
- Gestão energética completa

## Rural
- Solução para agronegócio
- Irrigação solar
- Sistemas isolados
- Financiamento rural específico

## Condomínios
- Geração compartilhada
- Redução de áreas comuns
- Rateio entre condôminos
- Economia coletiva
        """,
        "category": "solucoes"
    },
    
    "perguntas_frequentes": {
        "title": "Perguntas Frequentes",
        "content": """
# Perguntas Frequentes sobre Energia Solar

## Funciona em dias nublados?
Sim! Os painéis geram energia mesmo em dias nublados, apenas com eficiência reduzida (20-50% da capacidade).

## E durante a noite?
À noite o sistema não gera, mas você usa a energia da rede e compensa com os créditos gerados durante o dia.

## Precisa de manutenção?
Mínima! Apenas limpeza ocasional (2-3x ao ano) e verificação anual do sistema.

## Quanto tempo dura?
- Painéis solares: 25-30 anos (com garantia)
- Inversores: 10-15 anos
- Sistema completo: 25+ anos

## Posso aumentar o sistema depois?
Sim! O sistema é modular e pode ser expandido conforme necessidade.

## E se eu mudar de casa?
O sistema valoriza o imóvel. Pode ser vendido junto ou desmontado e reinstalado.

## Resiste a granizo?
Sim! Os painéis são testados para resistir a granizo de até 25mm a 80km/h.

## Qual o prazo de instalação?
Em média 30-45 dias do contrato até a ativação completa.
        """,
        "category": "faq"
    },
    
    "marcos_legais": {
        "title": "Legislação e Regulamentação",
        "content": """
# Marco Legal da Energia Solar

## Lei 14.300/2022
- Marco legal da geração distribuída
- Regras de transição até 2045
- Mantém benefícios para quem instalar até 2025
- Segurança jurídica para investimentos

## Resolução 1000/2021 ANEEL
- Regras de conexão à rede
- Sistema de compensação
- Procedimentos simplificados
- Prazos definidos

## Benefícios mantidos:
- Compensação 1:1 até 2025
- Isenção de cobrança pelo uso da rede
- Créditos válidos por 60 meses
- Possibilidade de compartilhamento

## ICMS - Convênio 16/2015
- Isenção de ICMS sobre energia compensada
- Válido em todo território nacional
- Benefício automático
- Sem burocracia adicional
        """,
        "category": "legislacao"
    },
    
    "calculos_dimensionamento": {
        "title": "Como Dimensionar um Sistema Solar",
        "content": """
# Dimensionamento de Sistema Solar

## Fórmula básica:
Potência (kWp) = Consumo mensal (kWh) / (30 dias × HSP × 0.75)

Onde:
- HSP = Horas de Sol Pleno (média 4.5-5.5 em Pernambuco)
- 0.75 = Fator de eficiência do sistema

## Exemplo prático:
- Consumo: 500 kWh/mês
- HSP em Recife: 5.2
- Cálculo: 500 / (30 × 5.2 × 0.75) = 4.27 kWp

## Área necessária:
- 1 kWp ≈ 7m² (telhado inclinado)
- 1 kWp ≈ 10m² (laje plana)
- Painel típico: 2m² (400-450W)

## Quantidade de painéis:
- Sistema 4.27 kWp
- Painéis de 450W
- Quantidade: 4270W ÷ 450W = 9.5 ≈ 10 painéis

## Geração estimada:
- Sistema 4.27 kWp em Recife
- Geração: 4.27 × 5.2 × 30 × 0.75 = 500 kWh/mês
        """,
        "category": "tecnico"
    }
}

# FAQs específicas para vendas
SALES_FAQS = [
    {
        "question": "Qual o valor do investimento?",
        "answer": "O investimento varia conforme o tamanho do sistema necessário. Para uma residência com conta de R$ 300-500, o investimento fica entre R$ 12.000 e R$ 18.000, com retorno em 3-4 anos."
    },
    {
        "question": "Tem financiamento?",
        "answer": "Sim! Trabalhamos com diversas linhas de financiamento, incluindo bancos públicos e privados, com taxas a partir de 0,99% ao mês e até 84 meses para pagar."
    },
    {
        "question": "Quanto tempo demora para instalar?",
        "answer": "O processo completo leva em média 30-45 dias, incluindo projeto, aprovação na distribuidora, instalação e ativação do sistema."
    },
    {
        "question": "E se minha conta for baixa?",
        "answer": "Temos soluções para todos os perfis! Para contas abaixo de R$ 200, oferecemos planos de energia por assinatura com desconto garantido, sem investimento inicial."
    },
    {
        "question": "Vocês dão garantia?",
        "answer": "Sim! Oferecemos garantia de 12 meses na instalação, 10 anos no inversor e 25 anos de performance nos painéis solares. Além disso, temos seguro contra danos."
    }
]
```

### 5.2 Ingestão de Conhecimento

```python
# services/knowledge/knowledge_ingestion.py
import asyncio
from typing import List, Dict, Any
import logging
from datetime import datetime
from uuid import uuid4

from config.supabase_config import supabase_config
from services.embeddings.embedding_service import EmbeddingService
from services.embeddings.text_chunker import TextChunker
from data.solar_knowledge import SOLAR_KNOWLEDGE, SALES_FAQS

logger = logging.getLogger(__name__)

class KnowledgeIngestion:
    """Serviço de ingestão de conhecimento"""
    
    def __init__(
        self,
        embedding_service: EmbeddingService,
        chunker: TextChunker
    ):
        self.embedding_service = embedding_service
        self.chunker = chunker
        self.supabase = supabase_config.get_client(admin=True)
    
    async def ingest_documents(self, documents: List[Dict[str, Any]]):
        """Ingere múltiplos documentos"""
        
        for doc in documents:
            try:
                await self.ingest_document(
                    title=doc['title'],
                    content=doc['content'],
                    category=doc.get('category', 'geral'),
                    metadata=doc.get('metadata', {})
                )
                logger.info(f"Documento '{doc['title']}' ingerido com sucesso")
            except Exception as e:
                logger.error(f"Erro ao ingerir '{doc['title']}': {e}")
    
    async def ingest_document(
        self,
        title: str,
        content: str,
        category: str,
        metadata: Dict[str, Any] = None
    ) -> str:
        """Ingere um documento na base de conhecimento"""
        
        # Criar documento
        doc_data = {
            "title": title,
            "content": content,
            "category": category,
            "metadata": metadata or {},
            "source": metadata.get('source', 'manual')
        }
        
        doc_response = self.supabase.table("documents").insert(doc_data).execute()
        document_id = doc_response.data[0]['id']
        
        # Dividir em chunks
        chunks = self.chunker.split_markdown(content)
        
        # Gerar embeddings e salvar chunks
        for chunk in chunks:
            try:
                # Gerar embedding
                embedding = await self.embedding_service.embed_text(chunk['content'])
                
                # Preparar dados do chunk
                chunk_data = {
                    "document_id": document_id,
                    "chunk_index": chunk['metadata']['chunk_index'],
                    "content": chunk['content'],
                    "embedding": embedding,
                    "metadata": chunk['metadata']
                }
                
                # Salvar chunk
                self.supabase.table("document_chunks").insert(chunk_data).execute()
                
            except Exception as e:
                logger.error(f"Erro ao processar chunk: {e}")
        
        logger.info(f"Documento '{title}' processado com {len(chunks)} chunks")
        return document_id
    
    async def ingest_faqs(self, faqs: List[Dict[str, str]]):
        """Ingere perguntas frequentes"""
        
        for faq in faqs:
            try:
                # Gerar embedding da pergunta
                embedding = await self.embedding_service.embed_text(faq['question'])
                
                # Salvar FAQ
                faq_data = {
                    "question": faq['question'],
                    "answer": faq['answer'],
                    "embedding": embedding,
                    "category_id": None  # Pode ser associado a categoria depois
                }
                
                self.supabase.table("faq_entries").insert(faq_data).execute()
                
                logger.info(f"FAQ ingerida: {faq['question'][:50]}...")
                
            except Exception as e:
                logger.error(f"Erro ao ingerir FAQ: {e}")
    
    async def update_embeddings(self):
        """Atualiza embeddings de documentos existentes sem embeddings"""
        
        # Buscar chunks sem embeddings
        response = self.supabase.table("document_chunks")\
            .select("id, content")\
            .is_("embedding", "null")\
            .execute()
        
        chunks_to_update = response.data
        
        logger.info(f"Atualizando {len(chunks_to_update)} chunks sem embeddings")
        
        for chunk in chunks_to_update:
            try:
                # Gerar embedding
                embedding = await self.embedding_service.embed_text(chunk['content'])
                
                # Atualizar chunk
                self.supabase.table("document_chunks")\
                    .update({"embedding": embedding})\
                    .eq("id", chunk['id'])\
                    .execute()
                
            except Exception as e:
                logger.error(f"Erro ao atualizar chunk {chunk['id']}: {e}")
        
        logger.info("Atualização de embeddings concluída")

# Script de ingestão inicial
async def run_initial_ingestion():
    """Executa ingestão inicial da base de conhecimento"""
    
    # Configurar serviços
    from services.embeddings.embedding_service import OpenAIEmbeddings
    
    embedding_service = OpenAIEmbeddings(
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    chunker = TextChunker(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    ingestion = KnowledgeIngestion(embedding_service, chunker)
    
    # Ingerir documentos base
    documents = [
        {
            "title": doc_data["title"],
            "content": doc_data["content"],
            "category": doc_data["category"]
        }
        for doc_data in SOLAR_KNOWLEDGE.values()
    ]
    
    await ingestion.ingest_documents(documents)
    
    # Ingerir FAQs
    await ingestion.ingest_faqs(SALES_FAQS)
    
    logger.info("Ingestão inicial concluída!")

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    asyncio.run(run_initial_ingestion())
```

---

## 6. Integração com AGnO

### 6.1 Knowledge Base para AGnO

```python
# agents/knowledge/solar_knowledge_base.py
from agno.knowledge import AgentKnowledge
from agno.vectordb.base import VectorDb
from typing import List, Dict, Any, Optional
import numpy as np
from supabase import Client
import logging

logger = logging.getLogger(__name__)

class SupabaseVectorDB(VectorDb):
    """Adaptador Supabase para AGnO VectorDB"""
    
    def __init__(
        self,
        client: Client,
        table_name: str = "document_chunks",
        embedding_column: str = "embedding",
        content_column: str = "content",
        dimension: int = 1536
    ):
        self.client = client
        self.table_name = table_name
        self.embedding_column = embedding_column
        self.content_column = content_column
        self.dimension = dimension
    
    async def search(
        self,
        query_embedding: List[float],
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Busca por similaridade vetorial"""
        
        # Converter para string do PostgreSQL
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        
        # Construir query RPC
        query = self.client.rpc(
            'match_documents',
            {
                'query_embedding': embedding_str,
                'match_count': limit,
                'filter': filters or {}
            }
        )
        
        response = query.execute()
        
        return response.data
    
    async def upsert(
        self,
        documents: List[Dict[str, Any]]
    ):
        """Insere ou atualiza documentos"""
        
        for doc in documents:
            data = {
                self.content_column: doc['content'],
                self.embedding_column: doc['embedding'],
                'metadata': doc.get('metadata', {})
            }
            
            self.client.table(self.table_name).upsert(data).execute()
    
    def create_collection(self, name: str):
        """Não aplicável para Supabase"""
        pass
    
    def delete_collection(self, name: str):
        """Não aplicável para Supabase"""
        pass

class SolarKnowledgeBase:
    """Base de conhecimento solar para AGnO"""
    
    def __init__(
        self,
        supabase_client: Client,
        embedding_service: Any,
        search_type: str = "hybrid"
    ):
        self.supabase = supabase_client
        self.embedding_service = embedding_service
        self.search_type = search_type
        
        # Criar VectorDB adapter
        self.vector_db = SupabaseVectorDB(
            client=supabase_client,
            table_name="document_chunks"
        )
        
        # Criar AGnO Knowledge
        self.knowledge = AgentKnowledge(
            vector_db=self.vector_db,
            num_documents=5,
            search_type=search_type
        )
    
    async def search(
        self,
        query: str,
        limit: int = 5,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Busca conhecimento relevante"""
        
        # Gerar embedding da query
        query_embedding = await self.embedding_service.embed_text(query)
        
        # Aplicar filtros
        filters = {}
        if category:
            filters['category'] = category
        
        # Buscar documentos similares
        results = await self.vector_db.search(
            query_embedding=query_embedding,
            limit=limit,
            filters=filters
        )
        
        # Buscar também em FAQs
        faq_results = await self._search_faqs(query, query_embedding, limit)
        
        # Combinar resultados
        all_results = self._combine_results(results, faq_results)
        
        return all_results[:limit]
    
    async def _search_faqs(
        self,
        query: str,
        query_embedding: List[float],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Busca em perguntas frequentes"""
        
        embedding_str = f"[{','.join(map(str, query_embedding))}]"
        
        response = self.supabase.rpc(
            'match_faqs',
            {
                'query_embedding': embedding_str,
                'match_count': limit
            }
        ).execute()
        
        return response.data
    
    def _combine_results(
        self,
        doc_results: List[Dict[str, Any]],
        faq_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Combina resultados de documentos e FAQs"""
        
        combined = []
        
        # Adicionar FAQs com score alto primeiro
        for faq in faq_results:
            if faq.get('similarity', 0) > 0.85:
                combined.append({
                    'content': faq['answer'],
                    'type': 'faq',
                    'question': faq['question'],
                    'score': faq['similarity']
                })
        
        # Adicionar documentos
        for doc in doc_results:
            combined.append({
                'content': doc['content'],
                'type': 'document',
                'title': doc.get('title', ''),
                'score': doc.get('similarity', 0)
            })
        
        # Ordenar por score
        combined.sort(key=lambda x: x['score'], reverse=True)
        
        return combined
    
    async def add_feedback(
        self,
        chunk_id: str,
        query: str,
        was_helpful: bool,
        feedback_text: Optional[str] = None
    ):
        """Adiciona feedback sobre resultado"""
        
        feedback_data = {
            "chunk_id": chunk_id,
            "query": query,
            "was_helpful": was_helpful,
            "feedback_text": feedback_text
        }
        
        self.supabase.table("knowledge_feedback").insert(feedback_data).execute()
```

### 6.2 Funções SQL para Busca

```sql
-- migrations/003_create_search_functions.sql

-- Função para buscar documentos por similaridade
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),
    match_count int DEFAULT 5,
    filter jsonb DEFAULT '{}'::jsonb
)
RETURNS TABLE (
    id uuid,
    document_id uuid,
    content text,
    title text,
    category text,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dc.id,
        dc.document_id,
        dc.content,
        d.title,
        d.category,
        1 - (dc.embedding <=> query_embedding) as similarity
    FROM document_chunks dc
    JOIN documents d ON d.id = dc.document_id
    WHERE 
        (filter->>'category' IS NULL OR d.category = filter->>'category')
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Função para buscar FAQs por similaridade
CREATE OR REPLACE FUNCTION match_faqs(
    query_embedding vector(1536),
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id uuid,
    question text,
    answer text,
    similarity float,
    usage_count int
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.id,
        f.question,
        f.answer,
        1 - (f.embedding <=> query_embedding) as similarity,
        f.usage_count
    FROM faq_entries f
    WHERE f.embedding IS NOT NULL
    ORDER BY f.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Função para busca híbrida (vetorial + texto)
CREATE OR REPLACE FUNCTION hybrid_search(
    query_text text,
    query_embedding vector(1536),
    match_count int DEFAULT 5,
    text_weight float DEFAULT 0.3,
    vector_weight float DEFAULT 0.7
)
RETURNS TABLE (
    id uuid,
    content text,
    title text,
    combined_score float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH text_search AS (
        SELECT 
            dc.id,
            dc.content,
            d.title,
            ts_rank_cd(
                to_tsvector('portuguese', dc.content),
                plainto_tsquery('portuguese', query_text)
            ) as text_score
        FROM document_chunks dc
        JOIN documents d ON d.id = dc.document_id
        WHERE 
            to_tsvector('portuguese', dc.content) @@ 
            plainto_tsquery('portuguese', query_text)
    ),
    vector_search AS (
        SELECT 
            dc.id,
            1 - (dc.embedding <=> query_embedding) as vector_score
        FROM document_chunks dc
    )
    SELECT 
        COALESCE(ts.id, vs.id) as id,
        ts.content,
        ts.title,
        (
            COALESCE(ts.text_score, 0) * text_weight + 
            COALESCE(vs.vector_score, 0) * vector_weight
        ) as combined_score
    FROM text_search ts
    FULL OUTER JOIN vector_search vs ON ts.id = vs.id
    ORDER BY combined_score DESC
    LIMIT match_count;
END;
$$;

-- Índice para busca por texto
CREATE INDEX IF NOT EXISTS document_chunks_content_gin_idx 
ON document_chunks 
USING gin(to_tsvector('portuguese', content));

-- Atualizar contador de uso das FAQs
CREATE OR REPLACE FUNCTION increment_faq_usage()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE faq_entries 
    SET usage_count = usage_count + 1
    WHERE id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

## 7. Pipeline de Ingestão

### 7.1 Pipeline Automatizado

```python
# services/knowledge/ingestion_pipeline.py
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime
import hashlib
import logging
from pathlib import Path
import PyPDF2
import docx
import markdown

logger = logging.getLogger(__name__)

class IngestionPipeline:
    """Pipeline completo de ingestão de documentos"""
    
    def __init__(
        self,
        ingestion_service,
        supported_formats: List[str] = None
    ):
        self.ingestion_service = ingestion_service
        self.supported_formats = supported_formats or [
            '.txt', '.md', '.pdf', '.docx', '.doc'
        ]
    
    async def process_file(
        self,
        file_path: str,
        category: str = "geral",
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Processa um arquivo individual"""
        
        path = Path(file_path)
        
        if path.suffix.lower() not in self.supported_formats:
            logger.warning(f"Formato não suportado: {path.suffix}")
            return None
        
        # Extrair conteúdo baseado no tipo
        content = await self._extract_content(path)
        
        if not content:
            logger.error(f"Não foi possível extrair conteúdo de {file_path}")
            return None
        
        # Gerar hash para evitar duplicatas
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Verificar se já existe
        if await self._document_exists(content_hash):
            logger.info(f"Documento já existe: {path.name}")
            return None
        
        # Preparar metadados
        doc_metadata = {
            "file_name": path.name,
            "file_type": path.suffix,
            "file_size": path.stat().st_size,
            "content_hash": content_hash,
            "imported_at": datetime.utcnow().isoformat()
        }
        
        if metadata:
            doc_metadata.update(metadata)
        
        # Ingerir documento
        doc_id = await self.ingestion_service.ingest_document(
            title=path.stem,
            content=content,
            category=category,
            metadata=doc_metadata
        )
        
        return doc_id
    
    async def _extract_content(self, path: Path) -> Optional[str]:
        """Extrai conteúdo baseado no tipo de arquivo"""
        
        try:
            if path.suffix.lower() in ['.txt', '.md']:
                return self._extract_text(path)
            elif path.suffix.lower() == '.pdf':
                return self._extract_pdf(path)
            elif path.suffix.lower() in ['.docx', '.doc']:
                return self._extract_docx(path)
        except Exception as e:
            logger.error(f"Erro ao extrair conteúdo: {e}")
            return None
    
    def _extract_text(self, path: Path) -> str:
        """Extrai texto de arquivo texto/markdown"""
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Se for markdown, converter para texto
        if path.suffix.lower() == '.md':
            # Manter markdown para preservar estrutura
            return content
        
        return content
    
    def _extract_pdf(self, path: Path) -> str:
        """Extrai texto de PDF"""
        content = []
        
        with open(path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                content.append(page.extract_text())
        
        return '\n'.join(content)
    
    def _extract_docx(self, path: Path) -> str:
        """Extrai texto de DOCX"""
        doc = docx.Document(path)
        content = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                content.append(paragraph.text)
        
        return '\n'.join(content)
    
    async def _document_exists(self, content_hash: str) -> bool:
        """Verifica se documento já existe pelo hash"""
        
        response = self.ingestion_service.supabase\
            .table("documents")\
            .select("id")\
            .eq("metadata->>content_hash", content_hash)\
            .execute()
        
        return len(response.data) > 0
    
    async def process_directory(
        self,
        directory_path: str,
        category: str = "geral",
        recursive: bool = True
    ) -> Dict[str, Any]:
        """Processa todos os arquivos de um diretório"""
        
        dir_path = Path(directory_path)
        
        if not dir_path.exists() or not dir_path.is_dir():
            raise ValueError(f"Diretório inválido: {directory_path}")
        
        results = {
            "total_files": 0,
            "processed": 0,
            "skipped": 0,
            "errors": 0,
            "documents": []
        }
        
        # Buscar arquivos
        pattern = "**/*" if recursive else "*"
        
        for file_path in dir_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                results["total_files"] += 1
                
                try:
                    doc_id = await self.process_file(
                        str(file_path),
                        category=category
                    )
                    
                    if doc_id:
                        results["processed"] += 1
                        results["documents"].append({
                            "id": doc_id,
                            "file": str(file_path)
                        })
                    else:
                        results["skipped"] += 1
                        
                except Exception as e:
                    logger.error(f"Erro ao processar {file_path}: {e}")
                    results["errors"] += 1
        
        return results
```

### 7.2 Web Scraping para Conhecimento

```python
# services/knowledge/web_scraper.py
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import logging
from urllib.parse import urljoin, urlparse
import asyncio

logger = logging.getLogger(__name__)

class WebScraper:
    """Scraper para coletar conhecimento da web"""
    
    def __init__(
        self,
        ingestion_service,
        max_depth: int = 2,
        max_pages: int = 50
    ):
        self.ingestion_service = ingestion_service
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.visited_urls = set()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_website(
        self,
        start_url: str,
        category: str = "web",
        url_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Faz scraping de um website"""
        
        results = {
            "pages_scraped": 0,
            "pages_ingested": 0,
            "errors": 0
        }
        
        # Fila de URLs para processar
        queue = [(start_url, 0)]  # (url, depth)
        
        while queue and results["pages_scraped"] < self.max_pages:
            url, depth = queue.pop(0)
            
            if url in self.visited_urls:
                continue
            
            self.visited_urls.add(url)
            
            try:
                # Fazer scraping da página
                content, links = await self._scrape_page(url)
                
                if content:
                    # Ingerir conteúdo
                    await self._ingest_page(url, content, category)
                    results["pages_ingested"] += 1
                
                results["pages_scraped"] += 1
                
                # Adicionar links à fila se não exceder profundidade
                if depth < self.max_depth:
                    for link in links:
                        if url_filter and url_filter not in link:
                            continue
                        
                        if link not in self.visited_urls:
                            queue.append((link, depth + 1))
                
            except Exception as e:
                logger.error(f"Erro ao fazer scraping de {url}: {e}")
                results["errors"] += 1
        
        return results
    
    async def _scrape_page(self, url: str) -> tuple[Optional[str], List[str]]:
        """Faz scraping de uma página individual"""
        
        try:
            async with self.session.get(url, timeout=30) as response:
                if response.status != 200:
                    return None, []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remover scripts e estilos
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Extrair texto principal
                main_content = self._extract_main_content(soup)
                
                # Extrair links
                links = []
                for link in soup.find_all('a', href=True):
                    absolute_url = urljoin(url, link['href'])
                    
                    # Filtrar apenas links do mesmo domínio
                    if urlparse(absolute_url).netloc == urlparse(url).netloc:
                        links.append(absolute_url)
                
                return main_content, links
                
        except Exception as e:
            logger.error(f"Erro ao fazer scraping: {e}")
            return None, []
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extrai conteúdo principal da página"""
        
        # Tentar encontrar conteúdo principal
        main_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.content',
            '#content',
            '.post',
            '.entry-content'
        ]
        
        for selector in main_selectors:
            main = soup.select_one(selector)
            if main:
                return self._clean_text(main.get_text())
        
        # Fallback para body
        body = soup.find('body')
        if body:
            return self._clean_text(body.get_text())
        
        return ""
    
    def _clean_text(self, text: str) -> str:
        """Limpa texto extraído"""
        
        # Remover espaços extras
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        
        return '\n'.join(lines)
    
    async def _ingest_page(
        self,
        url: str,
        content: str,
        category: str
    ):
        """Ingere conteúdo da página"""
        
        # Extrair título da URL
        parsed = urlparse(url)
        title = parsed.path.strip('/').replace('/', ' - ') or parsed.netloc
        
        metadata = {
            "source": "web_scraping",
            "url": url,
            "domain": parsed.netloc
        }
        
        await self.ingestion_service.ingest_document(
            title=title,
            content=content,
            category=category,
            metadata=metadata
        )
```

---

## 8. Busca e Recuperação

### 8.1 Serviço de Busca Inteligente

```python
# services/knowledge/search_service.py
from typing import List, Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class SearchService:
    """Serviço de busca inteligente no conhecimento"""
    
    def __init__(
        self,
        knowledge_base,
        reranker=None
    ):
        self.knowledge_base = knowledge_base
        self.reranker = reranker
    
    async def search(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        search_type: str = "hybrid",
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """Busca inteligente com re-ranking opcional"""
        
        # Preprocessar query
        processed_query = self._preprocess_query(query)
        
        # Extrair intenção e palavras-chave
        intent, keywords = self._extract_intent(processed_query)
        
        # Ajustar filtros baseado na intenção
        if intent:
            filters = self._adjust_filters_by_intent(intent, filters)
        
        # Buscar resultados
        results = await self.knowledge_base.search(
            query=processed_query,
            limit=limit * 2,  # Buscar mais para re-ranking
            category=filters.get('category') if filters else None
        )
        
        # Re-rankear se disponível
        if self.reranker and len(results) > limit:
            results = await self._rerank_results(query, results)
        
        # Limitar resultados
        results = results[:limit]
        
        # Enriquecer com metadados se solicitado
        if include_metadata:
            results = self._enrich_results(results, keywords)
        
        # Registrar busca para analytics
        await self._log_search(query, len(results))
        
        return results
    
    def _preprocess_query(self, query: str) -> str:
        """Preprocessa query para melhorar busca"""
        
        # Remover pontuação excessiva
        query = re.sub(r'[!?.,;:]+', ' ', query)
        
        # Expandir abreviações comuns
        abbreviations = {
            'kwh': 'kilowatt hora',
            'kwp': 'kilowatt pico',
            'pv': 'fotovoltaico',
            'r$': 'reais',
            'conta luz': 'conta de luz'
        }
        
        query_lower = query.lower()
        for abbr, full in abbreviations.items():
            query_lower = query_lower.replace(abbr, full)
        
        return query_lower.strip()
    
    def _extract_intent(self, query: str) -> Tuple[Optional[str], List[str]]:
        """Extrai intenção e palavras-chave da query"""
        
        # Padrões de intenção
        intent_patterns = {
            'preco': ['quanto', 'valor', 'preço', 'custo', 'investimento'],
            'economia': ['economizar', 'economia', 'desconto', 'redução'],
            'instalacao': ['instalar', 'instalação', 'prazo', 'demora'],
            'funcionamento': ['funciona', 'como', 'processo', 'etapas'],
            'beneficio': ['vantagem', 'benefício', 'porque', 'vale a pena'],
            'tecnico': ['kwp', 'potência', 'geração', 'eficiência', 'painel']
        }
        
        query_lower = query.lower()
        detected_intent = None
        keywords = []
        
        # Detectar intenção
        for intent, patterns in intent_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                detected_intent = intent
                keywords.extend([p for p in patterns if p in query_lower])
                break
        
        # Extrair palavras-chave adicionais
        important_words = [
            'solar', 'energia', 'painel', 'usina', 'conta', 'luz',
            'economia', 'desconto', 'financiamento', 'garantia'
        ]
        
        keywords.extend([w for w in important_words if w in query_lower])
        
        # Remover duplicatas
        keywords = list(set(keywords))
        
        return detected_intent, keywords
    
    def _adjust_filters_by_intent(
        self,
        intent: str,
        filters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Ajusta filtros baseado na intenção"""
        
        if filters is None:
            filters = {}
        
        # Mapear intenção para categorias
        intent_category_map = {
            'preco': ['economia', 'faq'],
            'economia': ['economia', 'basico'],
            'instalacao': ['instalacao', 'faq'],
            'funcionamento': ['basico', 'tecnico'],
            'beneficio': ['basico', 'economia'],
            'tecnico': ['tecnico', 'instalacao']
        }
        
        if intent in intent_category_map:
            filters['preferred_categories'] = intent_category_map[intent]
        
        return filters
    
    async def _rerank_results(
        self,
        query: str,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Re-rankeia resultados para melhor relevância"""
        
        # Por ora, implementação simples baseada em scores
        # Em produção, usar modelo de re-ranking dedicado
        
        reranked = []
        
        for result in results:
            score = result.get('score', 0)
            
            # Boost para FAQs relevantes
            if result.get('type') == 'faq':
                score *= 1.2
            
            # Boost para match exato de palavras-chave
            content_lower = result['content'].lower()
            query_words = query.lower().split()
            
            exact_matches = sum(1 for word in query_words if word in content_lower)
            score += exact_matches * 0.1
            
            result['reranked_score'] = score
            reranked.append(result)
        
        # Ordenar por novo score
        reranked.sort(key=lambda x: x['reranked_score'], reverse=True)
        
        return reranked
    
    def _enrich_results(
        self,
        results: List[Dict[str, Any]],
        keywords: List[str]
    ) -> List[Dict[str, Any]]:
        """Enriquece resultados com metadados úteis"""
        
        enriched = []
        
        for result in results:
            # Destacar palavras-chave no conteúdo
            highlighted_content = result['content']
            
            for keyword in keywords:
                pattern = re.compile(f'({keyword})', re.IGNORECASE)
                highlighted_content = pattern.sub(r'**\1**', highlighted_content)
            
            result['highlighted_content'] = highlighted_content
            
            # Adicionar preview
            result['preview'] = result['content'][:200] + '...' if len(result['content']) > 200 else result['content']
            
            enriched.append(result)
        
        return enriched
    
    async def _log_search(self, query: str, result_count: int):
        """Registra busca para analytics"""
        
        # Em produção, salvar no banco para análise
        logger.info(f"Busca realizada: '{query}' - {result_count} resultados")
```

### 8.2 Integração no Agente

```python
# agents/integrations/knowledge_integration.py
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class KnowledgeAugmentedAgent:
    """Mixin para adicionar RAG ao agente"""
    
    def __init__(self, knowledge_base, search_service):
        self.knowledge_base = knowledge_base
        self.search_service = search_service
    
    async def augment_prompt_with_knowledge(
        self,
        user_message: str,
        conversation_context: Dict[str, Any],
        max_knowledge_pieces: int = 3
    ) -> str:
        """Aumenta prompt com conhecimento relevante"""
        
        # Buscar conhecimento relevante
        knowledge_results = await self.search_service.search(
            query=user_message,
            limit=max_knowledge_pieces,
            search_type="hybrid"
        )
        
        if not knowledge_results:
            return ""
        
        # Formatar conhecimento para o prompt
        knowledge_context = self._format_knowledge_context(knowledge_results)
        
        # Criar prompt aumentado
        augmented_prompt = f"""
CONHECIMENTO RELEVANTE:
{knowledge_context}

Com base no conhecimento acima e no contexto da conversa, responda a pergunta do cliente.
Se a informação estiver disponível no conhecimento, use-a para dar uma resposta precisa.
Se não houver informação suficiente, diga que vai verificar com a equipe técnica.
        """
        
        return augmented_prompt
    
    def _format_knowledge_context(
        self,
        results: List[Dict[str, Any]]
    ) -> str:
        """Formata resultados do conhecimento para o contexto"""
        
        formatted_pieces = []
        
        for i, result in enumerate(results, 1):
            if result['type'] == 'faq':
                piece = f"""
{i}. PERGUNTA: {result.get('question', 'N/A')}
   RESPOSTA: {result['content']}
                """
            else:
                piece = f"""
{i}. {result.get('title', 'Informação')}:
   {result['content']}
                """
            
            formatted_pieces.append(piece.strip())
        
        return '\n\n'.join(formatted_pieces)
    
    async def check_faq_before_llm(
        self,
        user_message: str
    ) -> Optional[str]:
        """Verifica se é uma FAQ antes de usar o LLM"""
        
        # Buscar apenas FAQs com alta similaridade
        results = await self.knowledge_base._search_faqs(
            query=user_message,
            query_embedding=await self.knowledge_base.embedding_service.embed_text(user_message),
            limit=1
        )
        
        if results and results[0].get('similarity', 0) > 0.9:
            # FAQ muito similar encontrada
            faq = results[0]
            
            # Incrementar contador de uso
            await self.knowledge_base.supabase\
                .table("faq_entries")\
                .update({"usage_count": faq['usage_count'] + 1})\
                .eq("id", faq['id'])\
                .execute()
            
            return faq['answer']
        
        return None
```

---

## 9. Otimização e Performance

### 9.1 Cache de Embeddings

```python
# services/knowledge/embedding_cache.py
import redis
import hashlib
import json
from typing import List, Optional
import numpy as np
import logging

logger = logging.getLogger(__name__)

class EmbeddingCache:
    """Cache para embeddings"""
    
    def __init__(self, redis_url: str, ttl_seconds: int = 86400):
        self.redis_client = redis.from_url(redis_url)
        self.ttl = ttl_seconds
        self.prefix = "embedding:"
    
    def _get_cache_key(self, text: str) -> str:
        """Gera chave de cache para texto"""
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"{self.prefix}{text_hash}"
    
    async def get(self, text: str) -> Optional[List[float]]:
        """Busca embedding no cache"""
        try:
            key = self._get_cache_key(text)
            cached = self.redis_client.get(key)
            
            if cached:
                embedding = json.loads(cached)
                logger.debug(f"Cache hit para embedding: {text[:50]}...")
                return embedding
            
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cache de embedding: {e}")
            return None
    
    async def set(self, text: str, embedding: List[float]):
        """Salva embedding no cache"""
        try:
            key = self._get_cache_key(text)
            self.redis_client.setex(
                key,
                self.ttl,
                json.dumps(embedding)
            )
            logger.debug(f"Embedding cacheado: {text[:50]}...")
        except Exception as e:
            logger.error(f"Erro ao cachear embedding: {e}")
    
    async def get_batch(
        self,
        texts: List[str]
    ) -> Tuple[List[Optional[List[float]]], List[int]]:
        """Busca múltiplos embeddings no cache"""
        
        embeddings = []
        missing_indices = []
        
        for i, text in enumerate(texts):
            embedding = await self.get(text)
            
            if embedding is None:
                missing_indices.append(i)
            
            embeddings.append(embedding)
        
        return embeddings, missing_indices
    
    async def set_batch(
        self,
        texts: List[str],
        embeddings: List[List[float]]
    ):
        """Salva múltiplos embeddings no cache"""
        
        for text, embedding in zip(texts, embeddings):
            await self.set(text, embedding)
```

### 9.2 Otimização de Busca

```python
# services/knowledge/search_optimizer.py
from typing import List, Dict, Any
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

class SearchOptimizer:
    """Otimizador de busca vetorial"""
    
    def __init__(self):
        self.query_cache = {}
        self.result_cache = {}
    
    def optimize_query_embedding(
        self,
        query_embedding: List[float],
        boost_factors: Dict[str, float] = None
    ) -> List[float]:
        """Otimiza embedding da query com boost factors"""
        
        if boost_factors is None:
            return query_embedding
        
        # Aplicar boosts baseados em contexto
        # Em produção, isso seria mais sofisticado
        optimized = np.array(query_embedding)
        
        # Exemplo: boost para termos importantes
        if boost_factors.get('technical_boost'):
            # Aumentar dimensões relacionadas a termos técnicos
            technical_dims = range(100, 200)  # Exemplo
            optimized[technical_dims] *= boost_factors['technical_boost']
        
        # Normalizar
        norm = np.linalg.norm(optimized)
        if norm > 0:
            optimized = optimized / norm
        
        return optimized.tolist()
    
    def cluster_results(
        self,
        results: List[Dict[str, Any]],
        n_clusters: int = 3
    ) -> List[List[Dict[str, Any]]]:
        """Agrupa resultados similares"""
        
        if len(results) <= n_clusters:
            return [[r] for r in results]
        
        # Extrair embeddings dos resultados
        embeddings = []
        for result in results:
            if 'embedding' in result:
                embeddings.append(result['embedding'])
            else:
                # Fallback para score
                embeddings.append([result.get('score', 0)])
        
        # Calcular matriz de similaridade
        embeddings_array = np.array(embeddings)
        similarities = cosine_similarity(embeddings_array)
        
        # Clustering simples
        clusters = [[] for _ in range(n_clusters)]
        assigned = set()
        
        for i in range(len(results)):
            if i in assigned:
                continue
            
            # Encontrar cluster para este resultado
            cluster_idx = i % n_clusters
            clusters[cluster_idx].append(results[i])
            assigned.add(i)
            
            # Adicionar resultados similares ao mesmo cluster
            for j in range(len(results)):
                if j not in assigned and similarities[i][j] > 0.8:
                    clusters[cluster_idx].append(results[j])
                    assigned.add(j)
        
        # Remover clusters vazios
        clusters = [c for c in clusters if c]
        
        return clusters
    
    def diversify_results(
        self,
        results: List[Dict[str, Any]],
        diversity_factor: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Diversifica resultados para evitar redundância"""
        
        if len(results) <= 1:
            return results
        
        diversified = [results[0]]  # Sempre incluir o melhor
        
        for candidate in results[1:]:
            # Calcular similaridade máxima com resultados já selecionados
            max_similarity = 0
            
            for selected in diversified:
                # Comparar conteúdo
                sim = self._content_similarity(
                    candidate.get('content', ''),
                    selected.get('content', '')
                )
                max_similarity = max(max_similarity, sim)
            
            # Incluir se suficientemente diferente
            if max_similarity < (1 - diversity_factor):
                diversified.append(candidate)
        
        return diversified
    
    def _content_similarity(self, text1: str, text2: str) -> float:
        """Calcula similaridade entre textos"""
        
        # Implementação simples baseada em palavras comuns
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
```

---

## 10. Manutenção e Atualização

### 10.1 Sistema de Atualização

```python
# services/knowledge/knowledge_updater.py
from typing import List, Dict, Any
import asyncio
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class KnowledgeUpdater:
    """Sistema de atualização da base de conhecimento"""
    
    def __init__(
        self,
        ingestion_service,
        search_service,
        update_interval_hours: int = 24
    ):
        self.ingestion_service = ingestion_service
        self.search_service = search_service
        self.update_interval = timedelta(hours=update_interval_hours)
        self.last_update = None
    
    async def check_for_updates(self) -> List[Dict[str, Any]]:
        """Verifica documentos que precisam atualização"""
        
        # Buscar documentos antigos
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        response = self.ingestion_service.supabase\
            .table("documents")\
            .select("id, title, updated_at")\
            .lt("updated_at", cutoff_date.isoformat())\
            .execute()
        
        outdated_docs = response.data
        
        # Buscar documentos com baixo feedback
        response = self.ingestion_service.supabase\
            .table("knowledge_feedback")\
            .select("chunk_id, COUNT(*)")\
            .eq("was_helpful", False)\
            .execute()
        
        # Processar feedback
        problematic_chunks = []
        for feedback in response.data:
            if feedback['count'] > 5:  # Mais de 5 feedbacks negativos
                problematic_chunks.append(feedback['chunk_id'])
        
        return {
            'outdated_documents': outdated_docs,
            'problematic_chunks': problematic_chunks
        }
    
    async def update_document(
        self,
        document_id: str,
        new_content: str
    ):
        """Atualiza um documento existente"""
        
        # Buscar documento atual
        response = self.ingestion_service.supabase\
            .table("documents")\
            .select("*")\
            .eq("id", document_id)\
            .single()\
            .execute()
        
        if not response.data:
            logger.error(f"Documento {document_id} não encontrado")
            return
        
        document = response.data
        
        # Deletar chunks antigos
        self.ingestion_service.supabase\
            .table("document_chunks")\
            .delete()\
            .eq("document_id", document_id)\
            .execute()
        
        # Reprocessar documento
        await self.ingestion_service.ingest_document(
            title=document['title'],
            content=new_content,
            category=document['category'],
            metadata={
                **document['metadata'],
                'updated_from': document_id,
                'update_reason': 'scheduled_update'
            }
        )
        
        logger.info(f"Documento {document['title']} atualizado")
    
    async def cleanup_duplicates(self):
        """Remove documentos duplicados"""
        
        # Buscar possíveis duplicatas por título
        response = self.ingestion_service.supabase\
            .table("documents")\
            .select("id, title, created_at")\
            .order("created_at")\
            .execute()
        
        documents = response.data
        seen_titles = {}
        duplicates = []
        
        for doc in documents:
            title_lower = doc['title'].lower().strip()
            
            if title_lower in seen_titles:
                # Manter o mais antigo
                duplicates.append(doc['id'])
            else:
                seen_titles[title_lower] = doc['id']
        
        # Deletar duplicatas
        for dup_id in duplicates:
            self.ingestion_service.supabase\
                .table("documents")\
                .delete()\
                .eq("id", dup_id)\
                .execute()
            
            logger.info(f"Documento duplicado removido: {dup_id}")
        
        return len(duplicates)
    
    async def optimize_embeddings(self):
        """Otimiza embeddings existentes"""
        
        # Re-gerar embeddings com modelo mais recente
        await self.ingestion_service.update_embeddings()
        
        # Recalcular índices
        # Em produção, isso seria feito via SQL
        logger.info("Embeddings otimizados")
```

### 10.2 Monitoramento de Qualidade

```python
# services/knowledge/quality_monitor.py
from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class QualityMonitor:
    """Monitora qualidade da base de conhecimento"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    async def generate_quality_report(self) -> Dict[str, Any]:
        """Gera relatório de qualidade"""
        
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'metrics': {}
        }
        
        # Métrica 1: Cobertura de tópicos
        coverage = await self._calculate_topic_coverage()
        report['metrics']['topic_coverage'] = coverage
        
        # Métrica 2: Feedback dos usuários
        feedback_stats = await self._analyze_feedback()
        report['metrics']['user_feedback'] = feedback_stats
        
        # Métrica 3: Uso de FAQs
        faq_usage = await self._analyze_faq_usage()
        report['metrics']['faq_effectiveness'] = faq_usage
        
        # Métrica 4: Gaps de conhecimento
        knowledge_gaps = await self._identify_knowledge_gaps()
        report['metrics']['knowledge_gaps'] = knowledge_gaps
        
        return report
    
    async def _calculate_topic_coverage(self) -> Dict[str, Any]:
        """Calcula cobertura por categoria"""
        
        response = self.supabase\
            .table("documents")\
            .select("category, COUNT(*)")\
            .execute()
        
        coverage = {}
        for row in response.data:
            coverage[row['category']] = row['count']
        
        # Categorias esperadas
        expected_categories = [
            'basico', 'economia', 'instalacao', 
            'solucoes', 'faq', 'legislacao', 'tecnico'
        ]
        
        missing_categories = [
            cat for cat in expected_categories 
            if cat not in coverage
        ]
        
        return {
            'categories': coverage,
            'missing_categories': missing_categories,
            'total_documents': sum(coverage.values())
        }
    
    async def _analyze_feedback(self) -> Dict[str, Any]:
        """Analisa feedback dos usuários"""
        
        # Feedback positivo vs negativo
        response = self.supabase\
            .table("knowledge_feedback")\
            .select("was_helpful, COUNT(*)")\
            .execute()
        
        positive = 0
        negative = 0
        
        for row in response.data:
            if row['was_helpful']:
                positive = row['count']
            else:
                negative = row['count']
        
        total = positive + negative
        satisfaction_rate = positive / total if total > 0 else 0
        
        return {
            'total_feedback': total,
            'positive': positive,
            'negative': negative,
            'satisfaction_rate': satisfaction_rate
        }
    
    async def _analyze_faq_usage(self) -> Dict[str, Any]:
        """Analisa uso de FAQs"""
        
        # FAQs mais usadas
        response = self.supabase\
            .table("faq_entries")\
            .select("question, usage_count")\
            .order("usage_count", desc=True)\
            .limit(10)\
            .execute()
        
        top_faqs = response.data
        
        # FAQs não usadas
        response = self.supabase\
            .table("faq_entries")\
            .select("COUNT(*)")\
            .eq("usage_count", 0)\
            .execute()
        
        unused_count = response.data[0]['count'] if response.data else 0
        
        return {
            'top_faqs': top_faqs,
            'unused_faq_count': unused_count
        }
    
    async def _identify_knowledge_gaps(self) -> List[str]:
        """Identifica gaps no conhecimento"""
        
        # Queries sem resultados satisfatórios
        # Em produção, isso viria de logs de busca
        
        gaps = []
        
        # Exemplo: verificar feedbacks negativos
        response = self.supabase\
            .table("knowledge_feedback")\
            .select("query")\
            .eq("was_helpful", False)\
            .execute()
        
        failed_queries = [f['query'] for f in response.data]
        
        # Agrupar queries similares
        # Implementação simplificada
        unique_topics = list(set(failed_queries))[:10]
        
        return unique_topics
```

---

## 🎉 Conclusão

Parabéns! Você implementou um sistema RAG completo com Supabase e pgvector.

### Checklist de Conclusão:
- [ ] Supabase configurado
- [ ] pgvector habilitado
- [ ] Tabelas criadas
- [ ] Sistema de embeddings funcionando
- [ ] Base de conhecimento populada
- [ ] Busca vetorial implementada
- [ ] Integração com AGnO completa
- [ ] Pipeline de ingestão pronto
- [ ] Otimizações aplicadas
- [ ] Sistema de manutenção configurado

### Próximos Passos:
1. Popular a base com mais conhecimento específico
2. Implementar API e webhooks: [04-api-webhooks.md](04-api-webhooks.md)
3. Treinar re-ranker customizado
4. Adicionar mais fontes de conhecimento

---

**💡 Dica**: Execute o script de ingestão inicial para popular a base de conhecimento antes de prosseguir.