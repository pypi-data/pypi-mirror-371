"""
Simplified File Executor for GitLlama
Executes the planned file operations
"""

import logging
from pathlib import Path
from typing import Dict, List
from ..ai import OllamaClient, AIQuery

logger = logging.getLogger(__name__)


class TodoExecutor:
    """Executes planned file operations"""
    
    def __init__(self, client: OllamaClient, model: str = "gemma3:4b"):
        self.client = client
        self.model = model
        self.ai = AIQuery(client, model)
    
    def execute_plan(self, repo_path: Path, action_plan: Dict) -> List[str]:
        """Execute the action plan"""
        logger.info(f"Executing plan with {len(action_plan['files_to_modify'])} files")
        
        modified_files = []
        
        for file_info in action_plan['files_to_modify']:
            file_path = repo_path / file_info['path']
            operation = file_info['operation']
            
            logger.info(f"Executing {operation} on {file_info['path']}")
            
            if operation == 'EDIT':
                # Check if file exists to provide context to AI
                original_content = ""
                if file_path.exists():
                    original_content = file_path.read_text()
                
                content = self._edit_file_content(
                    file_info['path'],
                    original_content,
                    action_plan['plan'],
                    action_plan['todo_excerpt']
                )
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)
                modified_files.append(file_info['path'])
                
            elif operation == 'DELETE':
                if file_path.exists():
                    file_path.unlink()
                    modified_files.append(file_info['path'])
                else:
                    logger.warning(f"File to delete doesn't exist: {file_info['path']}")
        
        return modified_files
    
    def _edit_file_content(self, file_path: str, original_content: str, plan: str, todo: str) -> str:
        """Edit file content (create new or completely rewrite existing)"""
        if original_content:
            # File exists - edit it
            prompt = f"""Completely edit this file according to the plan: {file_path}

Current content (for reference):
{original_content[:2000]}

Plan excerpt:
{plan[:1000]}

TODO excerpt:
{todo[:500]}

Generate the COMPLETE new file content. Do not modify - completely rewrite.
Wrap in appropriate markdown code blocks."""
            context_name = "file_edit"
        else:
            # File doesn't exist - create new
            prompt = f"""Create complete content for this new file: {file_path}

Based on this plan:
{plan[:1000]}

To help implement this TODO:
{todo[:500]}

Generate professional, working code with comments.
Wrap the content in appropriate markdown code blocks."""
            context_name = "file_creation"
        
        result = self.ai.file_write(
            requirements=prompt,
            context="",
            context_name=context_name
        )
        
        # The file_write query already cleans the content
        return result.content