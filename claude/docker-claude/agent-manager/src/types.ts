/**
 * Production-level type definitions for Claude Agent Manager
 */

export interface AgentConfig {
  name: string;
  description: string;
  tools: string[];
  model: 'claude-3-5-sonnet-20241022' | 'claude-3-opus-20240229' | 'claude-3-haiku-20240307';
  systemPrompt: string;
  maxTokens?: number;
  temperature?: number;
}

export interface AgentSession {
  agentId: string;
  agentName: string;
  startedAt: Date;
  lastActivityAt: Date;
  status: 'active' | 'completed' | 'failed' | 'paused';
  prompt: string;
  conversationHistory: ConversationMessage[];
  metadata: Record<string, unknown>;
}

export interface ConversationMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface AgentState {
  currentSession: AgentSession | null;
  previousSessions: AgentSession[];
  processedFiles: string[];
  pendingFiles: string[];
  lastSavedAt: Date;
}

export interface BedrockConfig {
  region: string;
  profile: string;
  modelId: string;
  maxTokens: number;
}

export interface ExecutionContext {
  workspaceDir: string;
  outputDir: string;
  promptFile?: string;
  promptText?: string;
  resumeAgentId?: string;
  bedrockConfig: BedrockConfig;
}

export interface AgentExecutionResult {
  success: boolean;
  agentId: string;
  agentName: string;
  filesGenerated: string[];
  errors: string[];
  duration: number;
  tokenUsage?: {
    input: number;
    output: number;
  };
}

export interface PromptDiscoveryResult {
  totalFound: number;
  files: Array<{
    path: string;
    directory: string;
    processed: boolean;
  }>;
}

export type LogLevel = 'info' | 'warn' | 'error' | 'debug';

export interface LoggerConfig {
  level: LogLevel;
  outputFile?: string;
  console: boolean;
}
