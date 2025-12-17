/**
 * Zod validation schemas for forms.
 */
import { z } from 'zod'

/**
 * Login form validation schema.
 */
export const loginSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email address'),
  password: z
    .string()
    .min(1, 'Password is required'),
})

export type LoginFormData = z.infer<typeof loginSchema>

/**
 * Registration form validation schema.
 */
export const registerSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email address'),
  username: z
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(100, 'Username must be at most 100 characters')
    .regex(
      /^[a-zA-Z][a-zA-Z0-9_-]*$/,
      'Username must start with a letter and contain only alphanumeric characters, underscores, and hyphens'
    ),
  full_name: z
    .string()
    .min(1, 'Full name is required')
    .max(255, 'Full name must be at most 255 characters'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .max(100, 'Password must be at most 100 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number'),
  confirmPassword: z
    .string()
    .min(1, 'Please confirm your password'),
  bio: z
    .string()
    .max(1000, 'Bio must be at most 1000 characters')
    .optional(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ['confirmPassword'],
})

export type RegisterFormData = z.infer<typeof registerSchema>

/**
 * User create/edit form validation schema.
 */
export const userSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email address'),
  username: z
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(100, 'Username must be at most 100 characters')
    .regex(
      /^[a-zA-Z][a-zA-Z0-9_-]*$/,
      'Username must start with a letter and contain only alphanumeric characters, underscores, and hyphens'
    ),
  full_name: z
    .string()
    .min(1, 'Full name is required')
    .max(255, 'Full name must be at most 255 characters'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .max(100, 'Password must be at most 100 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number')
    .optional()
    .or(z.literal('')),
  bio: z
    .string()
    .max(1000, 'Bio must be at most 1000 characters')
    .optional(),
})

export type UserFormData = z.infer<typeof userSchema>

/**
 * User update form validation schema (for profile editing).
 */
export const userUpdateSchema = z.object({
  email: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email address')
    .optional(),
  username: z
    .string()
    .min(3, 'Username must be at least 3 characters')
    .max(100, 'Username must be at most 100 characters')
    .regex(
      /^[a-zA-Z][a-zA-Z0-9_-]*$/,
      'Username must start with a letter and contain only alphanumeric characters, underscores, and hyphens'
    )
    .optional(),
  full_name: z
    .string()
    .min(1, 'Full name is required')
    .max(255, 'Full name must be at most 255 characters')
    .optional(),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .max(100, 'Password must be at most 100 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number')
    .optional()
    .or(z.literal('')),
  bio: z
    .string()
    .max(1000, 'Bio must be at most 1000 characters')
    .optional(),
})

export type UserUpdateFormData = z.infer<typeof userUpdateSchema>
