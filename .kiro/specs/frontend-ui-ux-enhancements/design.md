# Design Document

## Overview

The Frontend UI/UX Enhancement feature transforms the Zero Trust Security Framework's user interface into a modern, polished, and accessible web application. This design implements a comprehensive design system with consistent visual language, smooth animations, and interactive feedback mechanisms. The enhancement focuses on improving user experience through micro-interactions, responsive layouts, and performance-optimized animations while maintaining the existing React + Tailwind CSS architecture.

### Core Design Principles

1. **Consistency**: Unified design language across all components using design tokens
2. **Feedback**: Immediate visual response to all user interactions
3. **Performance**: 60fps animations using hardware-accelerated CSS properties
4. **Accessibility**: WCAG 2.1 AA compliance with keyboard navigation and screen reader support
5. **Progressive Enhancement**: Core functionality works without JavaScript, enhanced with animations
6. **Mobile-First**: Responsive design starting from mobile and scaling up

## Architecture

### Technology Stack Enhancement

**New Dependencies:**
- `framer-motion`: ^11.0.0 - Complex animations and gestures
- `react-hot-toast`: ^2.4.1 - Toast notification system
- `lucide-react`: ^0.300.0 - Consistent icon library
- `clsx`: ^2.1.0 - Conditional className utility
- `date-fns`: ^3.0.0 - Date formatting
- `@headlessui/react`: ^1.7.0 - Accessible unstyled components

**Existing Stack:**
- React 19.2.0
- Tailwind CSS 3.4.18
- Recharts 3.4.1 (already installed)
- React Router DOM 7.9.5

### Design System Architecture

```
src/
├── styles/
│   ├── design-tokens.css      # CSS custom properties for colors, spacing, etc.
│   ├── animations.css          # Reusable animation keyframes
│   └── utilities.css           # Custom utility classes
├── components/
│   ├── ui/                     # Base UI components (Button, Card, Input, etc.)
│   ├── animated/               # Animated wrapper components
│   └── layouts/                # Layout components with animations
├── hooks/
│   ├── useAnimation.js         # Custom animation hooks
│   ├── useMediaQuery.js        # Responsive design hook
│   └── useReducedMotion.js     # Accessibility hook
└── utils/
    ├── animations.js           # Animation configuration constants
    └── classNames.js           # className utility functions
```


## Design System Tokens

### Color System

**Implementation:** Extend Tailwind config with design system colors

```javascript
// tailwind.config.js extensions
colors: {
  primary: {
    DEFAULT: '#2563eb',
    dark: '#1e40af',
    light: '#3b82f6',
    lighter: '#60a5fa',
  },
  secondary: {
    DEFAULT: '#7c3aed',
    teal: '#0d9488',
  },
  accent: {
    orange: '#f59e0b',
  },
  status: {
    success: '#10b981',
    error: '#ef4444',
    warning: '#f59e0b',
    info: '#3b82f6',
  },
  neutral: {
    bg: '#0f172a',
    card: '#1e293b',
    border: '#334155',
    text: '#f1f5f9',
    'text-secondary': '#94a3b8',
    'text-muted': '#64748b',
  },
}
```

**Gradients:** Defined as CSS custom properties

```css
:root {
  --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  --gradient-3: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  --gradient-4: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}
```

### Typography System

**Font Configuration:**

```javascript
// tailwind.config.js
fontFamily: {
  sans: ['Inter', 'system-ui', 'sans-serif'],
  mono: ['Fira Code', 'Consolas', 'monospace'],
},
fontSize: {
  'display': ['3.5rem', { lineHeight: '1.1', fontWeight: '700' }],
  'h1': ['2.5rem', { lineHeight: '1.2', fontWeight: '700' }],
  'h2': ['2rem', { lineHeight: '1.3', fontWeight: '600' }],
  'h3': ['1.5rem', { lineHeight: '1.4', fontWeight: '600' }],
  'body-lg': ['1.125rem', { lineHeight: '1.6', fontWeight: '400' }],
  'body': ['1rem', { lineHeight: '1.5', fontWeight: '400' }],
  'body-sm': ['0.875rem', { lineHeight: '1.5', fontWeight: '400' }],
  'caption': ['0.75rem', { lineHeight: '1.4', fontWeight: '400' }],
}
```

### Spacing and Layout

**Spacing Scale:**

```javascript
spacing: {
  'xs': '0.25rem',   // 4px
  'sm': '0.5rem',    // 8px
  'md': '1rem',      // 16px
  'lg': '1.5rem',    // 24px
  'xl': '2rem',      // 32px
  '2xl': '3rem',     // 48px
  '3xl': '4rem',     // 64px
}
```

**Border Radius:**

