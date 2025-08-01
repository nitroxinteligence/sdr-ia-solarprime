-- Função para incrementar contador de mensagens na conversa
CREATE OR REPLACE FUNCTION increment_conversation_messages(conversation_id UUID)
RETURNS void AS $$
BEGIN
    UPDATE conversations 
    SET total_messages = total_messages + 1,
        updated_at = NOW()
    WHERE id = conversation_id;
END;
$$ LANGUAGE plpgsql;

-- Função para incrementar contador de mensagens no profile
CREATE OR REPLACE FUNCTION increment_profile_messages(lead_id UUID)
RETURNS void AS $$
BEGIN
    UPDATE profiles 
    SET total_messages = COALESCE(total_messages, 0) + 1,
        updated_at = NOW()
    WHERE id = lead_id;
END;
$$ LANGUAGE plpgsql;