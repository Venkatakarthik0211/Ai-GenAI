# React TypeScript Frontend - UserHub UI

Create a complete React TypeScript frontend for the UserHub user management application.

## Requirements

### Core Features
1. **Authentication UI**
   - Login page with email/password
   - Registration page with form validation
   - Protected routes (redirect to login if not authenticated)
   - Token storage in localStorage
   - Auto-logout on token expiry

2. **User Management Interface**
   - User list table with pagination
   - User detail view
   - Create/Edit user forms
   - Delete user with confirmation modal
   - Search and filter functionality

3. **API Integration**
   - Axios HTTP client with interceptors
   - JWT token handling (add to headers)
   - Error handling and display
   - Loading states
   - API response type definitions

4. **User Experience**
   - Responsive design (mobile-friendly)
   - Loading spinners
   - Error notifications (toast/alert)
   - Success feedback
   - Form validation with error messages

## Files to Create

### 1. `App.tsx` (150-200 lines)
- React Router setup with routes
- Authentication context provider
- Layout component with navigation
- Protected route wrapper
- Global error boundary

### 2. `main.tsx` (30-40 lines)
- React app initialization
- StrictMode wrapper
- Root element rendering

### 3. `index.html` (30-40 lines)
- HTML template
- Meta tags for responsive design
- Root div element

### 4. `vite.config.ts` (30-50 lines)
- Vite configuration
- Proxy setup for API calls
- Path aliases
- Build optimization

### 5. `tsconfig.json` (40-60 lines)
- TypeScript configuration
- Strict mode enabled
- Path mappings
- JSX configuration

### 6. `package.json` (40-60 lines)
All dependencies with versions:
- react, react-dom (^18.2.0)
- react-router-dom (^6.20.0)
- axios (^1.6.0)
- @tanstack/react-query (^5.0.0)
- react-hook-form (^7.48.0)
- zod (^3.22.0)
- zustand (^4.4.0)
- react-toastify (^9.1.0)
- Development dependencies (vite, typescript, eslint, etc.)

### 7. `src/api/client.ts` (80-100 lines)
- Axios instance configuration
- Request/response interceptors
- Token injection
- Error handling
- Base URL from environment

### 8. `src/api/auth.ts` (60-80 lines)
- Login API call
- Register API call
- Logout function
- Refresh token function
- Get current user

### 9. `src/api/users.ts` (100-120 lines)
- Get all users (with pagination)
- Get user by ID
- Create user
- Update user
- Delete user
- TypeScript interfaces for requests/responses

### 10. `src/types/user.ts` (40-60 lines)
- User interface
- AuthResponse interface
- Pagination types
- API response types

### 11. `src/contexts/AuthContext.tsx` (150-200 lines)
- Authentication state management
- Login/logout functions
- Token storage
- User context provider
- useAuth custom hook

### 12. `src/components/auth/LoginForm.tsx` (120-150 lines)
- Login form with react-hook-form
- Email and password inputs
- Form validation with zod
- Submit handler
- Error display
- Link to registration

### 13. `src/components/auth/RegisterForm.tsx` (150-180 lines)
- Registration form
- Name, email, password, confirm password
- Form validation
- Submit handler
- Link to login

### 14. `src/components/users/UserList.tsx` (200-250 lines)
- User table component
- Pagination controls
- Search input
- Edit/Delete action buttons
- Loading skeleton
- Empty state

### 15. `src/components/users/UserForm.tsx` (150-180 lines)
- Create/Edit user form
- Form fields (name, email, etc.)
- Validation
- Submit handler
- Cancel button

### 16. `src/components/users/UserDetail.tsx` (100-120 lines)
- Display user information
- Edit button
- Delete button
- Back to list button

### 17. `src/components/common/ProtectedRoute.tsx` (40-60 lines)
- Route wrapper component
- Authentication check
- Redirect to login if not authenticated

### 18. `src/components/common/Navbar.tsx` (80-100 lines)
- Navigation bar
- Logo/Brand
- User menu with logout
- Responsive mobile menu

### 19. `src/components/common/LoadingSpinner.tsx` (30-40 lines)
- Loading spinner component
- Centered with animation

### 20. `src/components/common/ErrorMessage.tsx` (30-40 lines)
- Error display component
- Styled error message

### 21. `src/pages/LoginPage.tsx` (50-70 lines)
- Login page layout
- LoginForm integration
- Redirect after login

### 22. `src/pages/RegisterPage.tsx` (50-70 lines)
- Registration page layout
- RegisterForm integration
- Redirect after registration

