"""
Testes para processamento de PDF
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import base64
from agents.sdr_agent import SDRAgent


class TestPDFProcessing:
    """Testes para processamento de documentos PDF"""
    
    @pytest.fixture
    def agent(self):
        """Fixture para criar agente SDR"""
        return SDRAgent()
    
    @pytest.fixture
    def mock_pdf_data(self):
        """Fixture com dados de PDF mockados"""
        return {
            'path': '/tmp/test_conta_luz.pdf',
            'filename': 'conta_luz.pdf',
            'mimetype': 'application/pdf'
        }
    
    @pytest.fixture
    def expected_bill_data(self):
        """Fixture com dados esperados de uma conta de luz"""
        return {
            "bill_value": "R$ 850,00",
            "consumption_kwh": "450",
            "reference_period": "12/2024",
            "customer_name": "João Silva",
            "address": "Rua das Flores, 123 - São Paulo/SP",
            "document": "123.456.789-00",
            "distributor": "Enel SP",
            "consumption_history": []
        }
    
    @pytest.mark.asyncio
    async def test_process_pdf_with_path(self, agent, mock_pdf_data, expected_bill_data):
        """Testa processamento de PDF com caminho do arquivo"""
        
        # Mock do PDFImageReader
        with patch('agents.sdr_agent.AGNO_READERS_AVAILABLE', True):
            with patch('agents.sdr_agent.PDFImageReader') as mock_pdf_reader:
                # Mock do Agent.run para retornar dados da conta
                mock_result = Mock()
                mock_result.content = f'{{"bill_value": "{expected_bill_data["bill_value"]}", "consumption_kwh": "{expected_bill_data["consumption_kwh"]}"}}'
                
                with patch('asyncio.to_thread', return_value=mock_result):
                    result = await agent._process_pdf_with_ocr(mock_pdf_data)
                    
                    assert result is not None
                    assert result['bill_value'] == expected_bill_data['bill_value']
                    assert result['_processed_by'] == 'agno_pdf_image_reader'
                    
                    # Verificar que PDFImageReader foi chamado com o path correto
                    mock_pdf_reader.assert_called_once_with(pdf=mock_pdf_data['path'])
    
    @pytest.mark.asyncio
    async def test_process_pdf_with_base64(self, agent):
        """Testa processamento de PDF com dados base64"""
        
        # Criar PDF base64 fake
        pdf_content = b"fake pdf content"
        pdf_base64 = base64.b64encode(pdf_content).decode()
        
        pdf_data = {
            'base64': pdf_base64,
            'filename': 'conta_luz.pdf'
        }
        
        with patch('agents.sdr_agent.AGNO_READERS_AVAILABLE', True):
            with patch('agents.sdr_agent.PDFImageReader') as mock_pdf_reader:
                with patch('tempfile.NamedTemporaryFile') as mock_temp_file:
                    mock_temp_file.return_value.__enter__.return_value.name = '/tmp/temp.pdf'
                    
                    mock_result = Mock()
                    mock_result.content = '{"bill_value": "R$ 500,00"}'
                    
                    with patch('asyncio.to_thread', return_value=mock_result):
                        with patch('os.unlink'):  # Mock para não tentar deletar arquivo
                            result = await agent._process_pdf_with_ocr(pdf_data)
                            
                            assert result is not None
                            assert result['_processed_by'] == 'agno_pdf_image_reader'
    
    @pytest.mark.asyncio
    async def test_process_pdf_fallback_to_image(self, agent, mock_pdf_data):
        """Testa fallback para processamento como imagem quando PDFImageReader falha"""
        
        # Simular falha do PDFImageReader
        with patch('agents.sdr_agent.AGNO_READERS_AVAILABLE', True):
            with patch('agents.sdr_agent.PDFImageReader', side_effect=Exception("PDFImageReader failed")):
                # Mock do pdf2image
                with patch('agents.sdr_agent.convert_from_path') as mock_convert:
                    mock_image = Mock()
                    mock_image.save = Mock()
                    mock_convert.return_value = [mock_image]
                    
                    # Mock da análise de imagem
                    with patch.object(agent, '_analyze_image_with_gemini', return_value={'bill_value': 'R$ 750,00'}):
                        with patch('os.unlink'):  # Mock para não tentar deletar arquivo
                            result = await agent._process_pdf_with_ocr(mock_pdf_data)
                            
                            assert result is not None
                            assert result['_processed_by'] == 'pdf2image_conversion'
                            assert result['_original_format'] == 'pdf'
    
    @pytest.mark.asyncio
    async def test_process_pdf_all_methods_fail(self, agent, mock_pdf_data):
        """Testa quando todos os métodos de processamento falham"""
        
        # Simular falha de todos os métodos
        with patch('agents.sdr_agent.AGNO_READERS_AVAILABLE', False):
            result = await agent._process_pdf_with_ocr(mock_pdf_data)
            
            assert result is not None
            assert result['media_received'] == 'pdf'
            assert result['analysis_status'] == 'processing_failed'
            assert 'suggestion' in result
            assert result['fallback'] == 'request_image'
    
    @pytest.mark.asyncio
    async def test_process_pdf_with_url(self, agent):
        """Testa processamento de PDF com URL"""
        
        pdf_data = {
            'url': 'https://example.com/conta_luz.pdf',
            'filename': 'conta_luz.pdf'
        }
        
        with patch('agents.sdr_agent.AGNO_READERS_AVAILABLE', True):
            with patch('agents.sdr_agent.PDFImageReader') as mock_pdf_reader:
                with patch('aiohttp.ClientSession') as mock_session:
                    # Mock da resposta HTTP
                    mock_response = AsyncMock()
                    mock_response.read = AsyncMock(return_value=b"fake pdf content")
                    
                    mock_session.return_value.__aenter__.return_value.get.return_value.__aenter__.return_value = mock_response
                    
                    with patch('tempfile.NamedTemporaryFile') as mock_temp_file:
                        mock_temp_file.return_value.__enter__.return_value.name = '/tmp/temp.pdf'
                        
                        mock_result = Mock()
                        mock_result.content = '{"bill_value": "R$ 600,00"}'
                        
                        with patch('asyncio.to_thread', return_value=mock_result):
                            with patch('os.unlink'):  # Mock para não tentar deletar arquivo
                                result = await agent._process_pdf_with_ocr(pdf_data)
                                
                                assert result is not None
                                assert result['_processed_by'] == 'agno_pdf_image_reader'
    
    @pytest.mark.asyncio
    async def test_parse_vision_result(self, agent):
        """Testa parsing de resultado da análise de visão"""
        
        # Teste com resultado válido
        mock_result = Mock()
        mock_result.content = '{"bill_value": "800", "consumption_kwh": "400"}'
        
        parsed = agent._parse_vision_result(mock_result)
        
        assert parsed is not None
        assert parsed['bill_value'] == 'R$ 800'  # Deve adicionar R$ automaticamente
        assert parsed['consumption_kwh'] == '400'
    
    @pytest.mark.asyncio
    async def test_parse_vision_result_with_code_markers(self, agent):
        """Testa parsing quando resultado tem marcadores de código"""
        
        mock_result = Mock()
        mock_result.content = '```json\n{"bill_value": "R$ 900,00"}\n```'
        
        parsed = agent._parse_vision_result(mock_result)
        
        assert parsed is not None
        assert parsed['bill_value'] == 'R$ 900,00'
    
    @pytest.mark.asyncio
    async def test_parse_vision_result_invalid_json(self, agent):
        """Testa parsing quando JSON é inválido"""
        
        mock_result = Mock()
        mock_result.content = 'Invalid JSON content'
        
        parsed = agent._parse_vision_result(mock_result)
        
        assert parsed is None
    
    @pytest.mark.asyncio
    async def test_process_pdf_integration_with_message(self, agent):
        """Testa integração do processamento de PDF com process_message"""
        
        pdf_data = {
            'path': '/tmp/conta_luz.pdf',
            'mimetype': 'application/pdf'
        }
        
        # Mock do processamento de PDF
        with patch.object(agent, '_process_pdf_with_ocr', return_value={
            'bill_value': 'R$ 1200,00',
            'consumption_kwh': '600',
            'customer_name': 'Maria Santos'
        }):
            # Mock dos repositórios
            with patch('agents.sdr_agent.lead_repository') as mock_lead_repo:
                with patch('agents.sdr_agent.conversation_repository') as mock_conv_repo:
                    with patch('agents.sdr_agent.message_repository') as mock_msg_repo:
                        # Mock do lead
                        mock_lead = Mock()
                        mock_lead.id = 'lead-123'
                        mock_lead_repo.create_or_update = AsyncMock(return_value=mock_lead)
                        
                        # Mock da conversa
                        mock_conv = Mock()
                        mock_conv.id = 'conv-123'
                        mock_conv_repo.create_or_resume = AsyncMock(return_value=mock_conv)
                        
                        # Mock das mensagens
                        mock_msg_repo.get_conversation_messages = AsyncMock(return_value=[])
                        mock_msg_repo.get_conversation_context = AsyncMock(return_value="")
                        mock_msg_repo.save_user_message = AsyncMock()
                        mock_msg_repo.save_assistant_message = AsyncMock()
                        
                        # Mock do agente
                        with patch.object(agent, '_run_agent', return_value="Analisei sua conta e vi que você paga R$ 1200,00..."):
                            response, metadata = await agent.process_message(
                                message="Aqui está minha conta de luz",
                                phone_number="+5511999999999",
                                media_type="document",
                                media_data=pdf_data
                            )
                            
                            assert response is not None
                            assert "1200" in response
                            assert metadata['stage'] is not None