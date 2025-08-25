css_vars = """
:root {
  /* Primary Brand Colors */
  --primary-blue: #0078d4;
  --primary-blue-dark: #106ebe;
  --primary-blue-light: #40e0ff;
  --accent-purple: #764ba2;
  --accent-purple-light: #667eea;

  /* Glassmorphism Colors */
  --glass-white: rgba(255, 255, 255, 0.95);
  --glass-white-soft: rgba(255, 255, 255, 0.85);
  --glass-white-subtle: rgba(255, 255, 255, 0.75);
  --glass-dark: rgba(31, 41, 55, 0.95);
  --glass-dark-soft: rgba(31, 41, 55, 0.85);

  /* Glass Borders */
  --glass-border: 1px solid rgba(255, 255, 255, 0.2);
  --glass-border-strong: 1px solid rgba(255, 255, 255, 0.3);
  --glass-border-subtle: 1px solid rgba(255, 255, 255, 0.1);
  --glass-border-dark: 1px solid rgba(255, 255, 255, 0.05);

  /* Gradients */
  --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-primary-alt: linear-gradient(135deg, #0078d4 0%, #005a9e 100%);
  --gradient-success: linear-gradient(135deg, #22c55e, #16a34a);
  --gradient-error: linear-gradient(135deg, #dc2626 0%, #991b1b 100%);
  --gradient-warning: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  --gradient-text: linear-gradient(135deg, #1f2937, #374151);

  /* Animated Gradients */
  --gradient-animated: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --gradient-size: 400% 400%;

  /* Shadows */
  --shadow-glass: 0 8px 32px rgba(31, 38, 135, 0.37);
  --shadow-glass-lg: 0 20px 40px rgba(0,0,0,0.1);
  --shadow-glass-xl: 0 25px 50px rgba(31, 38, 135, 0.3);
  --shadow-button: 0 8px 20px rgba(0, 120, 212, 0.3);
  --shadow-button-hover: 0 12px 30px rgba(0, 120, 212, 0.4);
  --shadow-success: 0 10px 25px rgba(34, 197, 94, 0.3);
  --shadow-error: 0 10px 25px rgba(220, 38, 38, 0.3);

  /* Typography */
  --font-family-primary: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-base: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;
  --font-size-2xl: 24px;
  --font-size-3xl: 30px;
  --font-size-4xl: 36px;
  --font-size-5xl: 48px;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;
  --space-2xl: 48px;
  --space-3xl: 64px;

  /* Border Radius */
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-2xl: 24px;
  --radius-full: 50%;

  /* Animation Timing */
  --duration-fast: 0.15s;
  --duration-normal: 0.3s;
  --duration-slow: 0.5s;
  --ease-out: cubic-bezier(0.25, 0.46, 0.45, 0.94);
  --ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
  --ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);

  /* Z-index Stack */
  --z-particles: 1;
  --z-content: 2;
  --z-overlay: 1000;
  --z-modal: 2000;
  --z-toast: 3000;
}
"""