```javascript
borderRadius: {
  'sm': '0.375rem',  // 6px
  'md': '0.5rem',    // 8px
  'lg': '0.75rem',   // 12px
  'xl': '1rem',      // 16px
  'full': '9999px',
}
```

**Shadows:**

```javascript
boxShadow: {
  'sm': '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  'md': '0 4px 6px -1px rgb(0 0 0 / 0.1)',
  'lg': '0 10px 15px -3px rgb(0 0 0 / 0.1)',
  'xl': '0 20px 25px -5px rgb(0 0 0 / 0.1)',
  'glow': '0 0 20px rgba(37, 99, 235, 0.4)',
}
```


## Animation System

### Animation Timing and Easing

**Duration Constants:**

```javascript
// src/utils/animations.js
export const ANIMATION_DURATION = {
  fast: 100,      // Button clicks, quick feedback
  normal: 200,    // Standard transitions
  slow: 300,      // Page transitions
  chart: 800,     // Data visualization
  countUp: 1000,  // Number animations
};

export const EASING = {
  easeOut: 'cubic-bezier(0.16, 1, 0.3, 1)',
  easeIn: 'cubic-bezier(0.7, 0, 0.84, 0)',
  easeInOut: 'cubic-bezier(0.65, 0, 0.35, 1)',
  spring: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
};
```

### Framer Motion Variants

**Page Transitions:**

```javascript
export const pageVariants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
};

export const pageTransition = {
  duration: 0.3,
  ease: 'easeInOut',
};
```

**Modal Animations:**

```javascript
export const modalVariants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.9 },
};

export const backdropVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 },
};
```

**Stagger Children:**

```javascript
export const staggerContainer = {
  animate: {
    transition: {
      staggerChildren: 0.1,
    },
  },
};

export const staggerItem = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
};
```

### CSS Animations

**Keyframe Definitions:**

```css
/* src/styles/animations.css */

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.4); }
  50% { box-shadow: 0 0 20px 10px rgba(37, 99, 235, 0); }
}

@keyframes draw-checkmark {
  0% { stroke-dashoffset: 100; }
  100% { stroke-dashoffset: 0; }
}

@keyframes slide-in-right {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}

@keyframes count-up {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
```

### Performance Optimization

**Hardware Acceleration:**

```css
.will-animate {
  will-change: transform, opacity;
}

.gpu-accelerated {
  transform: translateZ(0);
  backface-visibility: hidden;
}
```

**Reduced Motion Support:**

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```


## Component Design Specifications

### Button Component

**Variants and States:**

```jsx
// src/components/ui/Button.jsx
const Button = ({ 
  variant = 'primary', 
  size = 'md', 
  loading = false, 
  icon, 
  children,
  ...props 
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200';
  
  const variants = {
    primary: 'bg-primary text-white hover:bg-primary-dark hover:scale-105 active:scale-95',
    secondary: 'border-2 border-primary text-primary hover:bg-primary hover:text-white',
    ghost: 'text-primary hover:bg-primary/10',
    danger: 'bg-status-error text-white hover:bg-red-600',
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-body-sm',
    md: 'px-4 py-2 text-body',
    lg: 'px-6 py-3 text-body-lg',
  };
  
  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className={clsx(baseClasses, variants[variant], sizes[size])}
      disabled={loading}
      {...props}
    >
      {loading && <Spinner className="mr-2" />}
      {icon && <span className="mr-2">{icon}</span>}
      {children}
    </motion.button>
  );
};
```

### Card Component

**Hover Effects and Variants:**

```jsx
// src/components/ui/Card.jsx
const Card = ({ 
  children, 
  hoverable = false, 
  gradient = false,
  className,
  ...props 
}) => {
  return (
    <motion.div
      whileHover={hoverable ? { y: -4, boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)' } : {}}
      transition={{ duration: 0.2 }}
      className={clsx(
        'bg-neutral-card rounded-lg p-6 border border-neutral-border',
        gradient && 'border-2 border-transparent bg-gradient-to-br from-primary/20 to-secondary/20',
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
};
```

### Input Component

**Floating Labels and Validation:**

```jsx
// src/components/ui/Input.jsx
const Input = ({ 
  label, 
  error, 
  success, 
  icon, 
  type = 'text',
  ...props 
}) => {
  const [focused, setFocused] = useState(false);
  const [hasValue, setHasValue] = useState(false);
  
  return (
    <div className="relative">
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-neutral-text-muted">
            {icon}
          </div>
        )}
        <input
          type={type}
          className={clsx(
            'w-full px-4 py-3 bg-neutral-card border-2 rounded-lg',
            'transition-all duration-200',
            'focus:outline-none focus:ring-2 focus:ring-primary/50',
            icon && 'pl-10',
            error && 'border-status-error',
            success && 'border-status-success',
            !error && !success && 'border-neutral-border focus:border-primary'
          )}
          onFocus={() => setFocused(true)}
          onBlur={(e) => {
            setFocused(false);
            setHasValue(e.target.value !== '');
          }}
          {...props}
        />
        <label
          className={clsx(
            'absolute left-4 transition-all duration-200 pointer-events-none',
            focused || hasValue
              ? 'top-0 -translate-y-1/2 text-xs bg-neutral-card px-1 text-primary'
              : 'top-1/2 -translate-y-1/2 text-body text-neutral-text-muted'
          )}
        >
          {label}
        </label>
        {success && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-status-success"
          >
            <CheckIcon />
          </motion.div>
        )}
      </div>
      {error && (
        <motion.p
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0, x: [0, -10, 10, -10, 10, 0] }}
          transition={{ x: { duration: 0.4 } }}
          className="mt-1 text-body-sm text-status-error"
        >
          {error}
        </motion.p>
      )}
    </div>
  );
};
```

### Toast Notification Component

**Implementation with react-hot-toast:**

```jsx
// src/components/ui/Toast.jsx
import toast, { Toaster } from 'react-hot-toast';

