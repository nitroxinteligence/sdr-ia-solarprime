-- =====================================================
-- Script para DESABILITAR RLS temporariamente (TESTES)
-- =====================================================
-- ATENÇÃO: Execute este script APENAS em ambiente de desenvolvimento/testes
-- NÃO USE EM PRODUÇÃO!
-- =====================================================

-- Desabilitar RLS nas tabelas
ALTER TABLE leads DISABLE ROW LEVEL SECURITY;
ALTER TABLE conversations DISABLE ROW LEVEL SECURITY;
ALTER TABLE messages DISABLE ROW LEVEL SECURITY;
ALTER TABLE lead_qualifications DISABLE ROW LEVEL SECURITY;
ALTER TABLE follow_ups DISABLE ROW LEVEL SECURITY;
ALTER TABLE analytics DISABLE ROW LEVEL SECURITY;

-- Para reabilitar RLS depois dos testes, use:
/*
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE lead_qualifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE follow_ups ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;
*/