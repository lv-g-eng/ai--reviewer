declare module 'msw' {
  export function setupServer(...handlers: any[]): any;
  export const rest: any;
}