### 23. `src/pages/UsersPage.tsx` (80-100 lines)
- Users list page
- UserList component
- Create user button
- Search and filters

### 24. `src/pages/UserDetailPage.tsx` (60-80 lines)
- User detail page
- Fetch user by ID from route params
- UserDetail component

### 25. `src/pages/UserFormPage.tsx` (80-100 lines)
- Create/Edit user page
- UserForm component
- Determine create vs edit from route

### 26. `src/hooks/useUsers.ts` (100-120 lines)
- Custom hook for user operations
- React Query hooks
- useGetUsers, useGetUser, useCreateUser, useUpdateUser, useDeleteUser
- Caching and invalidation

### 27. `src/utils/validators.ts` (60-80 lines)
- Zod validation schemas
- loginSchema, registerSchema, userSchema
- Reusable validation functions

### 28. `src/styles/index.css` (150-200 lines)
- Global styles
- CSS reset
- Utility classes
- Responsive breakpoints
- Color variables

### 29. `.env.example`
```
VITE_API_BASE_URL=http://localhost:8000
```

### 30. `vite-env.d.ts`
- Vite environment types

## Technical Stack
- **Framework**: React 18.2+
- **Language**: TypeScript 5.0+
- **Build Tool**: Vite 5.0+
- **Routing**: React Router 6.20+
- **HTTP Client**: Axios 1.6+
- **State Management**: Zustand 4.4+ (or Context API)
- **Server State**: TanStack Query (React Query) 5.0+
- **Forms**: React Hook Form 7.48+
- **Validation**: Zod 3.22+
- **Notifications**: React Toastify 9.1+
- **Styling**: CSS Modules or plain CSS

## Code Quality Requirements
- ✅ TypeScript strict mode
- ✅ Type definitions for all props and state
- ✅ Reusable components
- ✅ Custom hooks for logic reuse
- ✅ Error boundaries
- ✅ Loading states
- ✅ Responsive design
- ✅ Accessible forms (labels, ARIA)
- ✅ ESLint-compatible code
- ✅ Production-ready (no console.logs, no TODOs)

## Routes

### Public Routes
- `/login` - Login page
- `/register` - Registration page

### Protected Routes
- `/` - Redirect to /users
- `/users` - User list page
- `/users/new` - Create user page
- `/users/:id` - User detail page
- `/users/:id/edit` - Edit user page

## Component Architecture

```
src/
├── main.tsx
├── App.tsx
├── vite-env.d.ts
├── api/
│   ├── client.ts
│   ├── auth.ts
│   └── users.ts
├── types/
│   └── user.ts
├── contexts/
│   └── AuthContext.tsx
├── components/
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   └── RegisterForm.tsx
│   ├── users/
│   │   ├── UserList.tsx
│   │   ├── UserForm.tsx
│   │   └── UserDetail.tsx
│   └── common/
│       ├── ProtectedRoute.tsx
│       ├── Navbar.tsx
│       ├── LoadingSpinner.tsx
│       └── ErrorMessage.tsx
├── pages/
│   ├── LoginPage.tsx
│   ├── RegisterPage.tsx
│   ├── UsersPage.tsx
│   ├── UserDetailPage.tsx
│   └── UserFormPage.tsx
├── hooks/
│   └── useUsers.ts
├── utils/
│   └── validators.ts
└── styles/
    └── index.css
```

## Special Instructions

1. **API Integration**
   - Use axios interceptors to add JWT token to all requests
   - Handle 401 responses by redirecting to login
   - Display user-friendly error messages

2. **Form Validation**
   - Email format validation
   - Password strength requirements (min 8 chars, 1 uppercase, 1 number)
   - Confirm password matching
   - Required field validation

3. **User Experience**
   - Show loading spinners during API calls
   - Display success toasts after CRUD operations
   - Confirm before deleting users
   - Auto-focus first input on forms
   - Disable submit buttons while loading

4. **Responsive Design**
   - Mobile-first approach
   - Hamburger menu on mobile
   - Responsive table (stack on mobile)
   - Touch-friendly buttons

5. **Security**
   - Store JWT in localStorage (with httpOnly note for production)
   - Clear token on logout
   - Validate all user inputs
   - Escape user-generated content

6. **Performance**
   - Use React.memo for expensive components
   - Implement pagination (not load all users at once)
   - Lazy load routes with React.lazy
   - Optimize bundle size

7. **Accessibility**
   - Semantic HTML elements
   - Label all form inputs
   - Keyboard navigation support
   - ARIA attributes where needed

8. Make the app ready to run with `npm run dev`
