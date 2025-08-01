# Migration Scripts

This directory contains scripts for migrating and managing the SDR IA SolarPrime agent system.

## migrate_to_modular.py

This script safely migrates the system from the old monolithic `sdr_agent.py` to the new modular agent architecture.

### Features

- **Pre-migration checks**: Validates environment, database, and service connectivity
- **Automatic backup**: Creates backups of database tables and configurations
- **Safe migration**: Updates webhooks and migrates active conversations
- **Rollback capability**: Can restore previous state if migration fails
- **Comprehensive logging**: Detailed logs of all migration steps
- **Validation**: Tests the new system before completing migration

### Prerequisites

1. Ensure all required environment variables are set in `.env`:
   ```
   SUPABASE_URL
   SUPABASE_KEY
   EVOLUTION_API_URL
   EVOLUTION_API_KEY
   EVOLUTION_INSTANCE
   KOMMO_SUBDOMAIN
   GOOGLE_API_KEY
   WEBHOOK_URL
   REDIS_URL
   ```

2. Ensure the new modular agent code is in place:
   - `agente/core/agent.py`
   - `agente/core/context_manager.py`
   - `agente/core/message_handler.py`
   - `agente/tools/` directory with all tools
   - `agente/integrations/` directory with integrations

3. Stop the current agent service:
   ```bash
   sudo systemctl stop sdr-agent
   ```

### Usage

1. **Run the migration**:
   ```bash
   cd /path/to/project
   python agente/scripts/migrate_to_modular.py
   ```

2. **Monitor the output**: The script will show progress for each step:
   - Environment variable checks
   - Service connectivity tests
   - Backup creation
   - Webhook updates
   - Cache clearing
   - Validation tests

3. **Check the results**:
   - Look for "✅ Migration completed successfully!" message
   - Review the migration report in `agente/scripts/reports/`
   - Check logs in `agente/scripts/logs/`

### What the Migration Does

1. **Pre-Migration Checks**:
   - Verifies all required environment variables
   - Tests database connectivity
   - Tests Redis connectivity
   - Tests Evolution API accessibility
   - Verifies new modular file structure

2. **Backup Creation**:
   - Backs up `agent_sessions`, `kommo_tokens`, and `follow_ups` tables
   - Saves current webhook configuration
   - Copies environment configuration

3. **Migration Steps**:
   - Updates Evolution API webhook to new `/webhook/modular` endpoint
   - Migrates active conversation sessions
   - Clears old Redis cache keys
   - Creates migration marker file

4. **Validation**:
   - Tests new webhook endpoint
   - Verifies tool accessibility
   - Checks integration files
   - Tests database connectivity through new system

5. **Rollback** (if needed):
   - Restores original webhook configuration
   - Removes migration markers
   - Cleans up migration metadata

### After Migration

1. **Update your web server configuration** to route `/webhook/modular` to the new handler:
   ```nginx
   location /webhook/modular {
       proxy_pass http://localhost:8000/webhook/whatsapp;
       # ... other proxy settings
   }
   ```

2. **Start the new agent service**:
   ```bash
   sudo systemctl start sdr-agent
   ```

3. **Monitor the system**:
   ```bash
   # Check logs
   tail -f /var/log/sdr-agent.log
   
   # Check webhook delivery
   curl -X GET https://your-evolution-api.com/webhook/find/your-instance \
        -H "apikey: your-api-key"
   ```

4. **Test with a message**:
   - Send a test message to the WhatsApp number
   - Verify it's processed by the new modular agent
   - Check that all integrations work correctly

### Rollback Procedure

If issues occur after migration, you can rollback:

1. **Automatic rollback** (if migration fails):
   - The script automatically rolls back on failure
   - Check logs for rollback status

2. **Manual rollback**:
   ```bash
   # Stop the service
   sudo systemctl stop sdr-agent
   
   # Restore webhook manually using Evolution API
   # Use the webhook configuration from backups/*/webhook_config.json
   
   # Remove migration marker
   rm .migration_completed
   
   # Update nginx to route back to old endpoint
   # Restart the old agent
   ```

### Troubleshooting

1. **Pre-migration checks fail**:
   - Verify all environment variables are set correctly
   - Check network connectivity to services
   - Ensure database credentials are valid

2. **Webhook update fails**:
   - Check Evolution API credentials
   - Verify instance name is correct
   - Check Evolution API is accessible

3. **Validation fails**:
   - Check nginx configuration for new route
   - Verify new agent files are in place
   - Check file permissions

4. **Active sessions issue**:
   - The migration preserves active sessions
   - They will be picked up by the new agent
   - Monitor for any conversation continuity issues

