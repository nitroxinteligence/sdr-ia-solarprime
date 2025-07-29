
        -- Tabela de métricas de performance
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            function_name VARCHAR(255) NOT NULL,
            metric_type VARCHAR(50) NOT NULL,
            value FLOAT NOT NULL,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Índices para queries rápidas
        CREATE INDEX idx_metrics_function ON performance_metrics(function_name);
        CREATE INDEX idx_metrics_timestamp ON performance_metrics(timestamp);
        CREATE INDEX idx_metrics_type ON performance_metrics(metric_type);
        
        -- Tabela de alertas
        CREATE TABLE IF NOT EXISTS performance_alerts (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            level VARCHAR(20) NOT NULL,
            message TEXT NOT NULL,
            details JSONB DEFAULT '{}',
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            resolved BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Índices
        CREATE INDEX idx_alerts_level ON performance_alerts(level);
        CREATE INDEX idx_alerts_timestamp ON performance_alerts(timestamp);
        CREATE INDEX idx_alerts_resolved ON performance_alerts(resolved);
        
        -- Tabela de relatórios
        CREATE TABLE IF NOT EXISTS performance_reports (
            id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
            report_data JSONB NOT NULL,
            sla_percentage FLOAT,
            total_requests INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Políticas RLS
        ALTER TABLE performance_metrics ENABLE ROW LEVEL SECURITY;
        ALTER TABLE performance_alerts ENABLE ROW LEVEL SECURITY;
        ALTER TABLE performance_reports ENABLE ROW LEVEL SECURITY;
        
        -- Acesso apenas para service role
        CREATE POLICY "Service role full access to metrics" ON performance_metrics
            FOR ALL USING (auth.role() = 'service_role');
            
        CREATE POLICY "Service role full access to alerts" ON performance_alerts
            FOR ALL USING (auth.role() = 'service_role');
            
        CREATE POLICY "Service role full access to reports" ON performance_reports
            FOR ALL USING (auth.role() = 'service_role');
        