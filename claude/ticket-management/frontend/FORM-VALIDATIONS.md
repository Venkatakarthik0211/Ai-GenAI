# Form Validation Rules

Comprehensive frontend validation to prevent backend errors and improve user experience.

## 📋 Table of Contents

- [Register Form](#register-form)
- [Login Form](#login-form)
- [Forgot Password Form](#forgot-password-form)
- [Reset Password Form](#reset-password-form)

---

## Register Form

**File**: `src/components/auth/RegisterForm/RegisterForm.tsx`

### Validation Rules

#### First Name
- ✅ **Required**: Cannot be empty
- ✅ **Min length**: 1 character
- ✅ **Max length**: 50 characters
- ✅ **Pattern**: Only letters, spaces, hyphens, and apostrophes (`^[a-zA-Z\s'-]+$`)
- ❌ **Example errors**: "John123", "John@Doe", "J0hn"

#### Last Name
- ✅ **Required**: Cannot be empty
- ✅ **Min length**: 1 character
- ✅ **Max length**: 50 characters
- ✅ **Pattern**: Only letters, spaces, hyphens, and apostrophes (`^[a-zA-Z\s'-]+$`)
- ❌ **Example errors**: "Smith123", "Smith@", "Sm1th"

#### Email
- ✅ **Required**: Cannot be empty
- ✅ **Format**: Valid email format (RFC 5322 compliant)
- ✅ **Max length**: 100 characters
- ✅ **Auto-transform**: Converted to lowercase
- ✅ **Auto-trim**: Removes leading/trailing spaces
- ✅ **Example valid**: `john.doe@example.com`, `user+tag@domain.co.uk`
- ❌ **Example invalid**: `notanemail`, `@example.com`, `user@.com`

#### Username
- ✅ **Required**: Cannot be empty
- ✅ **Min length**: 3 characters
- ✅ **Max length**: 50 characters
- ✅ **Pattern**: Letters, numbers, underscores, hyphens only (`^[a-zA-Z0-9_-]+$`)
- ✅ **Must start with**: Letter (`^[a-zA-Z]`)
- ✅ **Example valid**: `john_doe`, `user123`, `john-smith`
- ❌ **Example invalid**: `123user` (starts with number), `user@name` (special char), `ab` (too short)

#### Password
- ✅ **Required**: Cannot be empty
- ✅ **Min length**: 8 characters
- ✅ **Max length**: 128 characters
- ✅ **Complexity requirements** (all required):
  - At least 1 uppercase letter (A-Z)
  - At least 1 lowercase letter (a-z)
  - At least 1 digit (0-9)
  - At least 1 special character (`@$!%*?&#^()_+-=[]{}|;:,.<>`)
- ✅ **Visual feedback**: Password strength meter
- ✅ **Real-time validation**: Shows which requirements are met
- ✅ **Example valid**: `MyP@ssw0rd`, `Secure#123`, `C0mpl3x!Pass`
- ❌ **Example invalid**: `password` (no uppercase/number/special), `PASSWORD123` (no lowercase/special)

#### Confirm Password
- ✅ **Required**: Cannot be empty
- ✅ **Must match**: Password field
- ✅ **Real-time comparison**: Shows error immediately when doesn't match

#### Phone Number (Optional)
- ✅ **Optional**: Can be left empty
- ✅ **Format**: E.164 international format (`^\+[1-9]\d{6,14}$`)
  - Must start with `+`
  - Country code (1-9)
  - 7-15 total digits after country code
- ✅ **Example valid**: `+1234567890`, `+911234567890`, `+441234567890`
- ❌ **Example invalid**: `1234567890` (no +), `+123` (too short), `+91411815` (too short)
- 💡 **Hint shown**: "Format: +[country code][number] (e.g., +911234567890 for India)"

#### Department (Optional)
- ✅ **Optional**: Can be left empty
- ✅ **Max length**: 100 characters

#### Terms & Conditions
- ✅ **Required**: Must be checked
- ✅ **Type**: Boolean checkbox
- ❌ **Error if unchecked**: "You must accept the terms and conditions"

---

## Login Form

**File**: `src/components/auth/LoginForm/LoginForm.tsx`

### Validation Rules

#### Username/Email
- ✅ **Required**: Cannot be empty
- ✅ **Min length**: 3 characters
- ✅ **Max length**: 100 characters
- ✅ **Auto-trim**: Removes leading/trailing spaces
- ✅ **Accepts**: Both email and username formats

#### Password
- ✅ **Required**: Cannot be empty
- ✅ **Min length**: 8 characters
- ✅ **Max length**: 128 characters
- ✅ **No complexity check**: Only length validation (backend validates on login)

---

## Forgot Password Form

**File**: `src/components/auth/ForgotPasswordForm/ForgotPasswordForm.tsx`

### Validation Rules

#### Email
- ✅ **Required**: Cannot be empty
- ✅ **Format**: Valid email format
- ✅ **Max length**: 100 characters
- ✅ **Auto-transform**: Converted to lowercase
- ✅ **Auto-trim**: Removes leading/trailing spaces
- ✅ **Example valid**: `user@example.com`
- ❌ **Example invalid**: `notanemail`, `user@`, `@domain.com`

---

## Reset Password Form

**File**: `src/components/auth/ResetPasswordForm/ResetPasswordForm.tsx`

### Validation Rules

#### New Password
- ✅ **Required**: Cannot be empty
- ✅ **Min length**: 8 characters
- ✅ **Max length**: 128 characters
- ✅ **Complexity requirements** (all required):
  - At least 1 uppercase letter (A-Z)
  - At least 1 lowercase letter (a-z)
  - At least 1 digit (0-9)
  - At least 1 special character (`@$!%*?&#^()_+-=[]{}|;:,.<>`)
- ✅ **Visual feedback**: Password strength meter
- ✅ **Real-time validation**: Shows which requirements are met

#### Confirm Password
- ✅ **Required**: Cannot be empty
- ✅ **Must match**: New password field
- ✅ **Real-time comparison**: Shows error when doesn't match

---

## 🎯 Validation Patterns Summary

### Password Regex
```javascript
/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^()_+\-=\[\]{}|;:,.<>])[A-Za-z\d@$!%*?&#^()_+\-=\[\]{}|;:,.<>]{8,}$/
```

### Phone Number Regex (E.164)
```javascript
/^\+[1-9]\d{6,14}$/
```

### Username Pattern
```javascript
/^[a-zA-Z0-9_-]+$/  // Allowed characters
/^[a-zA-Z]/          // Must start with letter
```

### Name Pattern
```javascript
/^[a-zA-Z\s'-]+$/   // Letters, spaces, hyphens, apostrophes only
```

---

## 🛡️ Security Features

### Password Strength Indicator
- **Weak** (0-40%): Red - Missing multiple requirements
- **Fair** (41-60%): Orange - Meets basic requirements
- **Good** (61-80%): Blue - Strong password
- **Strong** (81-100%): Green - Very strong password

### Real-time Validation
- ✅ Immediate feedback on field blur
- ✅ Live password strength calculation
- ✅ Real-time password match checking
- ✅ Character count validation

### Prevention of Common Errors
- ✅ Trims whitespace automatically
- ✅ Converts email to lowercase
- ✅ Enforces minimum security standards
- ✅ Prevents invalid characters
- ✅ Validates format before submission

---

## 🚫 Error Prevention

### Backend Error Prevention

#### Phone Number Format
**Backend expects**: E.164 format with 10-15 digits after country code
**Frontend enforces**: `+[country code][7-15 digits]`
**Prevents**: `CheckViolation: chk_users_phone_format`

#### Email Format
**Backend expects**: Valid email, max 100 characters
**Frontend enforces**: RFC 5322 email validation, 100 char limit
**Prevents**: Invalid email format errors

#### Password Complexity
**Backend expects**: Min 8 chars, uppercase, lowercase, digit, special
**Frontend enforces**: Same requirements + visual feedback
**Prevents**: Password complexity requirement errors

#### Username Format
**Backend expects**: 3-50 chars, alphanumeric + underscore/hyphen
**Frontend enforces**: Same + must start with letter
**Prevents**: Invalid username format errors

#### String Length Limits
**Backend enforces**: VARCHAR limits on all fields
**Frontend prevents**: Exceeding max lengths before submission

---

## 🎨 User Experience Features

### Visual Indicators
- ✅ Password strength meter with color coding
- ✅ Real-time requirement checklist
- ✅ Error messages in red below fields
- ✅ Field hints in gray italic text
- ✅ Success states (green borders)

### Helpful Hints
- 💡 Phone number format example shown
- 💡 Password requirements listed
- 💡 Optional fields marked clearly
- 💡 Character counters for long fields

### Accessibility
- ✅ ARIA labels on all inputs
- ✅ Error messages linked to fields
- ✅ Keyboard navigation support
- ✅ Screen reader compatible

---

## 📝 Testing Checklist

### Register Form
- [ ] Try registering with invalid phone (e.g., `+123`)
- [ ] Try weak password (e.g., `password`)
- [ ] Try username starting with number (e.g., `123user`)
- [ ] Try names with numbers (e.g., `John123`)
- [ ] Try invalid email (e.g., `notanemail`)
- [ ] Try without accepting terms
- [ ] Try mismatched passwords
- [ ] Verify all fields show proper error messages

### Login Form
- [ ] Try empty username/password
- [ ] Try username < 3 characters
- [ ] Try password < 8 characters
- [ ] Verify trim works (spaces around username)

### Forgot Password
- [ ] Try invalid email format
- [ ] Try empty email
- [ ] Verify lowercase conversion works

### Reset Password
- [ ] Try weak password
- [ ] Try mismatched passwords
- [ ] Verify password strength meter updates
- [ ] Verify requirements checklist updates

---

## 🔧 Customization

### Adding New Validation Rules

```typescript
// In the form schema
const customSchema = z.object({
  field_name: z.string()
    .min(1, 'Required')
    .max(50, 'Too long')
    .regex(/pattern/, 'Invalid format')
    .refine((val) => customLogic(val), {
      message: 'Custom error message'
    }),
})
```

### Modifying Existing Rules

Update the Zod schema in the respective form component:
- `RegisterForm.tsx` - Lines 19-59
- `LoginForm.tsx` - Lines 13-25
- `ForgotPasswordForm.tsx` - Lines 12-19
- `ResetPasswordForm.tsx` - Lines 15-26

---

## 🚀 Benefits

1. **Prevents backend errors** - Validates before API calls
2. **Better UX** - Immediate feedback vs server round-trip
3. **Reduces server load** - Invalid requests never sent
4. **Consistent validation** - Matches backend rules exactly
5. **Educational** - Users learn format requirements
6. **Accessibility** - Clear error messages for screen readers

---

## 📚 Dependencies

- **zod**: ^3.22.4 - Schema validation
- **@hookform/resolvers**: ^3.3.2 - React Hook Form + Zod integration
- **react-hook-form**: ^7.48.2 - Form state management

All validations are **client-side only** for UX improvement. Backend still performs authoritative validation for security.
