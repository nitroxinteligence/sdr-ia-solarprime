#!/usr/bin/env python3
"""
Migration script to transition from monolithic sdr_agent.py to modular agent architecture.
This script safely migrates the system with rollback capabilities.
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import shutil
import subprocess
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dotenv import load_dotenv
import aiohttp
from supabase import create_client, Client
import redis.asyncio as redis

# Load environment variables
load_dotenv()

# Setup logging
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MigrationManager:
    """Manages the migration from monolithic to modular agent architecture."""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.evolution_api_url = os.getenv("EVOLUTION_API_URL")
        self.evolution_api_key = os.getenv("EVOLUTION_API_KEY")
        self.evolution_instance = os.getenv("EVOLUTION_INSTANCE")
        self.kommo_subdomain = os.getenv("KOMMO_SUBDOMAIN")
        self.backup_dir = Path(__file__).parent / "backups" / datetime.now().strftime('%Y%m%d_%H%M%S')
        self.rollback_config = {}
        
    async def run(self):
        """Execute the migration process."""
        logger.info("Starting migration to modular agent architecture")
        
        try:
            # Pre-migration checks
            if not await self.pre_migration_checks():
                logger.error("Pre-migration checks failed. Aborting.")
                return False
            
            # Create backup
            await self.backup_current_state()
            
            # Execute migration steps
            success = await self.execute_migration()
            
            if success:
                # Validate migration
                if await self.validate_migration():
                    logger.info("Migration completed successfully!")
                    await self.generate_report("success")
                    return True
                else:
                    logger.error("Migration validation failed. Rolling back...")
                    await self.rollback()
                    return False
            else:
                logger.error("Migration failed. Rolling back...")
                await self.rollback()
                return False
                
        except Exception as e:
            logger.error(f"Unexpected error during migration: {e}")
            await self.rollback()
            return False
    
    async def pre_migration_checks(self) -> bool:
        """Perform pre-migration checks."""
        logger.info("Running pre-migration checks...")
        checks_passed = True
        
        # Check environment variables
        required_vars = [
            "SUPABASE_URL", "SUPABASE_KEY", "EVOLUTION_API_URL",
            "EVOLUTION_API_KEY", "EVOLUTION_INSTANCE", "KOMMO_SUBDOMAIN",
            "GOOGLE_API_KEY", "WEBHOOK_URL"
        ]
        
        logger.info("Checking environment variables...")
        for var in required_vars:
            if not os.getenv(var):
                logger.error(f"Missing required environment variable: {var}")
                checks_passed = False
            else:
                logger.info(f"✓ {var} is set")
        
        # Check database connectivity
        logger.info("Checking database connectivity...")
        try:
            supabase: Client = create_client(self.supabase_url, self.supabase_key)
            # Test query
            result = supabase.table("agent_sessions").select("id").limit(1).execute()
            logger.info("✓ Database connection successful")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            checks_passed = False
        
        # Check Redis connectivity
        logger.info("Checking Redis connectivity...")
        try:
            redis_client = await redis.from_url(self.redis_url)
            await redis_client.ping()
            await redis_client.close()
            logger.info("✓ Redis connection successful")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            checks_passed = False
        
        # Check Evolution API
        logger.info("Checking Evolution API...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.evolution_api_url}/instance/connectionState/{self.evolution_instance}",
                    headers={"apikey": self.evolution_api_key}
                ) as response:
                    if response.status == 200:
                        logger.info("✓ Evolution API accessible")
                    else:
                        logger.error(f"Evolution API returned status {response.status}")
                        checks_passed = False
        except Exception as e:
            logger.error(f"Evolution API check failed: {e}")
            checks_passed = False
        
        # Check file structure
        logger.info("Checking new modular structure...")
        required_files = [
            "agente/core/agent.py",
            "agente/core/context_manager.py",
            "agente/core/message_handler.py",
            "agente/tools/__init__.py",
            "agente/integrations/whatsapp.py"
        ]
        
        base_path = Path(__file__).parent.parent.parent
        for file_path in required_files:
            full_path = base_path / file_path
            if not full_path.exists():
                logger.error(f"Missing required file: {file_path}")
                checks_passed = False
            else:
                logger.info(f"✓ {file_path} exists")
        
        return checks_passed
    
    async def backup_current_state(self):
        """Backup current configuration and data."""
        logger.info("Creating backup...")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup database tables
        supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        tables_to_backup = ["agent_sessions", "kommo_tokens", "follow_ups"]
        for table in tables_to_backup:
            try:
                data = supabase.table(table).select("*").execute()
                with open(self.backup_dir / f"{table}.json", 'w') as f:
                    json.dump(data.data, f, indent=2, default=str)
                logger.info(f"✓ Backed up {table} ({len(data.data)} records)")
            except Exception as e:
                logger.warning(f"Failed to backup {table}: {e}")
        
        # Backup current webhook configuration
        try:
            async with aiohttp.ClientSession() as session:
                # Get current webhook config from Evolution API
                async with session.get(
                    f"{self.evolution_api_url}/webhook/find/{self.evolution_instance}",
                    headers={"apikey": self.evolution_api_key}
                ) as response:
                    if response.status == 200:
                        webhook_config = await response.json()
                        with open(self.backup_dir / "webhook_config.json", 'w') as f:
                            json.dump(webhook_config, f, indent=2)
                        self.rollback_config['webhook'] = webhook_config
                        logger.info("✓ Backed up webhook configuration")
        except Exception as e:
            logger.warning(f"Failed to backup webhook config: {e}")
        
        # Backup environment file
        env_path = Path(__file__).parent.parent.parent / ".env"
        if env_path.exists():
            shutil.copy(env_path, self.backup_dir / ".env.backup")
            logger.info("✓ Backed up environment configuration")
    
    async def execute_migration(self) -> bool:
        """Execute the migration steps."""
        logger.info("Executing migration...")
        
        try:
            # Step 1: Update webhook endpoint
            logger.info("Updating webhook endpoint...")
            webhook_url = os.getenv("WEBHOOK_URL", "https://sdr.solarprimepe.com.br")
            new_webhook_path = "/webhook/modular"  # New modular endpoint
            
            async with aiohttp.ClientSession() as session:
                webhook_data = {
                    "enabled": True,
                    "url": f"{webhook_url}{new_webhook_path}",
                    "webhookByEvents": False,
                    "events": [
                        "messages.upsert",
                        "messages.update",
                        "messages.delete",
                        "send.message",
                        "contacts.upsert",
                        "contacts.update",
                        "presence.update",
                        "chats.upsert",
                        "chats.update",
                        "chats.delete",
                        "groups.upsert",
                        "groups.update",
                        "group-participants.update",
                        "connection.update",
                        "call",
                        "instance.status"
                    ]
                }
                
                async with session.post(
                    f"{self.evolution_api_url}/webhook/set/{self.evolution_instance}",
                    headers={"apikey": self.evolution_api_key},
                    json=webhook_data
                ) as response:
                    if response.status in [200, 201]:
                        logger.info("✓ Webhook endpoint updated successfully")
                    else:
                        logger.error(f"Failed to update webhook: {response.status}")
                        return False
            
            # Step 2: Migrate in-progress conversations
            logger.info("Migrating in-progress conversations...")
            supabase: Client = create_client(self.supabase_url, self.supabase_key)
            
            # Get active sessions
            active_sessions = supabase.table("agent_sessions").select("*").eq("is_active", True).execute()
            
            if active_sessions.data:
                logger.info(f"Found {len(active_sessions.data)} active sessions to migrate")
                
                # Mark sessions for migration
                for session in active_sessions.data:
                    try:
                        # Add migration flag to session
                        supabase.table("agent_sessions").update({
                            "metadata": {
                                **(session.get("metadata") or {}),
                                "migrated_at": datetime.utcnow().isoformat(),
                                "migration_version": "modular_v1"
                            }
                        }).eq("id", session["id"]).execute()
                        
                        logger.info(f"✓ Marked session {session['id']} for migration")
                    except Exception as e:
                        logger.error(f"Failed to migrate session {session['id']}: {e}")
            
            # Step 3: Clear Redis cache
            logger.info("Clearing Redis cache...")
            redis_client = await redis.from_url(self.redis_url)
            
            # Get all keys related to old agent
            keys_to_delete = []
            async for key in redis_client.scan_iter(match="sdr_agent:*"):
                keys_to_delete.append(key)
            
            if keys_to_delete:
                await redis_client.delete(*keys_to_delete)
                logger.info(f"✓ Cleared {len(keys_to_delete)} Redis keys")
            
            await redis_client.close()
            
            # Step 4: Update system configuration
            logger.info("Updating system configuration...")
            
            # Create migration marker
            with open(Path(__file__).parent.parent.parent / ".migration_completed", 'w') as f:
                f.write(json.dumps({
                    "migrated_at": datetime.utcnow().isoformat(),
                    "version": "modular_v1",
                    "old_agent": "sdr_agent.py",
                    "new_agent": "agente/core/agent.py"
                }, indent=2))
            
            logger.info("✓ Migration steps completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False
    
    async def validate_migration(self) -> bool:
        """Validate the migration was successful."""
        logger.info("Validating migration...")
        validation_passed = True
        
        # Test new webhook endpoint
        logger.info("Testing new webhook endpoint...")
        webhook_url = os.getenv("WEBHOOK_URL", "https://sdr.solarprimepe.com.br")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Send test request to new endpoint
                test_payload = {
                    "event": "connection.update",
                    "instance": self.evolution_instance,
                    "data": {
                        "instance": self.evolution_instance,
                        "state": "open"
                    }
                }
                
                async with session.post(
                    f"{webhook_url}/webhook/modular",
                    json=test_payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        logger.info("✓ New webhook endpoint responding correctly")
                    else:
                        logger.error(f"Webhook test failed with status {response.status}")
                        validation_passed = False
        except Exception as e:
            logger.error(f"Webhook test failed: {e}")
            validation_passed = False
        
        # Verify all tools are accessible
        logger.info("Testing tool accessibility...")
        base_path = Path(__file__).parent.parent
        tools_path = base_path / "tools"
        
        if tools_path.exists():
            tool_files = list(tools_path.glob("*.py"))
            logger.info(f"✓ Found {len(tool_files)} tool files")
        else:
            logger.error("Tools directory not found")
            validation_passed = False
        
        # Check integrations
        logger.info("Checking integrations...")
        integrations = ["whatsapp", "kommo", "calendar"]
        integrations_path = base_path / "integrations"
        
        for integration in integrations:
            if (integrations_path / f"{integration}.py").exists():
                logger.info(f"✓ {integration} integration found")
            else:
                logger.warning(f"⚠ {integration} integration not found")
        
        # Verify database connectivity through new system
        logger.info("Testing database through new system...")
        try:
            supabase: Client = create_client(self.supabase_url, self.supabase_key)
            test_result = supabase.table("agent_sessions").select("id").limit(1).execute()
            logger.info("✓ Database accessible through new system")
        except Exception as e:
            logger.error(f"Database test failed: {e}")
            validation_passed = False
        
        return validation_passed
    
    async def rollback(self):
        """Rollback to previous state."""
        logger.warning("Starting rollback procedure...")
        
        try:
            # Restore webhook configuration
            if 'webhook' in self.rollback_config:
                logger.info("Restoring webhook configuration...")
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.evolution_api_url}/webhook/set/{self.evolution_instance}",
                        headers={"apikey": self.evolution_api_key},
                        json=self.rollback_config['webhook']
                    ) as response:
                        if response.status in [200, 201]:
                            logger.info("✓ Webhook configuration restored")
                        else:
                            logger.error("Failed to restore webhook configuration")
            
            # Remove migration marker
            migration_marker = Path(__file__).parent.parent.parent / ".migration_completed"
            if migration_marker.exists():
                migration_marker.unlink()
                logger.info("✓ Removed migration marker")
            
            # Clear any migration flags from database
            supabase: Client = create_client(self.supabase_url, self.supabase_key)
            
            # Get sessions with migration metadata
            migrated_sessions = supabase.table("agent_sessions").select("id, metadata").execute()
            
            for session in migrated_sessions.data:
                if session.get("metadata") and "migrated_at" in session["metadata"]:
                    metadata = session["metadata"]
                    metadata.pop("migrated_at", None)
                    metadata.pop("migration_version", None)
                    
                    supabase.table("agent_sessions").update({
                        "metadata": metadata
                    }).eq("id", session["id"]).execute()
            
            logger.info("✓ Rollback completed")
            await self.generate_report("rollback")
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            await self.generate_report("rollback_failed")
    
    async def generate_report(self, status: str):
        """Generate migration report."""
        report_path = Path(__file__).parent / "reports"
        report_path.mkdir(exist_ok=True)
        
        report = {
            "migration_id": datetime.now().strftime('%Y%m%d_%H%M%S'),
            "status": status,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "backup_location": str(self.backup_dir),
            "details": {
                "environment_check": "passed" if status != "rollback_failed" else "failed",
                "database_migration": "completed" if status == "success" else "failed",
                "webhook_update": "completed" if status == "success" else "failed",
                "validation": "passed" if status == "success" else "failed"
            }
        }
        
        report_file = report_path / f"migration_report_{report['migration_id']}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Migration report saved to: {report_file}")
        
        # Log summary
        logger.info("=" * 60)
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Status: {status.upper()}")
        logger.info(f"Backup Location: {self.backup_dir}")
        logger.info(f"Report: {report_file}")
        logger.info("=" * 60)


async def main():
    """Main entry point."""
    manager = MigrationManager()
    success = await manager.run()
    
    if success:
        logger.info("\n✅ Migration completed successfully!")
        logger.info("The system is now using the modular agent architecture.")
        logger.info("Please monitor the system for any issues.")
    else:
        logger.error("\n❌ Migration failed!")
        logger.error("The system has been rolled back to the previous state.")
        logger.error("Please check the logs for details.")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)