export const ToastContainer = () => (
  <Toaster
    position="top-right"
    toastOptions={{
      duration: 5000,
      style: {
        background: '#1e293b',
        color: '#f1f5f9',
        borderRadius: '0.5rem',
        padding: '1rem',
      },
      success: {
        iconTheme: {
          primary: '#10b981',
          secondary: '#fff',
        },
      },
      error: {
        iconTheme: {
          primary: '#ef4444',
          secondary: '#fff',
        },
      },
    }}
  />
);

export const showToast = {
  success: (message) => toast.success(message),
  error: (message) => toast.error(message),
  warning: (message) => toast(message, { icon: '⚠️' }),
  info: (message) => toast(message, { icon: 'ℹ️' }),
};
```

### Modal Component

**Accessible Modal with Animations:**

```jsx
// src/components/ui/Modal.jsx
import { Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';

const Modal = ({ isOpen, onClose, title, children, size = 'md' }) => {
  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  };
  
  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={onClose}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-200"
              enterFrom="opacity-0 scale-90"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-90"
            >
              <Dialog.Panel className={clsx(
                'w-full transform overflow-hidden rounded-lg',
                'bg-neutral-card p-6 shadow-xl transition-all',
                sizes[size]
              )}>
                <Dialog.Title className="text-h3 font-semibold text-neutral-text mb-4">
                  {title}
                </Dialog.Title>
                {children}
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};
```


### Loading States

**Skeleton Screen Component:**

```jsx
// src/components/ui/Skeleton.jsx
const Skeleton = ({ className, variant = 'text' }) => {
  const variants = {
    text: 'h-4 w-full',
    title: 'h-8 w-3/4',
    avatar: 'h-12 w-12 rounded-full',
    card: 'h-32 w-full',
  };
  
  return (
    <div className={clsx(
      'bg-neutral-border rounded animate-pulse relative overflow-hidden',
      variants[variant],
      className
    )}>
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-shimmer" />
    </div>
  );
};

