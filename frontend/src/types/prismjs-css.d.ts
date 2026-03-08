/**
 * Type declarations for prismjs CSS imports and language components
 *
 * Prism.js CSS files and language components are imported dynamically
 * for syntax highlighting themes and language support.
 * This declaration file tells TypeScript that these imports are valid.
 */

// CSS theme imports
declare module 'prismjs/themes/*.css' {
  const content: string;
  export default content;
}

declare module 'prismjs/themes/prism-tomorrow.css' {
  const content: string;
  export default content;
}

declare module 'prismjs/themes/prism.css' {
  const content: string;
  export default content;
}

declare module 'prismjs/themes/prism-dark.css' {
  const content: string;
  export default content;
}

declare module 'prismjs/themes/prism-funky.css' {
  const content: string;
  export default content;
}

declare module 'prismjs/themes/prism-okaidia.css' {
  const content: string;
  export default content;
}

declare module 'prismjs/themes/prism-solarizedlight.css' {
  const content: string;
  export default content;
}

declare module 'prismjs/themes/prism-twilight.css' {
  const content: string;
  export default content;
}

declare module 'prismjs/themes/prism-coy.css' {
  const content: string;
  export default content;
}

// Language component imports
declare module 'prismjs/components/prism-*' {
  const content: typeof import('prismjs');
  export default content;
}

declare module 'prismjs/components/prism-python' {
  const content: typeof import('prismjs');
  export default content;
}

declare module 'prismjs/components/prism-javascript' {
  const content: typeof import('prismjs');
  export default content;
}

declare module 'prismjs/components/prism-typescript' {
  const content: typeof import('prismjs');
  export default content;
}

declare module 'prismjs/components/prism-jsx' {
  const content: typeof import('prismjs');
  export default content;
}

declare module 'prismjs/components/prism-tsx' {
  const content: typeof import('prismjs');
  export default content;
}

declare module 'prismjs/components/prism-css' {
  const content: typeof import('prismjs');
  export default content;
}

declare module 'prismjs/components/prism-json' {
  const content: typeof import('prismjs');
  export default content;
}

declare module 'prismjs/components/prism-markdown' {
  const content: typeof import('prismjs');
  export default content;
}

declare module 'prismjs/components/prism-go' {
  const content: typeof import('prismjs');
  export default content;
}

declare module 'prismjs/components/prism-java' {
  const content: typeof import('prismjs');
  export default content;
}

declare module 'prismjs/components/prism-csharp' {
  const content: typeof import('prismjs');
  export default content;
}

declare module 'prismjs/components/prism-rust' {
  const content: typeof import('prismjs');
  export default content;
}

declare module 'prismjs/components/prism-bash' {
  const content: typeof import('prismjs');
  export default content;
}

declare module 'prismjs/components/prism-yaml' {
  const content: typeof import('prismjs');
  export default content;
}

declare module 'prismjs/components/prism-sql' {
  const content: typeof import('prismjs');
  export default content;
}
