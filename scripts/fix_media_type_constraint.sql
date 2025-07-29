-- =====================================================
-- Correção da constraint media_type para aceitar 'buffered'
-- =====================================================

-- Primeiro, remover a constraint existente
ALTER TABLE messages 
DROP CONSTRAINT IF EXISTS messages_media_type_check;

-- Adicionar nova constraint incluindo 'buffered'
ALTER TABLE messages 
ADD CONSTRAINT messages_media_type_check 
CHECK (media_type IN ('image', 'audio', 'video', 'document', 'buffered', 'text'));

-- Verificar se funcionou
SELECT 
    conname AS constraint_name,
    pg_get_constraintdef(oid) AS constraint_definition
FROM pg_constraint
WHERE conrelid = 'messages'::regclass
AND conname = 'messages_media_type_check';