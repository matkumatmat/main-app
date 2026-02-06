# KAuth Frontend - Authentication UI

Modern, mobile-first authentication interface built with Astro, React, Tailwind CSS v4, and Zod validation. Features dark theme with lemon green accent colors.

## Features

- Full-page sign in, sign up, and OTP verification
- Modern, responsive design with mobile-first approach
- Dark theme with lemon green primary color
- Split-screen layout on desktop with animated placeholders
- Client-side form validation with Zod
- Animated OTP input with auto-focus and paste support
- Type-safe API calls with Axios
- Separated concerns: UI components, stateful components, controllers, and API layer
- Automatic token refresh and error handling

## Tech Stack

- **Framework**: Astro 5.x
- **UI Library**: React 19.x
- **Styling**: Tailwind CSS v4
- **Validation**: Zod
- **HTTP Client**: Axios
- **Animations**: Framer Motion
- **Language**: TypeScript

## Project Structure

```
src/
├── components/
│   ├── Auth/              # Stateful React components
│   │   ├── SignInForm.tsx
│   │   ├── SignUpForm.tsx
│   │   └── OtpForm.tsx
│   └── UI/                # Reusable UI components
│       ├── Button.tsx
│       ├── Input.tsx
│       └── Card.tsx
├── controllers/
│   └── authController.ts  # Authentication business logic
├── lib/
│   ├── api/
│   │   └── apiClient.ts   # Axios configuration & interceptors
│   └── schemas/
│       └── authSchemas.ts # Zod validation schemas
├── pages/
│   ├── sign-in.astro      # Sign-in page
│   ├── sign-up.astro      # Sign-up page
│   └── verify-otp.astro   # OTP verification page
├── layouts/
│   └── Layout.astro       # Base layout with metadata
└── styles/
    └── global.css         # Tailwind + theme configuration
```

## Getting Started

### Prerequisites

- Node.js 18.x or higher
- pnpm 8.x or higher

### Installation

```bash
pnpm install
```

### Development

```bash
pnpm dev
```

This starts the development server at `http://localhost:4321`

### Build for Production

```bash
pnpm build
```

Build artifacts will be in `./dist/`

### Preview Production Build

```bash
pnpm preview
```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
PUBLIC_API_BASE_URL=http://localhost/api/auth
```

For development, the default is `http://localhost/api/auth` which routes through nginx to the backend.

## Pages

### Sign In (`/sign-in`)

- Email and password authentication
- Remember me checkbox
- Forgot password link
- Link to sign up page
- Split-screen layout on desktop with animated icons

### Sign Up (`/sign-up`)

- Full name, email, and password registration
- Password confirmation with validation
- Password strength requirements displayed
- Terms of service agreement
- Link to sign in page
- Split-screen layout on desktop with statistics

### Verify OTP (`/verify-otp`)

- 6-digit OTP input with animations
- Auto-focus between input boxes
- Paste support for quick entry
- Resend OTP with cooldown timer
- Email display for verification context
- Split-screen layout on desktop with verification steps

## Validation Rules

### Sign In
- Email: Required, valid format
- Password: Required, min 8 characters

### Sign Up
- Full Name: Required, 2-100 characters
- Email: Required, valid format
- Password: Required, 8-128 characters, must contain:
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
- Confirm Password: Must match password

### OTP Verification
- OTP: Required, exactly 6 digits, numeric only

## API Integration

The frontend communicates with the backend via REST API. All API calls are handled through the `authController` which uses `apiClient` for HTTP requests.

### Request Headers

All requests include:
- `Content-Type: application/json`
- `Accept: application/json`
- `X-Client-Version: 1.0.0`
- `X-Client-Platform: web`
- `X-Request-Id`: UUID v4
- `X-Request-Timestamp`: ISO 8601 timestamp
- `Authorization`: Bearer token (when authenticated)

### Endpoints Used

- `POST /signup` - User registration
- `POST /signin` - User authentication
- `POST /verify-otp` - Email verification
- `POST /resend-otp` - Resend OTP code
- `POST /refresh` - Refresh access token
- `POST /signout` - Sign out user

See `API.md` for complete endpoint documentation.

## State Management

### Token Storage

Tokens are stored in `localStorage`:
- `accessToken`: JWT access token (1 hour expiry)
- `refreshToken`: JWT refresh token (7 days expiry)

