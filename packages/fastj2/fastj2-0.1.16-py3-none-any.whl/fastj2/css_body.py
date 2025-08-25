base = """
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: var(--font-family-primary);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-normal);
  line-height: 1.6;
  margin: 0;
  min-height: 100vh;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body.no-scroll {
  overflow: hidden;
}

html {
  scroll-behavior: smooth;
}

/* Focus styles for accessibility */
*:focus {
  outline: 2px solid var(--primary-blue);
  outline-offset: 2px;
}

button:focus,
input:focus,
select:focus,
textarea:focus {
  outline: 2px solid var(--primary-blue);
  outline-offset: 2px;
}
"""

typography = """
h1, h2, h3, h4, h5, h6 {
  margin: 0;
  font-weight: var(--font-weight-bold);
  background: var(--gradient-text);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
}

h1 { font-size: var(--font-size-5xl); }
h2 { font-size: var(--font-size-4xl); }
h3 { font-size: var(--font-size-3xl); }
h4 { font-size: var(--font-size-2xl); }
h5 { font-size: var(--font-size-xl); }
h6 { font-size: var(--font-size-lg); }

p {
  margin: 0;
  color: #6b7280;
  line-height: 1.5;
}

a {
  color: var(--primary-blue);
  text-decoration: none;
  font-weight: var(--font-weight-semibold);
  position: relative;
  transition: all var(--duration-normal) var(--ease-out);
}

a::before {
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  bottom: -2px;
  left: 50%;
  background: var(--gradient-primary-alt);
  transition: all var(--duration-normal) var(--ease-out);
  transform: translateX(-50%);
}

a:hover {
  color: #005a9e;
  transform: translateY(-1px);
}

a:hover::before {
  width: 100%;
}

.text-gradient {
  background: var(--gradient-text);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.text-gradient-primary {
  background: var(--gradient-primary);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
"""