// Usage in components
const DashboardSkeleton = () => (
  <div className="space-y-4">
    <Skeleton variant="title" />
    <div className="grid grid-cols-3 gap-4">
      <Skeleton variant="card" />
      <Skeleton variant="card" />
      <Skeleton variant="card" />
    </div>
  </div>
);
```

**Button Loading State:**

```jsx
const LoadingButton = ({ loading, children, ...props }) => (
  <Button {...props} disabled={loading}>
    {loading && (
      <motion.div
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        className="mr-2"
      >
        <Loader2Icon className="w-4 h-4" />
      </motion.div>
    )}
    {children}
  </Button>
);
```

### Progress Indicators

**Progress Bar Component:**

```jsx
// src/components/ui/ProgressBar.jsx
const ProgressBar = ({ value, max = 100, color = 'primary', showLabel = false }) => {
  const percentage = (value / max) * 100;
  
  return (
    <div className="w-full">
      <div className="flex justify-between mb-1">
        {showLabel && (
          <span className="text-body-sm text-neutral-text-secondary">
            {Math.round(percentage)}%
          </span>
        )}
      </div>
      <div className="w-full bg-neutral-border rounded-full h-2 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className={clsx(
            'h-full rounded-full',
            color === 'primary' && 'bg-gradient-to-r from-primary to-primary-light',
            color === 'success' && 'bg-status-success',
            color === 'warning' && 'bg-status-warning',
            color === 'error' && 'bg-status-error'
          )}
        />
      </div>
    </div>
  );
};
```

**Confidence Score Display:**

```jsx
const ConfidenceScore = ({ score }) => {
  const getColor = (score) => {
    if (score >= 90) return 'success';
    if (score >= 50) return 'warning';
    return 'error';
  };
  
  return (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-body-sm text-neutral-text-secondary">Confidence Score</span>
        <motion.span
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-h3 font-bold"
        >
          {score}
        </motion.span>
      </div>
      <ProgressBar value={score} color={getColor(score)} />
    </div>
  );
};
```


## Page-Specific Designs

### Enhanced Login Page

**Layout Structure:**

```jsx
// src/components/auth/Login.jsx (enhanced)
const EnhancedLogin = () => {
  return (
    <div className="min-h-screen flex">
      {/* Left Side - Branding */}
      <motion.div
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary via-secondary to-primary-dark relative overflow-hidden"
      >
        <div className="absolute inset-0 opacity-20">
          <FloatingSecurityIcons />
        </div>
        <div className="relative z-10 flex flex-col justify-center px-12">
          <h1 className="text-display text-white font-bold mb-4">
            Zero Trust Security
          </h1>
          <p className="text-body-lg text-white/80">
            Continuous verification for educational institutions
          </p>
        </div>
      </motion.div>
      
      {/* Right Side - Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-neutral-bg">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="w-full max-w-md"
        >
          <Card className="backdrop-blur-lg bg-neutral-card/80 shadow-xl">
            <h2 className="text-h2 font-bold text-neutral-text mb-6">
              Welcome Back
            </h2>
            <LoginForm />
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

const FloatingSecurityIcons = () => {
  const icons = [ShieldIcon, LockIcon, KeyIcon, FingerprintIcon];
  
  return (
    <div className="absolute inset-0">
      {icons.map((Icon, i) => (
        <motion.div
          key={i}
          animate={{
            y: [0, -20, 0],
            x: [0, 10, 0],
            rotate: [0, 5, 0],
          }}
          transition={{
            duration: 3 + i,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute"
          style={{
            top: `${20 + i * 20}%`,
            left: `${10 + i * 15}%`,
          }}
        >
          <Icon className="w-16 h-16 text-white" />
        </motion.div>
      ))}
    </div>
  );
};
```

### Enhanced Dashboard

**Stats Cards with Count-Up Animation:**

```jsx
// src/components/dashboards/StatsCard.jsx
const StatsCard = ({ title, value, icon, trend, color = 'primary' }) => {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const duration = 1000;
    const steps = 60;
    const increment = value / steps;
    let current = 0;
    
    const timer = setInterval(() => {
      current += increment;
      if (current >= value) {
        setCount(value);
        clearInterval(timer);
      } else {
        setCount(Math.floor(current));
      }
    }, duration / steps);
    
    return () => clearInterval(timer);
  }, [value]);
  
  return (
    <Card hoverable className="relative overflow-hidden">
      <div className={clsx(
        'absolute top-0 right-0 w-24 h-24 rounded-full blur-3xl opacity-20',
        `bg-${color}`
      )} />
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <span className="text-body-sm text-neutral-text-secondary">{title}</span>
          <div className={clsx(
            'p-2 rounded-lg',
            `bg-${color}/10`
          )}>
            {icon}
          </div>
        </div>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-h1 font-bold text-neutral-text mb-2"
        >
          {count}
        </motion.div>
        
        {trend && (
          <div className="flex items-center text-body-sm">
            {trend > 0 ? (
              <TrendingUpIcon className="w-4 h-4 text-status-success mr-1" />
            ) : (
              <TrendingDownIcon className="w-4 h-4 text-status-error mr-1" />
            )}
            <span className={trend > 0 ? 'text-status-success' : 'text-status-error'}>
              {Math.abs(trend)}%
            </span>
            <span className="text-neutral-text-muted ml-1">vs last month</span>
          </div>
        )}
      </div>
    </Card>
  );
};
```

### Enhanced Access Request Form

**Multi-Step Form with Progress:**

```jsx
// src/components/access/EnhancedRequestForm.jsx
const EnhancedRequestForm = () => {
  const [step, setStep] = useState(1);
  const totalSteps = 3;
  
  return (
    <div className="max-w-2xl mx-auto">
      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex justify-between mb-2">
          {[1, 2, 3].map((s) => (
            <div
              key={s}
              className={clsx(
                'flex items-center justify-center w-10 h-10 rounded-full',
                'transition-all duration-300',
                s <= step
                  ? 'bg-primary text-white scale-110'
                  : 'bg-neutral-border text-neutral-text-muted'
              )}
            >
              {s < step ? <CheckIcon /> : s}
            </div>
          ))}
        </div>
        <div className="relative h-2 bg-neutral-border rounded-full overflow-hidden">
          <motion.div
            initial={{ width: '0%' }}
            animate={{ width: `${(step / totalSteps) * 100}%` }}
            className="absolute h-full bg-gradient-to-r from-primary to-primary-light"
          />
        </div>
      </div>
      
      {/* Step Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={step}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
        >
          {step === 1 && <ResourceSelection />}
          {step === 2 && <IntentDescription />}
          {step === 3 && <ReviewSubmit />}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

const ResourceSelection = () => (
  <div className="grid grid-cols-2 gap-4">
    {resources.map((resource) => (
      <motion.div
        key={resource.id}
        whileHover={{ rotateY: 5, scale: 1.05 }}
        className="cursor-pointer"
      >
        <Card className="text-center p-6">
          <div className="text-4xl mb-3">{resource.icon}</div>
          <h3 className="text-h3 font-semibold mb-2">{resource.name}</h3>
          <p className="text-body-sm text-neutral-text-secondary">
            {resource.description}
          </p>
        </Card>
      </motion.div>
    ))}
  </div>
);
```


### Enhanced Table Component

**Sortable, Filterable Table with Animations:**

```jsx
// src/components/ui/Table.jsx
const Table = ({ columns, data, sortable = true, expandable = false }) => {
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [expandedRows, setExpandedRows] = useState(new Set());
  
  const handleSort = (key) => {
    setSortConfig({
      key,
      direction: sortConfig.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc',
    });
  };
  
  return (
    <div className="overflow-x-auto rounded-lg border border-neutral-border">
      <table className="w-full">
        <thead className="bg-neutral-card border-b border-neutral-border sticky top-0">
          <tr>
            {columns.map((column) => (
              <th
                key={column.key}
                className="px-6 py-3 text-left text-body-sm font-semibold text-neutral-text-secondary"
              >
                {sortable && column.sortable !== false ? (
                  <button
                    onClick={() => handleSort(column.key)}
                    className="flex items-center gap-2 hover:text-primary transition-colors"
                  >
                    {column.label}
                    <motion.div
                      animate={{
                        rotate: sortConfig.key === column.key && sortConfig.direction === 'desc' ? 180 : 0,
                      }}
                    >
                      <ChevronUpIcon className="w-4 h-4" />
                    </motion.div>
                  </button>
                ) : (
                  column.label
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          <AnimatePresence>
            {data.map((row, index) => (
              <TableRow
                key={row.id}
                row={row}
                columns={columns}
                index={index}
                expandable={expandable}
                expanded={expandedRows.has(row.id)}
                onToggleExpand={() => {
                  const newExpanded = new Set(expandedRows);
                  if (newExpanded.has(row.id)) {
                    newExpanded.delete(row.id);
                  } else {
                    newExpanded.add(row.id);
                  }
                  setExpandedRows(newExpanded);
                }}
              />
            ))}
          </AnimatePresence>
        </tbody>
      </table>
    </div>
  );
};

const TableRow = ({ row, columns, index, expandable, expanded, onToggleExpand }) => (
  <>
    <motion.tr
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ delay: index * 0.05 }}
      className={clsx(
        'border-b border-neutral-border transition-colors',
        index % 2 === 0 ? 'bg-neutral-bg' : 'bg-neutral-card',
        'hover:bg-primary/5'
      )}
    >
      {columns.map((column) => (
        <td key={column.key} className="px-6 py-4 text-body text-neutral-text">
          {column.render ? column.render(row[column.key], row) : row[column.key]}
        </td>
      ))}
      {expandable && (
        <td className="px-6 py-4">
          <button onClick={onToggleExpand}>
            <motion.div
              animate={{ rotate: expanded ? 180 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <ChevronDownIcon className="w-5 h-5" />
            </motion.div>
          </button>
        </td>
      )}
    </motion.tr>
    {expandable && expanded && (
      <motion.tr
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: 'auto' }}
        exit={{ opacity: 0, height: 0 }}
      >
        <td colSpan={columns.length + 1} className="px-6 py-4 bg-neutral-card/50">
          {row.expandedContent}
        </td>
      </motion.tr>
    )}
  </>
);
```

### Status Badge Component

```jsx
// src/components/ui/Badge.jsx
const Badge = ({ status, children, icon, removable, onRemove }) => {
  const statusStyles = {
    granted: 'bg-status-success/10 text-status-success border-status-success',
    denied: 'bg-status-error/10 text-status-error border-status-error',
    pending: 'bg-status-warning/10 text-status-warning border-status-warning',
    info: 'bg-status-info/10 text-status-info border-status-info',
  };
  
  const statusIcons = {
    granted: <CheckCircleIcon className="w-4 h-4" />,
    denied: <XCircleIcon className="w-4 h-4" />,
    pending: <ClockIcon className="w-4 h-4" />,
    info: <InfoIcon className="w-4 h-4" />,
  };
  
  return (
    <motion.span
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className={clsx(
        'inline-flex items-center gap-1.5 px-3 py-1 rounded-full',
        'text-body-sm font-medium border',
        statusStyles[status]
      )}
    >
      {icon || statusIcons[status]}
      {children}
      {removable && (
        <button
          onClick={onRemove}
          className="ml-1 hover:scale-110 transition-transform"
        >
          <XIcon className="w-3 h-3" />
        </button>
      )}
    </motion.span>
  );
};
```


## Responsive Design Strategy

### Breakpoint System

**Tailwind Configuration:**

```javascript
screens: {
  'mobile': '320px',
  'tablet': '640px',
  'desktop': '1024px',
  'wide': '1280px',
}
```

### Mobile Adaptations

**Collapsible Sidebar:**

```jsx
// src/components/layouts/Sidebar.jsx
const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const isMobile = useMediaQuery('(max-width: 1023px)');
  
  return (
    <>
      {/* Mobile Hamburger */}
      {isMobile && (
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="fixed top-4 left-4 z-50 p-2 bg-neutral-card rounded-lg"
        >
          <MenuIcon className="w-6 h-6" />
        </button>
      )}
      
      {/* Sidebar */}
      <AnimatePresence>
        {(!isMobile || isOpen) && (
          <>
            {/* Backdrop for mobile */}
            {isMobile && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                onClick={() => setIsOpen(false)}
                className="fixed inset-0 bg-black/50 z-40"
              />
            )}
            
            {/* Sidebar content */}
            <motion.aside
              initial={isMobile ? { x: -300 } : false}
              animate={{ x: 0 }}
              exit={isMobile ? { x: -300 } : {}}
              transition={{ type: 'spring', damping: 25 }}
              className={clsx(
                'bg-neutral-card border-r border-neutral-border',
                isMobile ? 'fixed left-0 top-0 bottom-0 w-64 z-40' : 'w-64'
              )}
            >
              <SidebarContent />
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
};
```

**Bottom Navigation (Mobile):**

```jsx
// src/components/layouts/BottomNav.jsx
const BottomNav = () => {
  const isMobile = useMediaQuery('(max-width: 639px)');
  
  if (!isMobile) return null;
  
  const navItems = [
    { icon: HomeIcon, label: 'Home', path: '/dashboard' },
    { icon: FileTextIcon, label: 'Requests', path: '/requests' },
    { icon: BellIcon, label: 'Alerts', path: '/notifications' },
    { icon: UserIcon, label: 'Profile', path: '/profile' },
  ];
  
  return (
    <motion.nav
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      className="fixed bottom-0 left-0 right-0 bg-neutral-card border-t border-neutral-border z-40"
    >
      <div className="flex justify-around items-center h-16">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className="flex flex-col items-center justify-center flex-1 h-full"
          >
            <item.icon className="w-6 h-6 mb-1" />
            <span className="text-caption">{item.label}</span>
          </Link>
        ))}
      </div>
    </motion.nav>
  );
};
```

### Responsive Grid Layouts

```jsx
// Responsive card grid
<div className="grid grid-cols-1 tablet:grid-cols-2 desktop:grid-cols-3 gap-4">
  {items.map(item => <Card key={item.id}>{item.content}</Card>)}
