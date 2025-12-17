/**
 * Agent Manager - Core orchestration for Claude Agent execution
 * Handles agent lifecycle, conversation management, and code generation
 */

import Anthropic from '@anthropic-ai/sdk';
import { glob } from 'glob';
import { readFile } from 'fs/promises';
import path from 'path';
import type {
  AgentConfig,
  AgentSession,
  ExecutionContext,
  AgentExecutionResult,
  PromptDiscoveryResult,
} from '../types.js';
import type { Logger } from '../utils/logger.js';
import type { StateManager } from './StateManager.js';
import type { BedrockAuth } from './BedrockAuth.js';

export class AgentManager {
  private client: Anthropic;
  private context: ExecutionContext;
  private logger: Logger;
  private stateManager: StateManager;
  private bedrockAuth: BedrockAuth;
  private agentRegistry: Map<string, AgentConfig>;

  constructor(
    context: ExecutionContext,
    logger: Logger,
    stateManager: StateManager,
    bedrockAuth: BedrockAuth
  ) {
    this.context = context;
    this.logger = logger;
    this.stateManager = stateManager;
    this.bedrockAuth = bedrockAuth;
    this.agentRegistry = new Map();

    // Will be initialized in initialize()
    this.client = null as any;
  }

  /**
   * Initialize agent manager with Anthropic client
   */
  async initialize(): Promise<void> {
    try {
      this.logger.info('Initializing Agent Manager...');

      // Get Anthropic configuration from Bedrock auth
      const config = await this.bedrockAuth.getAnthropicConfig();

      // Initialize Anthropic SDK client
      this.client = new Anthropic({
        apiKey: config.apiKey,
        baseURL: config.baseURL,
      });

      // Register available agents
      this.registerAgents();

      this.logger.success('Agent Manager initialized', {
        registeredAgents: Array.from(this.agentRegistry.keys()),
      });
    } catch (error) {
      this.logger.error('Failed to initialize Agent Manager', error);
      throw error;
    }
  }

  /**
   * Register available agent configurations
   */
  private registerAgents(): void {
    // Code Generator Agent
    this.agentRegistry.set('code-generator', {
      name: 'code-generator',
      description: 'Automated code generation specialist for PROMPT.md files',
      tools: ['Read', 'Write', 'Glob', 'Grep', 'Bash', 'TodoWrite'],
      model: 'claude-3-5-sonnet-20241022',
      systemPrompt: `You are an automated code generation specialist. Your role is to:

1. Discover PROMPT.md files in the project directory structure
2. Read and understand requirements in each PROMPT.md
3. Generate complete, production-ready code implementations
4. Place generated files in the same directory as the PROMPT.md
5. Follow best practices and coding standards
6. Generate all necessary files (code, configs, tests, documentation)

Work autonomously and methodically. For each PROMPT.md:
- Read the requirements carefully
- Plan the implementation
- Generate all necessary files
- Ensure code quality and completeness

Do not ask for user input - make reasonable decisions based on context.`,
      maxTokens: this.context.bedrockConfig.maxTokens,
      temperature: 0.7,
    });

    // General Purpose Agent
    this.agentRegistry.set('general-purpose', {
      name: 'general-purpose',
      description: 'General purpose agent for various automation tasks',
      tools: ['Read', 'Write', 'Glob', 'Grep', 'Bash'],
      model: 'claude-3-5-sonnet-20241022',
      systemPrompt: `You are a general-purpose automation assistant. Execute tasks autonomously:

- Understand the user's request
- Plan and execute necessary steps
- Generate required outputs
- Handle errors gracefully
- Work without user intervention

Make reasonable assumptions when needed and focus on completing the task efficiently.`,
      maxTokens: this.context.bedrockConfig.maxTokens,
      temperature: 0.7,
    });

    this.logger.debug('Registered agents', {
      agents: Array.from(this.agentRegistry.keys()),
    });
  }

  /**
   * Discover PROMPT.md files in workspace
   */
  async discoverPromptFiles(): Promise<PromptDiscoveryResult> {
    try {
      this.logger.info('Discovering PROMPT.md files...', {
        workspace: this.context.workspaceDir,
      });

      const pattern = path.join(this.context.workspaceDir, '**/PROMPT.md');
      const files = await glob(pattern, {
        ignore: ['**/node_modules/**', '**/dist/**', '**/.git/**'],
      });

      const result: PromptDiscoveryResult = {
        totalFound: files.length,
        files: files.map(filePath => ({
          path: filePath,
          directory: path.dirname(filePath),
          processed: this.stateManager.isFileProcessed(filePath),
        })),
      };

      this.logger.success('PROMPT.md discovery complete', {
        total: result.totalFound,
        processed: result.files.filter(f => f.processed).length,
        pending: result.files.filter(f => !f.processed).length,
      });

      return result;
    } catch (error) {
      this.logger.error('Failed to discover PROMPT.md files', error);
      throw error;
    }
  }

