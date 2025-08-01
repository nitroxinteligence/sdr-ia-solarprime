-- Funções para incrementar contadores de mensagens
-- Estas funções devem ser executadas no Supabase

-- Função para incrementar total_messages em conversations
CREATE OR REPLACE FUNCTION increment_conversation_messages(conv_id UUID)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE conversations 
    SET 
        total_messages = total_messages + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = conv_id;
END;
$$;

-- Função para incrementar total_messages em profiles
CREATE OR REPLACE FUNCTION increment_profile_messages(phone_number VARCHAR)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE profiles 
    SET 
        total_messages = total_messages + 1,
        last_interaction_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE phone = phone_number;
END;
$$;

-- Função combinada para incrementar ambos
CREATE OR REPLACE FUNCTION increment_message_counts(conv_id UUID, phone_number VARCHAR)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    -- Incrementar em conversations
    UPDATE conversations 
    SET 
        total_messages = total_messages + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = conv_id;
    
    -- Incrementar em profiles
    UPDATE profiles 
    SET 
        total_messages = total_messages + 1,
        last_interaction_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE phone = phone_number;
END;
$$;