</div>

// Responsive stats layout
<div className="grid grid-cols-2 tablet:grid-cols-4 gap-4">
  {stats.map(stat => <StatsCard key={stat.id} {...stat} />)}
</div>
```


## Dark Mode Implementation

### Theme Context

```jsx
// src/contexts/ThemeContext.jsx
const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    // Check localStorage
    const saved = localStorage.getItem('theme');
    if (saved) return saved;
    
    // Check system preference
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    
    return 'light';
  });
  
  useEffect(() => {
    localStorage.setItem('theme', theme);
    document.documentElement.classList.toggle('dark', theme === 'dark');
  }, [theme]);
  
  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };
  
  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
```

### Dark Mode Colors

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        neutral: {
          bg: {
            DEFAULT: '#0f172a',
            light: '#f8fafc',
          },
          card: {
            DEFAULT: '#1e293b',
            light: '#ffffff',
          },
          border: {
            DEFAULT: '#334155',
            light: '#e2e8f0',
          },
          text: {
            DEFAULT: '#f1f5f9',
            light: '#0f172a',
          },
        },
      },
    },
  },
};
```

### Theme Toggle Component

```jsx
// src/components/ui/ThemeToggle.jsx
const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <motion.button
      whileTap={{ scale: 0.95 }}
      onClick={toggleTheme}
      className="p-2 rounded-lg bg-neutral-card hover:bg-neutral-border transition-colors"
      aria-label="Toggle theme"
    >
      <AnimatePresence mode="wait">
        <motion.div
          key={theme}
          initial={{ rotate: -90, opacity: 0 }}
          animate={{ rotate: 0, opacity: 1 }}
          exit={{ rotate: 90, opacity: 0 }}
          transition={{ duration: 0.2 }}
        >
          {theme === 'dark' ? (
            <SunIcon className="w-5 h-5" />
          ) : (
            <MoonIcon className="w-5 h-5" />
          )}
        </motion.div>
      </AnimatePresence>
    </motion.button>
  );
};
```

