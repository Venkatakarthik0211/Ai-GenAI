#!/usr/bin/env node

/**
 * Claude Agent Manager - Main Entry Point
 * Production-level agent orchestration for automated code generation
 */

import { config as loadEnv } from 'dotenv';
import path from 'path';
import { Logger } from './utils/logger.js';
import { BedrockAuth } from './managers/BedrockAuth.js';
import { StateManager } from './managers/StateManager.js';
import { AgentManager } from './managers/AgentManager.js';
import type { ExecutionContext, BedrockConfig, LoggerConfig } from './types.js';

// Load environment variables
loadEnv();

/**
 * Parse command line arguments and environment variables
 */
function parseExecutionContext(): ExecutionContext {
  const workspaceDir = process.env.WORKSPACE_DIR || process.cwd();
  const outputDir = process.env.OUTPUT_DIR || path.join(workspaceDir, '.agents');
  const promptFile = process.env.PROMPT_FILE;
  const promptText = process.env.CLAUDE_PROMPT;
  const resumeAgentId = process.env.RESUME_AGENT_ID;

  const bedrockConfig: BedrockConfig = {
    region: process.env.AWS_REGION || 'us-east-1',
    profile: process.env.AWS_PROFILE || 'default',
    modelId: process.env.ANTHROPIC_MODEL || 'us.anthropic.claude-sonnet-4-5-20250929-v1:0',
    maxTokens: parseInt(process.env.MAX_TOKENS || '8192', 10),
  };

  return {
    workspaceDir,
    outputDir,
    promptFile,
    promptText,
    resumeAgentId,
    bedrockConfig,
  };
}

/**
 * Initialize logger
 */
function initializeLogger(outputDir: string): Logger {
  const loggerConfig: LoggerConfig = {
    level: (process.env.LOG_LEVEL as any) || 'info',
    outputFile: path.join(outputDir, 'agent-manager.log'),
    console: true,
  };

  return new Logger(loggerConfig);
}

/**
 * Main execution function
 */
async function main(): Promise<void> {
  const context = parseExecutionContext();
  const logger = initializeLogger(context.outputDir);

  try {
    logger.info('='.repeat(80));
    logger.info('Claude Agent Manager - Production Mode');
    logger.info('='.repeat(80));

    logger.info('Execution context', {
      workspace: context.workspaceDir,
      output: context.outputDir,
      region: context.bedrockConfig.region,
      model: context.bedrockConfig.modelId,
      resume: context.resumeAgentId || 'none',
    });

    // Step 1: Initialize Bedrock Authentication
    logger.info('Step 1/5: Initializing AWS Bedrock authentication...');
    const bedrockAuth = new BedrockAuth(context.bedrockConfig, logger);

    const credentialsValid = await bedrockAuth.verifyCredentials();
    if (!credentialsValid) {
      throw new Error('AWS credentials verification failed');
    }

    // Step 2: Initialize State Manager
    logger.info('Step 2/5: Initializing state manager...');
    const stateManager = new StateManager(context.outputDir, logger);
    await stateManager.initialize();

    // Step 3: Initialize Agent Manager
    logger.info('Step 3/5: Initializing agent manager...');
    const agentManager = new AgentManager(context, logger, stateManager, bedrockAuth);
    await agentManager.initialize();

    // Step 4: Determine execution mode
    logger.info('Step 4/5: Determining execution mode...');

    let executionMode: 'resume' | 'prompt-file' | 'prompt-text' | 'discover-all' = 'discover-all';
    let prompt: string | undefined;

    if (context.resumeAgentId) {
      executionMode = 'resume';
      logger.info('Mode: Resume existing agent', { agentId: context.resumeAgentId });
    } else if (context.promptFile) {
      executionMode = 'prompt-file';
      const { readFile } = await import('fs/promises');
      const promptPath = path.isAbsolute(context.promptFile)
        ? context.promptFile
        : path.join(context.workspaceDir, context.promptFile);
      prompt = await readFile(promptPath, 'utf-8');
      logger.info('Mode: Execute from prompt file', { file: promptPath });
    } else if (context.promptText) {
      executionMode = 'prompt-text';
      prompt = context.promptText;
      logger.info('Mode: Execute from prompt text');
    } else {
      executionMode = 'discover-all';
      logger.info('Mode: Discover and process all PROMPT.md files');
    }

    // Step 5: Execute
    logger.info('Step 5/5: Executing agent...');

    if (executionMode === 'discover-all') {
      // Discover and process all PROMPT.md files
      const results = await agentManager.processAllPromptFiles();

      logger.info('='.repeat(80));
      logger.success('Batch processing completed', {
        totalFiles: results.length,
        successful: results.filter(r => r.success).length,
        failed: results.filter(r => !r.success).length,
      });

      // Print summary
      for (const result of results) {
        if (result.success) {
          logger.success(`✓ Agent ${result.agentName} completed`, {
            agentId: result.agentId,
            filesGenerated: result.filesGenerated.length,
            tokens: result.tokenUsage
              ? `${result.tokenUsage.input} in / ${result.tokenUsage.output} out`
              : 'unknown',
          });
        } else {
          logger.error(`✗ Agent ${result.agentName} failed`, {
            agentId: result.agentId,
            errors: result.errors,
          });
        }
      }
    } else {
      // Execute single agent
      const result = await agentManager.executeAgent(
        prompt!,
        executionMode === 'resume' ? context.resumeAgentId : undefined
      );

      logger.info('='.repeat(80));
      if (result.success) {
        logger.success('Agent execution completed successfully', {
          agentId: result.agentId,
          agentName: result.agentName,
          filesGenerated: result.filesGenerated.length,
          duration: `${(result.duration / 1000).toFixed(2)}s`,
          tokens: result.tokenUsage
            ? `${result.tokenUsage.input} in / ${result.tokenUsage.output} out`
            : 'unknown',
        });

        logger.info('To resume this agent, use:', {
          command: `RESUME_AGENT_ID=${result.agentId} docker-compose up`,
        });
      } else {
        logger.error('Agent execution failed', {
          agentId: result.agentId,
          errors: result.errors,
        });
        process.exit(1);
      }
    }

    logger.info('='.repeat(80));
    logger.success('Claude Agent Manager finished successfully');
    logger.info('='.repeat(80));
  } catch (error) {
    logger.error('Fatal error in Agent Manager', error);
    logger.info('='.repeat(80));
    process.exit(1);
  }
}

// Execute main function
main().catch(error => {
  console.error('Unhandled error:', error);
  process.exit(1);
});
