#!/usr/bin/env python3
"""
AI Reasoning Module using OpenRouter API
Replaces Claude Code reasoning functionality with OpenRouter integration
"""
import time
import logging
from pathlib import Path
import os
import json
from typing import List, Dict, Any, Optional
from .openrouter_config import OpenRouterAPI, chat_with_openrouter, CLAUDE_MODELS, OPENAI_MODELS


class OpenRouterReasoning:
    def __init__(self, vault_path: str, model: str = "anthropic/claude-3.5-sonnet"):
        """
        Initialize OpenRouter reasoning module
        """
        self.vault_path = Path(vault_path)
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # File handler for logging
        log_file_path = self.vault_path / 'openrouter_reasoning.log'
        handler = logging.FileHandler(log_file_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Initialize OpenRouter API
        try:
            self.openrouter = OpenRouterAPI()
            self.logger.info(f"OpenRouter API initialized with model: {model}")
        except ValueError as e:
            self.logger.error(f"Failed to initialize OpenRouter API: {e}")
            raise

    def analyze_task(self, task_description: str, context: str = "", company_handbook: str = "") -> Dict[str, Any]:
        """
        Analyze a task using OpenRouter API
        """
        system_message = f"""You are an AI employee tasked with analyzing work tasks.
Your role is to understand the task, analyze requirements, and create implementation plans.
Always follow the company guidelines and best practices.

Company Handbook:
{company_handbook}"""

        prompt = f"""Analyze the following task and provide a structured analysis:

Task: {task_description}

Context: {context}

Please provide:
1. Task understanding
2. Required steps
3. Potential challenges
4. Expected outcomes
5. Any approval requirements"""

        try:
            # Use the OpenRouterAPI directly with lower token count
            response = self.openrouter.chat_completion(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=300  # Lower token count to avoid credit issues
            )

            response_text = response["choices"][0]["message"]["content"]

            # Parse the response into structured data
            analysis = {
                "task_description": task_description,
                "context": context,
                "analysis": response,
                "timestamp": time.time(),
                "model_used": self.model
            }

            self.logger.info(f"Task analysis completed for: {task_description[:50]}...")
            return analysis

        except Exception as e:
            self.logger.error(f"Error in task analysis: {e}")
            return {
                "task_description": task_description,
                "context": context,
                "analysis": f"Error occurred during analysis: {str(e)}",
                "timestamp": time.time(),
                "model_used": self.model,
                "error": str(e)
            }

    def create_plan(self, task_description: str, analysis: Dict[str, Any], company_handbook: str = "") -> Dict[str, Any]:
        """
        Create a detailed plan based on task analysis
        """
        system_message = f"""You are an AI employee creating detailed implementation plans.
Create a comprehensive, step-by-step plan based on the task and analysis.
Always follow the company guidelines and best practices.

Company Handbook:
{company_handbook}"""

        prompt = f"""Create a detailed implementation plan for the following task:

Task: {task_description}

Analysis: {analysis.get('analysis', '')}

Please create a structured plan with:
1. Clear objectives
2. Step-by-step implementation
3. Resource requirements
4. Timeline estimates
5. Success criteria
6. Potential risks and mitigations
7. Approval requirements"""

        try:
            response = self.openrouter.chat_completion(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=400  # Lower token count to avoid credit issues
            )

            response_text = response["choices"][0]["message"]["content"]
            plan = {
                "task_description": task_description,
                "analysis": analysis,
                "plan": response_text,
                "status": "created",
                "timestamp": time.time(),
                "model_used": self.model
            }

            self.logger.info(f"Plan created for: {task_description[:50]}...")
            return plan

        except Exception as e:
            self.logger.error(f"Error in plan creation: {e}")
            return {
                "task_description": task_description,
                "analysis": analysis,
                "plan": f"Error occurred during plan creation: {str(e)}",
                "status": "error",
                "timestamp": time.time(),
                "model_used": self.model,
                "error": str(e)
            }

    def execute_task(self, plan: Dict[str, Any], company_handbook: str = "") -> Dict[str, Any]:
        """
        Execute a task based on the plan using OpenRouter API
        """
        system_message = f"""You are an AI employee executing tasks based on the provided plan.
Follow the plan steps precisely and report on progress.
Always follow the company guidelines and best practices.

Company Handbook:
{company_handbook}"""

        task_description = plan.get("task_description", "")
        plan_content = plan.get("plan", "")

        prompt = f"""Execute the following task based on the plan:

Task: {task_description}

Plan: {plan_content}

Please:
1. Follow the plan step by step
2. Report on execution progress
3. Note any deviations from the plan
4. Identify completed steps
5. Highlight any issues encountered
6. Provide final status"""

        try:
            response = self.openrouter.chat_completion(
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=400  # Lower token count to avoid credit issues
            )

            response_text = response["choices"][0]["message"]["content"]
            execution = {
                "task_description": task_description,
                "plan": plan,
                "execution_output": response_text,
                "status": "executed",
                "timestamp": time.time(),
                "model_used": self.model
            }

            self.logger.info(f"Task execution completed for: {task_description[:50]}...")
            return execution

        except Exception as e:
            self.logger.error(f"Error in task execution: {e}")
            return {
                "task_description": task_description,
                "plan": plan,
                "execution_output": f"Error occurred during execution: {str(e)}",
                "status": "error",
                "timestamp": time.time(),
                "model_used": self.model,
                "error": str(e)
            }

    def process_file_with_ai(self, file_path: Path, company_handbook: str = "") -> Dict[str, Any]:
        """
        Process a file using AI reasoning with OpenRouter
        """
        try:
            # Read the file content
            content = file_path.read_text()

            # Analyze the task
            analysis = self.analyze_task(
                task_description=content[:500],  # First 500 chars as description
                context=content,
                company_handbook=company_handbook
            )

            # Create a plan based on analysis
            plan = self.create_plan(
                task_description=content[:500],
                analysis=analysis,
                company_handbook=company_handbook
            )

            # Execute based on the plan
            execution = self.execute_task(
                plan=plan,
                company_handbook=company_handbook
            )

            result = {
                "file_path": str(file_path),
                "original_content": content,
                "analysis": analysis,
                "plan": plan,
                "execution": execution,
                "completed_at": time.time()
            }

            self.logger.info(f"File processing completed: {file_path.name}")
            return result

        except Exception as e:
            self.logger.error(f"Error processing file {file_path}: {e}")
            return {
                "file_path": str(file_path),
                "error": str(e),
                "completed_at": time.time()
            }

    def get_company_handbook(self) -> str:
        """
        Read the company handbook from the vault
        """
        handbook_path = self.vault_path / 'Company_Handbook.md'
        if handbook_path.exists():
            return handbook_path.read_text()
        return "No company handbook found. Follow standard business practices."

    def get_available_models(self) -> List[str]:
        """
        Get a list of available models
        """
        try:
            models_data = self.openrouter.list_models()
            models = models_data.get("data", [])
            return [model.get("id", "") for model in models if model.get("id")]
        except Exception as e:
            self.logger.error(f"Error getting available models: {e}")
            return [self.model]  # Return current model as fallback