## Accessibility Implementation

### Custom Hooks

**useReducedMotion Hook:**

```jsx
// src/hooks/useReducedMotion.js
export const useReducedMotion = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);
    
    const handler = (e) => setPrefersReducedMotion(e.matches);
    mediaQuery.addEventListener('change', handler);
    
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);
  
  return prefersReducedMotion;
};
```

**useMediaQuery Hook:**

```jsx
// src/hooks/useMediaQuery.js
export const useMediaQuery = (query) => {
  const [matches, setMatches] = useState(false);
  
  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    setMatches(mediaQuery.matches);
    
    const handler = (e) => setMatches(e.matches);
    mediaQuery.addEventListener('change', handler);
    
    return () => mediaQuery.removeEventListener('change', handler);
  }, [query]);
  
  return matches;
};
```

### Focus Management

```jsx
// src/components/ui/FocusableCard.jsx
const FocusableCard = ({ children, onClick, ...props }) => {
  return (
    <div
      role="button"
      tabIndex={0}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick?.(e);
        }
      }}
      className={clsx(
        'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
        'focus:ring-offset-neutral-bg rounded-lg'
      )}
      {...props}
    >
      {children}
    </div>
  );
};
```

### Skip to Content Link

```jsx
// src/components/layouts/Layout.jsx
const Layout = ({ children }) => {
  return (
    <>
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-white focus:rounded-lg"
      >
        Skip to main content
      </a>
      
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 flex flex-col">
          <Navbar />
          <main id="main-content" className="flex-1 p-6">
            {children}
          </main>
        </div>
      </div>
    </>
  );
};
```