  /**
   * Select appropriate agent based on prompt content
   */
  private selectAgent(prompt: string): AgentConfig {
    // Simple agent selection logic - can be enhanced
    const lowerPrompt = prompt.toLowerCase();

    if (
      lowerPrompt.includes('prompt.md') ||
      lowerPrompt.includes('code generation') ||
      lowerPrompt.includes('generate code')
    ) {
      return this.agentRegistry.get('code-generator')!;
    }

    return this.agentRegistry.get('general-purpose')!;
  }

  /**
   * Execute agent with given prompt
   */
  async executeAgent(prompt: string, resumeAgentId?: string): Promise<AgentExecutionResult> {
    const startTime = Date.now();
    let session: AgentSession;
    let agentConfig: AgentConfig;

    try {
      // Check if resuming existing session
      if (resumeAgentId) {
        this.logger.info('Attempting to resume agent session', { agentId: resumeAgentId });

        const existingSession = this.stateManager.getSession(resumeAgentId);
        if (existingSession) {
          session = existingSession;
          agentConfig = this.agentRegistry.get(session.agentName)!;

          this.logger.success('Resuming existing session', {
            agentId: resumeAgentId,
            agentName: session.agentName,
            startedAt: session.startedAt,
          });
        } else {
          this.logger.warn('Agent ID not found, starting new session', {
            agentId: resumeAgentId,
          });
          agentConfig = this.selectAgent(prompt);
          session = this.stateManager.startSession(
            this.generateAgentId(),
            agentConfig.name,
            prompt
          );
        }
      } else {
        // Start new session
        agentConfig = this.selectAgent(prompt);
        session = this.stateManager.startSession(
          this.generateAgentId(),
          agentConfig.name,
          prompt
        );

        this.logger.info('Started new agent session', {
          agentId: session.agentId,
          agentName: agentConfig.name,
        });
      }

      // Execute the agent conversation
      const result = await this.runAgentConversation(session, agentConfig, prompt);

      // Mark session as complete
      this.stateManager.completeSession(result.success);

      return result;
    } catch (error) {
      this.logger.error('Agent execution failed', error);

      if (session!) {
        this.stateManager.completeSession(false);
      }

      throw error;
    } finally {
      const duration = Date.now() - startTime;
      this.logger.info('Agent execution finished', {
        duration: `${(duration / 1000).toFixed(2)}s`,
      });
    }
  }

