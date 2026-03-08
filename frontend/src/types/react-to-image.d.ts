/**
 * Type declarations for react-to-image library
 */

declare module 'react-to-image' {
  export interface Options {
    backgroundColor?: string;
    filter?: (node: HTMLElement) => boolean;
    width?: number;
    height?: number;
    quality?: number;
    pixelRatio?: number;
    cacheBust?: boolean;
  }

  export function toPng(
    node: HTMLElement,
    options?: Options
  ): Promise<string>;

  export function toSvg(
    node: HTMLElement,
    options?: Options
  ): Promise<string>;

  export function toJpeg(
    node: HTMLElement,
    options?: Options
  ): Promise<string>;

  export function toBlob(
    node: HTMLElement,
    options?: Options
  ): Promise<Blob | null>;

  export function toCanvas(
    node: HTMLElement,
    options?: Options
  ): Promise<HTMLCanvasElement>;

  export function toPixelData(
    node: HTMLElement,
    options?: Options
  ): Promise<Uint8ClampedArray>;
}