## Chart and Data Visualization Design

### Recharts Configuration

**Animated Line Chart:**

```jsx
// src/components/charts/AnimatedLineChart.jsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const AnimatedLineChart = ({ data, dataKey, color = '#2563eb' }) => {
  const [animationComplete, setAnimationComplete] = useState(false);
  
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <defs>
          <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.8}/>
            <stop offset="95%" stopColor={color} stopOpacity={0}/>
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis 
          dataKey="name" 
          stroke="#94a3b8"
          style={{ fontSize: '12px' }}
        />
        <YAxis 
          stroke="#94a3b8"
          style={{ fontSize: '12px' }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '8px',
            color: '#f1f5f9',
          }}
        />
        <Line
          type="monotone"
          dataKey={dataKey}
          stroke={color}
          strokeWidth={3}
          fill="url(#colorGradient)"
          animationDuration={800}
          animationEasing="ease-out"
          dot={{ fill: color, r: 4 }}
          activeDot={{ r: 6, fill: color }}
          onAnimationEnd={() => setAnimationComplete(true)}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
```

**Animated Bar Chart:**

```jsx
// src/components/charts/AnimatedBarChart.jsx
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const AnimatedBarChart = ({ data, dataKey, color = '#2563eb' }) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
        <XAxis dataKey="name" stroke="#94a3b8" />
        <YAxis stroke="#94a3b8" />
        <Tooltip
          contentStyle={{
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '8px',
          }}
        />
        <Bar
          dataKey={dataKey}
          fill={color}
          radius={[8, 8, 0, 0]}
          animationDuration={500}
          animationBegin={0}
        />
      </BarChart>
    </ResponsiveContainer>
  );
};
```

**Donut Chart with Animation:**

```jsx
// src/components/charts/DonutChart.jsx
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts';

const DonutChart = ({ data, colors }) => {
  const [activeIndex, setActiveIndex] = useState(null);
  
  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={80}
          paddingAngle={5}
          dataKey="value"
          animationDuration={800}
          animationBegin={0}
          onMouseEnter={(_, index) => setActiveIndex(index)}
          onMouseLeave={() => setActiveIndex(null)}
        >
          {data.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={colors[index % colors.length]}
              style={{
                filter: activeIndex === index ? 'brightness(1.2)' : 'brightness(1)',
                transition: 'filter 0.2s',
              }}
            />
          ))}
        </Pie>
        <Legend
          verticalAlign="bottom"
          height={36}
          iconType="circle"
          formatter={(value) => (
            <span className="text-body-sm text-neutral-text-secondary">{value}</span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
};
```

## Performance Optimization

### Code Splitting

