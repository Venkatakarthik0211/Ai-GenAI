/**
 * AWS Bedrock Authentication Manager
 * Handles AWS credentials and bearer token generation
 */

import { STSClient, GetCallerIdentityCommand } from '@aws-sdk/client-sts';
import { fromIni } from '@aws-sdk/credential-providers';
import type { BedrockConfig } from '../types.js';
import type { Logger } from '../utils/logger.js';

export class BedrockAuth {
  private config: BedrockConfig;
  private logger: Logger;
  private bearerToken: string | null = null;

  constructor(config: BedrockConfig, logger: Logger) {
    this.config = config;
    this.logger = logger;
  }

  /**
   * Verify AWS credentials are valid
   */
  async verifyCredentials(): Promise<boolean> {
    try {
      this.logger.info('Verifying AWS credentials...', {
        region: this.config.region,
        profile: this.config.profile,
      });

      const stsClient = new STSClient({
        region: this.config.region,
        credentials: fromIni({ profile: this.config.profile }),
      });

      const command = new GetCallerIdentityCommand({});
      const response = await stsClient.send(command);

      this.logger.success('AWS credentials verified', {
        account: response.Account,
        arn: response.Arn,
      });

      return true;
    } catch (error) {
      this.logger.error('AWS credential verification failed', error);
      return false;
    }
  }

  /**
   * Generate Bedrock bearer token using Python script
   * This maintains compatibility with existing bedrock.py
   */
  async generateBearerToken(): Promise<string> {
    try {
      this.logger.info('Generating Bedrock bearer token...');

      const { execSync } = await import('child_process');

      // Execute the existing bedrock.py script
      const result = execSync('python3 /workspace/bedrock.py', {
        encoding: 'utf-8',
        env: {
          ...process.env,
          AWS_REGION: this.config.region,
          AWS_PROFILE: this.config.profile,
        },
      });

      const tokenData = JSON.parse(result);
      this.bearerToken = tokenData.bearerToken;

      this.logger.success('Bearer token generated', {
        tokenPrefix: this.bearerToken?.substring(0, 50) + '...',
      });

      return this.bearerToken;
    } catch (error) {
      this.logger.error('Failed to generate bearer token', error);
      throw new Error('Bearer token generation failed');
    }
  }

  /**
   * Get current bearer token (generate if not exists)
   */
  async getBearerToken(): Promise<string> {
    if (!this.bearerToken) {
      await this.generateBearerToken();
    }
    return this.bearerToken!;
  }

  /**
   * Get Anthropic SDK configuration for Bedrock
   */
  async getAnthropicConfig(): Promise<{
    apiKey: string;
    baseURL: string;
  }> {
    const bearerToken = await this.getBearerToken();

    return {
      apiKey: bearerToken,
      baseURL: 'https://bedrock-runtime.' + this.config.region + '.amazonaws.com',
    };
  }
}
