# Pre-Delivery Quality Checklist

Run through this checklist before delivering any UI implementation.

## 1. Visual Quality

- [ ] **Icons**: Using SVG icons (Heroicons, Lucide, Simple Icons) - NO emoji
- [ ] **Brand logos**: Real company logos, not placeholders
- [ ] **Hover states**: Every interactive element has a hover style
- [ ] **Transitions**: 150-300ms duration, ease-out timing
- [ ] **Spacing**: Consistent padding/margins using design system

## 2. Interaction

- [ ] **Cursor pointer**: All clickable elements have `cursor-pointer`
- [ ] **Focus rings**: 3-4px visible focus indicators
- [ ] **Touch targets**: Minimum 44x44px on mobile
- [ ] **Loading states**: Skeleton or spinner for async content
- [ ] **Error states**: Clear error messaging for forms

## 3. Light Mode

- [ ] **Contrast ratio**: Text meets 4.5:1 minimum (WCAG AA)
- [ ] **Glass cards**: Using `bg-white/80` or higher opacity
- [ ] **Borders**: Visible borders on light backgrounds
- [ ] **Shadows**: Subtle, not overly dramatic

## 4. Dark Mode

- [ ] **Contrast ratio**: Text meets 4.5:1 on dark backgrounds
- [ ] **Glass cards**: Using `bg-black/60` or similar
- [ ] **Borders**: Using `border-white/10` or similar
- [ ] **No pure black**: Prefer `bg-gray-900` or `bg-slate-900`

## 5. Layout

- [ ] **Floating elements**: Navbar/footer have spacing (not edge-to-edge)
- [ ] **Responsive**: Tested at 320px, 768px, 1024px, 1440px
- [ ] **Max-width**: Content has sensible maximum width
- [ ] **Grid consistency**: Using consistent column system

## 6. Accessibility

- [ ] **Alt text**: All images have descriptive alt text
- [ ] **Form labels**: Every input has a visible label
- [ ] **ARIA labels**: Interactive elements have accessible names
- [ ] **Keyboard navigation**: Tab order is logical
- [ ] **Skip links**: "Skip to content" for screen readers
- [ ] **Reduced motion**: Respects `prefers-reduced-motion`

## 7. Performance

- [ ] **Image optimization**: Using WebP/AVIF, proper sizing
- [ ] **Lazy loading**: Images below fold are lazy loaded
- [ ] **Font loading**: Using `font-display: swap`
- [ ] **Animation efficiency**: Using transform/opacity only

## Quick Fixes

### Missing cursor-pointer
```css
.interactive { @apply cursor-pointer; }
```

### Low contrast glass
```css
/* Light mode */
.glass { @apply bg-white/80 backdrop-blur-sm; }
/* Dark mode */
.glass { @apply bg-black/60 backdrop-blur-sm; }
```

### Unstable hover (avoid scale)
```css
/* Bad: causes layout shift */
.card:hover { transform: scale(1.05); }

/* Good: color/opacity only */
.card:hover { @apply bg-gray-50 transition-colors; }
```

### Floating navbar
```css
.navbar {
  @apply fixed top-4 left-4 right-4 rounded-xl;
}
```