```jsx
// src/App.jsx
import { lazy, Suspense } from 'react';

const AdminDashboard = lazy(() => import('./components/dashboards/AdminDashboard'));
const Analytics = lazy(() => import('./components/admin/Analytics'));
const AuditLogs = lazy(() => import('./components/admin/AuditLogs'));

const App = () => {
  return (
    <Suspense fallback={<LoadingScreen />}>
      <Routes>
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/analytics" element={<Analytics />} />
        <Route path="/admin/logs" element={<AuditLogs />} />
      </Routes>
    </Suspense>
  );
};
```

### Image Optimization

```jsx
// src/components/ui/OptimizedImage.jsx
const OptimizedImage = ({ src, alt, className, ...props }) => {
  const [loaded, setLoaded] = useState(false);
  
  return (
    <div className={clsx('relative overflow-hidden', className)}>
      {!loaded && <Skeleton className="absolute inset-0" />}
      <img
        src={src}
        alt={alt}
        loading="lazy"
        onLoad={() => setLoaded(true)}
        className={clsx(
          'transition-opacity duration-300',
          loaded ? 'opacity-100' : 'opacity-0'
        )}
        {...props}
      />
    </div>
  );
};
```

### Animation Performance

```jsx
// Use transform and opacity for animations
const performantAnimation = {
  initial: { opacity: 0, transform: 'translateY(20px)' },
  animate: { opacity: 1, transform: 'translateY(0)' },
  // Avoid animating: top, left, width, height, margin, padding
};

// Apply will-change for frequently animated elements
<motion.div
  style={{ willChange: 'transform, opacity' }}
  animate={{ x: 100 }}
/>
```

## Testing Strategy

### Component Testing

```jsx
// src/components/ui/Button.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
  
  it('applies hover animation', async () => {
    render(<Button>Hover me</Button>);
    const button = screen.getByText('Hover me');
    
    fireEvent.mouseEnter(button);
    // Test that scale transform is applied
    expect(button).toHaveStyle({ transform: 'scale(1.05)' });
  });
  
  it('shows loading state', () => {
    render(<Button loading>Loading</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
    expect(screen.getByTestId('spinner')).toBeInTheDocument();
  });
});
```

### Accessibility Testing

```jsx
// src/components/ui/Modal.test.jsx
import { render, screen } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Modal Accessibility', () => {
  it('should not have accessibility violations', async () => {
    const { container } = render(
      <Modal isOpen={true} title="Test Modal">
        <p>Modal content</p>
      </Modal>
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  it('traps focus within modal', () => {
    render(
      <Modal isOpen={true} title="Test Modal">
        <button>Button 1</button>
        <button>Button 2</button>
      </Modal>
    );
    
    // Test focus trap implementation
  });
});
```

## Implementation Phases

### Phase 1: Foundation (Week 1)
- Set up design tokens in Tailwind config
- Install animation libraries (framer-motion, react-hot-toast, lucide-react)
- Create base UI components (Button, Card, Input, Badge)
- Implement animation utilities and hooks
- Set up theme context for dark mode

### Phase 2: Core Components (Week 2)
- Enhance authentication pages with animations
- Implement toast notification system
- Create loading states and skeleton screens
- Build modal and drawer components
- Implement responsive sidebar and navigation

### Phase 3: Data Display (Week 3)
- Enhance table component with sorting and filtering
- Implement animated charts (line, bar, donut)
- Create stats cards with count-up animations
- Build progress indicators and confidence score displays
- Implement expandable rows and details views

### Phase 4: Page Enhancements (Week 4)
- Enhance dashboard layouts with animations
- Implement multi-step access request form
- Enhance request history with filters and animations
- Build admin analytics dashboard
- Implement audit log viewer with animations

### Phase 5: Polish and Optimization (Week 5)
- Implement dark mode throughout
- Add accessibility features (focus management, ARIA labels)
- Optimize animation performance
- Add responsive design refinements
- Conduct accessibility and performance testing

## Error Handling

### Animation Error Boundaries

```jsx
// src/components/ErrorBoundary.jsx
class AnimationErrorBoundary extends React.Component {
  state = { hasError: false };
  
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('Animation error:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      // Render without animations
      return <div className="no-animations">{this.props.children}</div>;
    }
    
    return this.props.children;
  }
}
```

## Documentation

### Component Documentation

Each component should include:
- Props interface with TypeScript or JSDoc
- Usage examples
- Accessibility notes
- Animation specifications

```jsx
/**
 * Button component with hover and click animations
 * 
 * @param {Object} props
 * @param {'primary'|'secondary'|'ghost'|'danger'} props.variant - Button style variant
 * @param {'sm'|'md'|'lg'} props.size - Button size
 * @param {boolean} props.loading - Show loading spinner
 * @param {ReactNode} props.icon - Optional icon element
 * @param {ReactNode} props.children - Button content
 * 
 * @example
 * <Button variant="primary" size="md" onClick={handleClick}>
 *   Submit
 * </Button>
 */
```
