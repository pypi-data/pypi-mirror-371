containers = """
/* Layout Containers */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--space-lg);
  position: relative;
  z-index: var(--z-content);
}

.container--sm {
  max-width: 640px;
}

.container--md {
  max-width: 768px;
}

.container--lg {
  max-width: 1024px;
}

.container--xl {
  max-width: 1280px;
}

/* Centering Layouts */
.centered-layout {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: var(--space-lg);
}

.centered-content {
  text-align: center;
  max-width: 500px;
  width: 100%;
}

/* Fullscreen Layout */
.fullscreen-layout {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Content Sections */
.content-section {
  margin-bottom: var(--space-3xl);
}

.content-section:last-child {
  margin-bottom: 0;
}
"""

grid = """
/* Grid System */
.grid {
  display: grid;
  gap: var(--space-lg);
}

.grid--sm {
  gap: var(--space-md);
}

.grid--lg {
  gap: var(--space-xl);
}

.grid--2 {
  grid-template-columns: repeat(2, 1fr);
}

.grid--3 {
  grid-template-columns: repeat(3, 1fr);
}

.grid--4 {
  grid-template-columns: repeat(4, 1fr);
}

.grid--auto {
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.grid--responsive {
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
}

/* Flex System */
.flex {
  display: flex;
}

.flex--column {
  flex-direction: column;
}

.flex--center {
  align-items: center;
  justify-content: center;
}

.flex--between {
  justify-content: space-between;
  align-items: center;
}

.flex--wrap {
  flex-wrap: wrap;
}

.flex--gap {
  gap: var(--space-md);
}

.flex--gap-sm {
  gap: var(--space-sm);
}

.flex--gap-lg {
  gap: var(--space-lg);
}

/* Media Queries */
@media (max-width: 768px) {
  .grid--2,
  .grid--3,
  .grid--4 {
    grid-template-columns: 1fr;
  }

  .flex--mobile-column {
    flex-direction: column;
  }
}
"""