### Backup Location

Backups are stored in:
```
agente/scripts/backups/YYYYMMDD_HHMMSS/
├── agent_sessions.json
├── kommo_tokens.json
├── follow_ups.json
├── webhook_config.json
└── .env.backup
```

Keep these backups for at least 30 days after successful migration.

### Migration Reports

Reports are saved in:
```
agente/scripts/reports/migration_report_YYYYMMDD_HHMMSS.json
```

Each report contains:
- Migration status (success/rollback/rollback_failed)
- Timestamps
- Backup location
- Detailed status of each migration step

### Support

If you encounter issues:

1. Check the detailed logs in `agente/scripts/logs/`
2. Review the migration report
3. Ensure all prerequisites are met
4. Contact the development team with logs and reports

## google_calendar_health_check.py

Comprehensive health check script for Google Calendar integration following 2025 API standards.

### Features

- **Environment validation**: Checks all required environment variables
- **Service initialization**: Validates Google Calendar service setup
- **API connectivity**: Tests connection to Google Calendar API
- **Permissions check**: Validates calendar access permissions
- **Rate limiting**: Tests rate limiting functionality
- **Basic operations**: Tests create/read/delete operations

### Usage

```bash
# Run comprehensive health check
cd /path/to/project
python agente/scripts/google_calendar_health_check.py

# Exit codes:
# 0 = Healthy
# 1 = Healthy with warnings
# 2 = Unhealthy (problems detected)
# 3 = Critical error
```

### Sample Output

```
🔍 Iniciando verificação de saúde do Google Calendar...
============================================================
1. Verificando variáveis de ambiente...
   ✅ GOOGLE_PROJECT_ID: solar-prime-project
   ✅ GOOGLE_PRIVATE_KEY: -----BEGIN PRIVATE KEY-----...
   ✅ GOOGLE_SERVICE_ACCOUNT_EMAIL: service@solar-prime.iam.gserviceaccount.com
   ✅ GOOGLE_CALENDAR_ID: primary

2. Verificando inicialização do serviço...
   ✅ Serviço inicializado com sucesso
   📅 Calendar ID: primary
   🌍 Timezone: America/Sao_Paulo

3. Verificando conectividade com a API...
   ✅ Conectividade com API confirmada
   📊 Calendar: Solar Prime Calendar
   🆔 ID: primary

4. Verificando permissões do calendário...
   ✅ Permissão de leitura: OK (5 eventos encontrados)
   ✅ Permissões ACL: 3 regras

5. Verificando rate limiting...
   ✅ Rate limiting funcionando (5 requests em 1.23s)
   📊 Requests rastreados: 5

6. Verificando operações básicas...
   ✅ Verificação de disponibilidade: 12 slots encontrados
   ✅ Criação de evento: OK
   ✅ Exclusão de evento: OK

============================================================
📋 RELATÓRIO FINAL DE SAÚDE
============================================================
📊 Testes executados: 6
✅ Aprovados: 6
❌ Falharam: 0
⚠️  Avisos: 0

🎉 STATUS GERAL: SAUDÁVEL
```

## quick_calendar_check.py

Fast health check script for CI/CD pipelines and monitoring systems.

### Features

- **Quick validation**: Fast check of Google Calendar availability
- **CI/CD friendly**: Simple exit codes for automation
- **Minimal output**: Concise status reporting
- **Low overhead**: Optimized for frequent monitoring

### Usage

```bash
# Quick health check
python agente/scripts/quick_calendar_check.py

# Exit codes:
# 0 = Healthy
# 1 = Unhealthy or disabled
```

### Integration Examples

**CI/CD Pipeline**:
```yaml
# .github/workflows/health-check.yml
- name: Google Calendar Health Check
  run: python agente/scripts/quick_calendar_check.py
```

**Monitoring Script**:
```bash
#!/bin/bash
if python agente/scripts/quick_calendar_check.py; then
    echo "Google Calendar: OK"
else
    echo "Google Calendar: FAILED" | mail -s "Service Alert" admin@solarprime.com
fi
```

**Systemd Service Monitor**:
```ini
[Unit]
Description=Google Calendar Health Monitor
After=network.target

[Service]
Type=oneshot
ExecStart=/path/to/agente/scripts/quick_calendar_check.py
User=sdr-agent

[Install]
WantedBy=multi-user.target
```

## Future Scripts

Additional scripts that may be added:
- `backup_agent.py`: Regular backup automation
- `update_tools.py`: Tool registry updates
- `test_integrations.py`: Integration testing suite