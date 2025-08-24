#!/usr/bin/env python3
"""
Pre-commit Hook for DataExploratoryProject

This hook automatically runs the auto-discovery system when new components
are added to ensure benchmarking and example scripts stay up-to-date.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PreCommitHook:
    """Pre-commit hook for automatic component discovery and script updates."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.auto_discovery_script = self.project_root / "auto_discovery_system.py"
        
    def get_staged_files(self) -> Set[str]:
        """Get list of staged files from git."""
        try:
            result = subprocess.run(
                ['git', 'diff', '--cached', '--name-only'],
                capture_output=True, text=True, cwd=self.project_root
            )
            if result.returncode == 0:
                return set(result.stdout.strip().split('\n') if result.stdout.strip() else [])
            else:
                logger.warning("Failed to get staged files from git")
                return set()
        except Exception as e:
            logger.warning(f"Error getting staged files: {e}")
            return set()
    
    def is_component_file(self, file_path: str) -> bool:
        """Check if a file is a component file that should trigger auto-discovery."""
        component_patterns = [
            # Data model files
            'models/data_models/',
            '*_model.py',
            
            # Estimator files
            'analysis/',
            '*_estimator.py',
            
            # Neural component files
            'models/data_models/neural_fsde/',
            'models/neural/',
            
            # High-performance files
            'analysis/high_performance/',
            
            # Test files
            'tests/',
            'test_*.py'
        ]
        
        file_path_lower = file_path.lower()
        
        for pattern in component_patterns:
            if pattern.endswith('/'):
                if pattern in file_path_lower:
                    return True
            elif pattern.startswith('*'):
                if file_path_lower.endswith(pattern[1:]):
                    return True
            else:
                if pattern in file_path_lower:
                    return True
        
        return False
    
    def should_run_discovery(self, staged_files: Set[str]) -> bool:
        """Determine if auto-discovery should be run based on staged files."""
        if not staged_files:
            return False
        
        # Check if any staged files are component files
        component_files = [f for f in staged_files if self.is_component_file(f)]
        
        if component_files:
            logger.info(f"Found {len(component_files)} component files in staged changes:")
            for file in component_files:
                logger.info(f"  - {file}")
            return True
        
        return False
    
    def run_auto_discovery(self) -> bool:
        """Run the auto-discovery system."""
        if not self.auto_discovery_script.exists():
            logger.error(f"Auto-discovery script not found: {self.auto_discovery_script}")
            return False
        
        try:
            logger.info("Running auto-discovery system...")
            
            result = subprocess.run(
                [sys.executable, str(self.auto_discovery_script)],
                capture_output=True, text=True, cwd=self.project_root
            )
            
            if result.returncode == 0:
                logger.info("Auto-discovery completed successfully")
                if result.stdout:
                    logger.info("Output:")
                    for line in result.stdout.strip().split('\n'):
                        logger.info(f"  {line}")
                return True
            else:
                logger.error("Auto-discovery failed")
                if result.stderr:
                    logger.error("Error output:")
                    for line in result.stderr.strip().split('\n'):
                        logger.error(f"  {line}")
                return False
                
        except Exception as e:
            logger.error(f"Error running auto-discovery: {e}")
            return False
    
    def stage_updated_files(self) -> bool:
        """Stage any files that were updated by the auto-discovery system."""
        try:
            # Check for updated files
            result = subprocess.run(
                ['git', 'diff', '--name-only'],
                capture_output=True, text=True, cwd=self.project_root
            )
            
            if result.returncode == 0 and result.stdout.strip():
                updated_files = result.stdout.strip().split('\n')
                logger.info(f"Found {len(updated_files)} updated files:")
                
                for file in updated_files:
                    logger.info(f"  - {file}")
                
                # Stage the updated files
                result = subprocess.run(
                    ['git', 'add'] + updated_files,
                    capture_output=True, text=True, cwd=self.project_root
                )
                
                if result.returncode == 0:
                    logger.info("Updated files staged successfully")
                    return True
                else:
                    logger.error("Failed to stage updated files")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error staging updated files: {e}")
            return False
    
    def run(self) -> int:
        """Run the pre-commit hook."""
        logger.info("Running pre-commit hook...")
        
        # Get staged files
        staged_files = self.get_staged_files()
        
        # Check if auto-discovery should be run
        if not self.should_run_discovery(staged_files):
            logger.info("No component files detected, skipping auto-discovery")
            return 0
        
        # Run auto-discovery
        if not self.run_auto_discovery():
            logger.error("Auto-discovery failed, commit aborted")
            return 1
        
        # Stage any updated files
        if not self.stage_updated_files():
            logger.error("Failed to stage updated files, commit aborted")
            return 1
        
        logger.info("Pre-commit hook completed successfully")
        return 0

def main():
    """Main function for the pre-commit hook."""
    hook = PreCommitHook()
    exit_code = hook.run()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

