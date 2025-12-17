# 🚀 Quick Start Guide - Frontend

## Prerequisites

- Node.js 18+ installed
- npm or yarn
- Backend API running on `http://localhost:8001`

---

## Installation

```bash
# 1. Navigate to frontend directory
cd /mnt/d/vscode/epam_git/mcp/claude/ticket-management/frontend

# 2. Install dependencies
npm install

# 3. Create environment file
cp .env.example .env

# 4. Start development server
npm run dev
```

The application will be available at: **http://localhost:3000**

---

## Environment Variables

Edit `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8001/api/v1
VITE_APP_NAME=Ticket Management System
```

---

## Available Routes

### Public Routes (No Authentication Required)
- `/login` - User login
- `/register` - New user registration
- `/forgot-password` - Request password reset
- `/reset-password?token=xxx` - Reset password with token

### Protected Routes (Coming Soon)
- `/dashboard` - Role-based dashboard
- `/profile` - User profile
- `/tickets` - Ticket management

---

## Testing the App

### 1. Register a New Account
1. Navigate to http://localhost:3000
2. Click "Signup →" link
3. Fill in the registration form:
   - First Name: John
   - Last Name: Doe
   - Email: john.doe@example.com
   - Username: johndoe
   - Password: MyP@ssw0rd! (must meet requirements)
   - Confirm Password
   - (Optional) Phone and Department
   - Accept Terms & Conditions
4. Click "CREATE ACCOUNT"
5. Check email for verification (if backend configured)

### 2. Login
1. Navigate to http://localhost:3000/login
2. Enter credentials:
   - Email/Username: johndoe
   - Password: MyP@ssw0rd!
3. Click "LOGIN"
4. You'll be redirected to dashboard (when implemented)

### 3. Forgot Password Flow
1. Click "Forgot your password?" on login page
2. Enter email address
3. Click "SEND RESET LINK"
4. Check email for reset link
5. Click link (opens /reset-password?token=xxx)
6. Enter new password
7. Click "RESET PASSWORD"
8. Redirected to login

---

## Project Structure

```
frontend/
├── src/
│   ├── api/              # API layer
│   │   ├── client/       # Axios configuration
│   │   └── endpoints/    # API endpoints
│   ├── components/       # React components
│   │   └── auth/         # Auth components
│   ├── pages/           # Page components
│   │   └── auth/        # Auth pages
│   ├── router/          # React Router setup
│   ├── types/           # TypeScript types
│   ├── App.tsx          # Main app component
│   └── main.tsx         # Entry point
├── package.json
├── vite.config.ts
└── tsconfig.json
```

---

## Key Features

### ✅ Implemented
- Login with username/email
- User registration with validation
- Password strength meter
- Username availability check
- Forgot password flow
- Reset password with token
- Toast notifications
- Loading states
- Error handling
- Responsive design
- Dark theme UI

### 🔜 Coming Soon
- Role-based dashboards
- User profile management
- Ticket management
- Admin panel
- Real-time notifications

---

## Development Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run type checking
npm run type-check

# Lint code
npm run lint

# Format code
npm run format
```

---

## Troubleshooting

### Issue: "Network Error" or "Failed to fetch"
**Solution**: Ensure backend API is running on http://localhost:8001

### Issue: "401 Unauthorized" on protected routes
**Solution**: Login again to refresh tokens

### Issue: Tokens not persisting
**Solution**: Check browser localStorage in DevTools

### Issue: CORS errors
**Solution**: Backend must have CORS configured for http://localhost:3000

---

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## Tech Stack

- **Framework**: React 18.2
- **Language**: TypeScript 5.x
- **Build Tool**: Vite 5.x
- **Router**: React Router 6.20
- **Forms**: React Hook Form 7.49
- **Validation**: Zod 3.22
- **HTTP Client**: Axios 1.6
- **Notifications**: React Hot Toast 2.4
- **State Management**: Redux Toolkit 2.0 (ready)

---

## API Endpoints Used

All endpoints from backend Postman collection:

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Create new user |
| POST | /auth/login | Authenticate user |
| POST | /auth/logout | End session |
| POST | /auth/refresh | Refresh access token |
| GET | /auth/me | Get current user |
| PUT | /auth/profile | Update profile |
| POST | /auth/change-password | Change password |
| POST | /auth/forgot-password | Request reset link |
| POST | /auth/reset-password | Reset with token |
| POST | /auth/verify-email | Verify email |
| POST | /auth/resend-verification | Resend verification |

---

## Getting Help

- 📖 See `IMPLEMENTATION-GUIDE.md` for detailed documentation
- 📖 See `AUTH-MODULE-COMPLETE.md` for implementation details
- 📖 See `FRONTEND-SYSTEM-DESIGN.md` for architecture
- 🐛 Check browser console for errors
- 🔍 Check Network tab in DevTools for API calls

---

## Next Steps

1. ✅ Authentication module complete
2. 🔜 Implement protected routes
3. 🔜 Build dashboard pages
4. 🔜 Add ticket management
5. 🔜 Implement admin features

---

**Happy Coding! 🎉**
