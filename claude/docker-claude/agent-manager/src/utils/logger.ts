/**
 * Production-level logger with Winston
 */

import winston from 'winston';
import type { LoggerConfig } from '../types.js';

export class Logger {
  private logger: winston.Logger;

  constructor(config: LoggerConfig) {
    const transports: winston.transport[] = [];

    // Console transport
    if (config.console) {
      transports.push(
        new winston.transports.Console({
          format: winston.format.combine(
            winston.format.colorize(),
            winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
            winston.format.printf(
              ({ timestamp, level, message }) => `[${timestamp}] ${level}: ${message}`
            )
          ),
        })
      );
    }

    // File transport
    if (config.outputFile) {
      transports.push(
        new winston.transports.File({
          filename: config.outputFile,
          format: winston.format.combine(
            winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
            winston.format.json()
          ),
        })
      );
    }

    this.logger = winston.createLogger({
      level: config.level,
      transports,
    });
  }

  info(message: string, meta?: Record<string, unknown>): void {
    this.logger.info(message, meta);
  }

  warn(message: string, meta?: Record<string, unknown>): void {
    this.logger.warn(message, meta);
  }

  error(message: string, error?: Error | unknown, meta?: Record<string, unknown>): void {
    const errorMeta = error instanceof Error ? { error: error.message, stack: error.stack } : { error };
    this.logger.error(message, { ...errorMeta, ...meta });
  }

  debug(message: string, meta?: Record<string, unknown>): void {
    this.logger.debug(message, meta);
  }

  success(message: string, meta?: Record<string, unknown>): void {
    this.info(`✓ ${message}`, meta);
  }
}
