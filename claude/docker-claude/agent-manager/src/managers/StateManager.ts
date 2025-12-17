/**
 * State Manager - Handles agent state persistence and resumability
 * Stores agent sessions, processed files, and enables resumption
 */

import { readFile, writeFile, mkdir } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';
import type { AgentState, AgentSession } from '../types.js';
import type { Logger } from '../utils/logger.js';

export class StateManager {
  private stateFile: string;
  private transcriptDir: string;
  private logger: Logger;
  private state: AgentState;

  constructor(outputDir: string, logger: Logger) {
    this.stateFile = path.join(outputDir, 'agent-state.json');
    this.transcriptDir = path.join(outputDir, '..', 'transcripts');
    this.logger = logger;
    this.state = this.getDefaultState();
  }

  /**
   * Initialize state manager - load existing state or create new
   */
  async initialize(): Promise<void> {
    try {
      await mkdir(path.dirname(this.stateFile), { recursive: true });
      await mkdir(this.transcriptDir, { recursive: true });

      if (existsSync(this.stateFile)) {
        await this.loadState();
        this.logger.info('State loaded from disk', {
          sessions: this.state.previousSessions.length,
          processedFiles: this.state.processedFiles.length,
        });
      } else {
        this.logger.info('Initialized new state');
      }
    } catch (error) {
      this.logger.error('Failed to initialize state manager', error);
      throw error;
    }
  }

  /**
   * Load state from disk
   */
  private async loadState(): Promise<void> {
    try {
      const data = await readFile(this.stateFile, 'utf-8');
      const loadedState = JSON.parse(data);

      // Convert date strings back to Date objects
      this.state = {
        ...loadedState,
        currentSession: loadedState.currentSession
          ? {
              ...loadedState.currentSession,
              startedAt: new Date(loadedState.currentSession.startedAt),
              lastActivityAt: new Date(loadedState.currentSession.lastActivityAt),
              conversationHistory: loadedState.currentSession.conversationHistory.map(
                (msg: { timestamp: string }) => ({
                  ...msg,
                  timestamp: new Date(msg.timestamp),
                })
              ),
            }
          : null,
        previousSessions: loadedState.previousSessions.map((session: {
          startedAt: string;
          lastActivityAt: string;
          conversationHistory: { timestamp: string }[];
        }) => ({
          ...session,
          startedAt: new Date(session.startedAt),
          lastActivityAt: new Date(session.lastActivityAt),
          conversationHistory: session.conversationHistory.map(msg => ({
            ...msg,
            timestamp: new Date(msg.timestamp),
          })),
        })),
        lastSavedAt: new Date(loadedState.lastSavedAt),
      };
    } catch (error) {
      this.logger.error('Failed to load state', error);
      this.state = this.getDefaultState();
    }
  }

  /**
   * Save state to disk
   */
  async saveState(): Promise<void> {
    try {
      this.state.lastSavedAt = new Date();
      const data = JSON.stringify(this.state, null, 2);
      await writeFile(this.stateFile, data, 'utf-8');
      this.logger.debug('State saved to disk');
    } catch (error) {
      this.logger.error('Failed to save state', error);
    }
  }

  /**
   * Get default state
   */
  private getDefaultState(): AgentState {
    return {
      currentSession: null,
      previousSessions: [],
      processedFiles: [],
      pendingFiles: [],
      lastSavedAt: new Date(),
    };
  }

  /**
   * Start a new agent session
   */
  startSession(agentId: string, agentName: string, prompt: string): AgentSession {
    const session: AgentSession = {
      agentId,
      agentName,
      startedAt: new Date(),
      lastActivityAt: new Date(),
      status: 'active',
      prompt,
      conversationHistory: [],
      metadata: {},
    };

    this.state.currentSession = session;
    this.saveState();

    this.logger.info('Started new agent session', {
      agentId,
      agentName,
    });

    return session;
  }

  /**
   * Update current session
   */
  updateSession(updates: Partial<AgentSession>): void {
    if (!this.state.currentSession) {
      this.logger.warn('No active session to update');
      return;
    }

    this.state.currentSession = {
      ...this.state.currentSession,
      ...updates,
      lastActivityAt: new Date(),
    };

    this.saveState();
  }

  /**
   * Complete current session
   */
  completeSession(success: boolean): void {
    if (!this.state.currentSession) {
      this.logger.warn('No active session to complete');
      return;
    }

    this.state.currentSession.status = success ? 'completed' : 'failed';
    this.state.previousSessions.push(this.state.currentSession);
    this.state.currentSession = null;

    this.saveState();

    this.logger.info('Session completed', { success });
  }

  /**
   * Get session by agent ID
   */
  getSession(agentId: string): AgentSession | null {
    // Check current session
    if (this.state.currentSession?.agentId === agentId) {
      return this.state.currentSession;
    }

    // Check previous sessions
    return this.state.previousSessions.find(s => s.agentId === agentId) || null;
  }

  /**
   * Get last agent ID
   */
  getLastAgentId(): string | null {
    if (this.state.currentSession) {
      return this.state.currentSession.agentId;
    }

    if (this.state.previousSessions.length > 0) {
      const lastSession = this.state.previousSessions[this.state.previousSessions.length - 1];
      return lastSession.agentId;
    }

    return null;
  }

  /**
   * Mark file as processed
   */
  markFileProcessed(filePath: string): void {
    if (!this.state.processedFiles.includes(filePath)) {
      this.state.processedFiles.push(filePath);
      this.saveState();
      this.logger.debug('Marked file as processed', { file: filePath });
    }
  }

  /**
   * Check if file is processed
   */
  isFileProcessed(filePath: string): boolean {
    return this.state.processedFiles.includes(filePath);
  }

  /**
   * Get all processed files
   */
  getProcessedFiles(): string[] {
    return [...this.state.processedFiles];
  }

  /**
   * Add pending file
   */
  addPendingFile(filePath: string): void {
    if (!this.state.pendingFiles.includes(filePath)) {
      this.state.pendingFiles.push(filePath);
      this.saveState();
    }
  }

  /**
   * Remove pending file
   */
  removePendingFile(filePath: string): void {
    this.state.pendingFiles = this.state.pendingFiles.filter(f => f !== filePath);
    this.saveState();
  }

  /**
   * Get all pending files
   */
  getPendingFiles(): string[] {
    return [...this.state.pendingFiles];
  }

  /**
   * Save transcript for agent session
   */
  async saveTranscript(agentId: string, content: string): Promise<void> {
    try {
      const transcriptFile = path.join(this.transcriptDir, `agent-${agentId}.jsonl`);
      await writeFile(transcriptFile, content, 'utf-8');
      this.logger.debug('Transcript saved', { agentId });
    } catch (error) {
      this.logger.error('Failed to save transcript', error);
    }
  }

  /**
   * Load transcript for agent session
   */
  async loadTranscript(agentId: string): Promise<string | null> {
    try {
      const transcriptFile = path.join(this.transcriptDir, `agent-${agentId}.jsonl`);
      if (existsSync(transcriptFile)) {
        return await readFile(transcriptFile, 'utf-8');
      }
      return null;
    } catch (error) {
      this.logger.error('Failed to load transcript', error);
      return null;
    }
  }

  /**
   * Reset state (for fresh start)
   */
  async resetState(): Promise<void> {
    this.state = this.getDefaultState();
    await this.saveState();
    this.logger.warn('State reset to defaults');
  }
}