### Automatic Token Refresh

The `apiClient` includes an interceptor that:
1. Detects 401 Unauthorized responses
2. Attempts to refresh the access token using refresh token
3. Retries the original request with new token
4. Redirects to sign-in if refresh fails

## Error Handling

### Validation Errors
- Displayed inline below each form field
- Real-time validation on input change
- Clear error on field correction

### API Errors
- Displayed in alert box above form
- Includes server-provided error message
- Auto-clears on new submission

### Network Errors
- Generic user-friendly message
- Retry option available

## Styling Guide

### Theme Colors

**Primary Color** (Lemon Green):
- `lime-50` to `lime-900` - Custom palette defined in global.css
- Primary CTA: `lime-400` (#a8ff33)

**Dark Theme**:
- Background: `#0a0a0a` with gradient to `#1a1a1a`
- Cards: `gray-800` with `gray-700` borders
- Text: White with `gray-300/400` for secondary text

### Component Styling Patterns

**Buttons**:
- Primary: Lime green background, dark text
- Secondary: Gray background, white text
- Outline: Transparent with lime border
- Ghost: Transparent with gray hover

**Inputs**:
- Dark background (`gray-800`)
- Gray border with lime focus ring
- Error state with red border and text

**Cards**:
- Dark background with blur effect
- Rounded corners (`rounded-2xl`)
- Shadow and border for depth

## Animations

### Framer Motion

Used for:
- Form entrance animations (fade + slide)
- Error message animations (scale + fade)
- OTP input staggered entrance
- Icon pulse animations

### CSS Animations

Used for:
- Button hover transitions
- Input focus effects
- Loading spinners

## Accessibility

- Semantic HTML elements
- Proper form labels
- Keyboard navigation support
- ARIA attributes where needed
- Focus visible indicators
- Error announcements

## Mobile Responsiveness

### Breakpoints

- Mobile: `< 768px` (default)
- Desktop: `>= 1024px` (split-screen layout)

### Mobile Optimizations

- Single column layout
- Full-width forms
- Touch-friendly button sizes
- Optimized OTP input for mobile keyboards
- Responsive typography

## Performance

- Static page generation with Astro
- Code splitting for React components
- Lazy loading with `client:load` directive
- Optimized animations with GPU acceleration
- Minimized bundle size

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development Tips

### Adding New Form Fields

1. Update Zod schema in `lib/schemas/authSchemas.ts`
2. Add field to form component state
3. Add Input component with validation
4. Update controller if API changes

### Customizing Theme

Edit `src/styles/global.css`:
- Modify `@theme` section for color palette
- Update CSS variables for spacing/sizing
- Adjust gradient backgrounds

### Adding New Pages

1. Create `.astro` file in `src/pages/`
2. Import Layout component
3. Import form component with `client:load`
4. Update navigation links

## Testing Locally with Backend

1. Ensure backend is running on port 8001 (Public Server)
2. Ensure nginx is running and routing `/api/auth/*` to backend
3. Start frontend dev server: `pnpm dev`
4. Access frontend at `http://localhost:4321`
5. API calls will route through nginx to backend

## Production Deployment

1. Set `PUBLIC_API_BASE_URL` to production API endpoint
2. Build: `pnpm build`
3. Serve static files from `dist/` directory
4. Configure nginx to:
   - Serve frontend static files
   - Route `/api/auth/*` to backend
   - Handle client-side routing (fallback to index.html)

## Troubleshooting

### API calls failing
- Check `PUBLIC_API_BASE_URL` is correct
- Verify backend is running
- Check nginx configuration
- Inspect browser network tab for details

### Styling not applied
- Clear browser cache
- Check Tailwind config
- Verify global.css is imported in Layout

### OTP input not working
- Check JavaScript is enabled
- Verify React hydration with `client:load`
- Check browser console for errors

## Additional Documentation

- **API Documentation**: See `API.md` for complete backend API specification
- **Architecture**: See root `CLAUDE.md` for project architecture
- **Component Docs**: See inline TypeScript comments in components

## License

Part of KAuth multi-service platform.

## Support

For issues or questions:
1. Check this README
2. Review API.md for endpoint details
3. Check component source code
4. Review CLAUDE.md for architecture guidelines