  /**
   * Run agent conversation using Anthropic SDK
   */
  private async runAgentConversation(
    session: AgentSession,
    agentConfig: AgentConfig,
    prompt: string
  ): Promise<AgentExecutionResult> {
    const result: AgentExecutionResult = {
      success: false,
      agentId: session.agentId,
      agentName: agentConfig.name,
      filesGenerated: [],
      errors: [],
      duration: 0,
      tokenUsage: {
        input: 0,
        output: 0,
      },
    };

    try {
      this.logger.info('Starting agent conversation', {
        agentId: session.agentId,
        model: agentConfig.model,
      });

      // Build conversation history
      const messages: Anthropic.MessageParam[] = [];

      // Add previous conversation history if resuming
      if (session.conversationHistory.length > 0) {
        for (const msg of session.conversationHistory) {
          messages.push({
            role: msg.role as 'user' | 'assistant',
            content: msg.content,
          });
        }
        this.logger.debug('Loaded conversation history', {
          messages: messages.length,
        });
      }

      // Add current prompt
      messages.push({
        role: 'user',
        content: prompt,
      });

      // Execute the conversation
      let continueConversation = true;
      let iterationCount = 0;
      const maxIterations = 50; // Safety limit

      while (continueConversation && iterationCount < maxIterations) {
        iterationCount++;

        this.logger.debug('Agent iteration', { iteration: iterationCount });

        const response = await this.client.messages.create({
          model: agentConfig.model,
          max_tokens: agentConfig.maxTokens || 8192,
          temperature: agentConfig.temperature,
          system: agentConfig.systemPrompt,
          messages,
        });

        // Update token usage
        result.tokenUsage!.input += response.usage.input_tokens;
        result.tokenUsage!.output += response.usage.output_tokens;

        // Process response
        const assistantMessage = response.content
          .filter(block => block.type === 'text')
          .map(block => (block as Anthropic.TextBlock).text)
          .join('\n');

        // Add to conversation history
        messages.push({
          role: 'assistant',
          content: assistantMessage,
        });

        // Save conversation to session
        session.conversationHistory.push({
          role: 'assistant',
          content: assistantMessage,
          timestamp: new Date(),
        });

        this.stateManager.updateSession({
          conversationHistory: session.conversationHistory,
        });

        this.logger.debug('Agent response received', {
          iteration: iterationCount,
          stopReason: response.stop_reason,
          outputTokens: response.usage.output_tokens,
        });

        // Check if agent wants to use tools (in a real implementation, you'd handle tool use)
        const toolUseBlocks = response.content.filter(block => block.type === 'tool_use');

        if (toolUseBlocks.length > 0) {
          this.logger.debug('Agent requested tools', {
            tools: toolUseBlocks.length,
          });
          // In a full implementation, you would:
          // 1. Execute the tools
          // 2. Add tool results to messages
          // 3. Continue conversation
          // For now, we'll just log and continue
        }

        // Determine if conversation should continue
        if (response.stop_reason === 'end_turn' || response.stop_reason === 'max_tokens') {
          continueConversation = false;
        }

        // Check for completion indicators in text
        if (
          assistantMessage.toLowerCase().includes('task completed') ||
          assistantMessage.toLowerCase().includes('all done') ||
          assistantMessage.toLowerCase().includes('finished')
        ) {
          continueConversation = false;
        }
      }

      // Save final transcript
      await this.saveTranscript(session);

      result.success = true;
      result.duration = Date.now() - Date.now(); // Will be set by caller

      this.logger.success('Agent conversation completed', {
        agentId: session.agentId,
        iterations: iterationCount,
        inputTokens: result.tokenUsage!.input,
        outputTokens: result.tokenUsage!.output,
      });

      return result;
    } catch (error) {
      this.logger.error('Agent conversation failed', error);
      result.errors.push(error instanceof Error ? error.message : String(error));
      return result;
    }
  }

  /**
   * Save agent transcript
   */
  private async saveTranscript(session: AgentSession): Promise<void> {
    try {
      const transcript = session.conversationHistory
        .map(msg => JSON.stringify({
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp.toISOString(),
        }))
        .join('\n');

      await this.stateManager.saveTranscript(session.agentId, transcript);

      this.logger.debug('Transcript saved', {
        agentId: session.agentId,
        messages: session.conversationHistory.length,
      });
    } catch (error) {
      this.logger.error('Failed to save transcript', error);
    }
  }

  /**
   * Process all discovered PROMPT.md files
   */
  async processAllPromptFiles(): Promise<AgentExecutionResult[]> {
    const discovery = await this.discoverPromptFiles();
    const results: AgentExecutionResult[] = [];

    for (const promptFile of discovery.files) {
      if (promptFile.processed) {
        this.logger.info('Skipping already processed file', {
          file: promptFile.path,
        });
        continue;
      }

      try {
        this.logger.info('Processing PROMPT.md', {
          file: promptFile.path,
          directory: promptFile.directory,
        });

        // Read the prompt content
        const promptContent = await readFile(promptFile.path, 'utf-8');

        // Execute agent with this prompt
        const result = await this.executeAgent(
          `Process this PROMPT.md file at ${promptFile.path}:\n\n${promptContent}\n\nGenerate all necessary files in the directory: ${promptFile.directory}`
        );

        results.push(result);

        // Mark file as processed
        this.stateManager.markFileProcessed(promptFile.path);

        this.logger.success('PROMPT.md processed successfully', {
          file: promptFile.path,
        });
      } catch (error) {
        this.logger.error('Failed to process PROMPT.md', error, {
          file: promptFile.path,
        });

        results.push({
          success: false,
          agentId: 'unknown',
          agentName: 'code-generator',
          filesGenerated: [],
          errors: [error instanceof Error ? error.message : String(error)],
          duration: 0,
        });
      }
    }

    return results;
  }

  /**
   * Generate unique agent ID
   */
  private generateAgentId(): string {
    return `agent-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
  }

  /**
   * Get last agent ID from state
   */
  getLastAgentId(): string | null {
    return this.stateManager.getLastAgentId();
  }
}
