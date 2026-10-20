// Inline SVG icons: no file to download, and they take the color of the text
// (currentColor). Always next to a text that says the same thing: decorative
// for a screen reader. Copied in index.html for the welcome screen. The
// width and height attributes keep them small if the CSS is missing.

type IconProps = { className?: string };

const STROKE = {
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 2,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
} as const;

/** The logo of public/favicon.svg: a road to the horizon under a sun. */
export function LogoMark({ className }: IconProps) {
  return (
    <svg className={className} width="64" height="64" viewBox="0 0 64 64" aria-hidden="true" focusable="false">
      <rect className="logo-ground" width="64" height="64" rx="14" />
      <path className="logo-road" d="M14 44h36M20 44l6-20h12l6 20" />
      <circle className="logo-sun" cx="32" cy="16" r="5" />
    </svg>
  );
}

export function CarIcon({ className }: IconProps) {
  return (
    <svg className={className} width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" focusable="false" {...STROKE}>
      <path d="M5 11l1.5-4.5A2 2 0 0 1 8.4 5h7.2a2 2 0 0 1 1.9 1.5L19 11" />
      <rect x="3" y="11" width="18" height="6" rx="2" />
      <path d="M6 17v2M18 17v2M7 14h.01M17 14h.01" />
    </svg>
  );
}

export function TicketIcon({ className }: IconProps) {
  return (
    <svg className={className} width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" focusable="false" {...STROKE}>
      <path d="M3 7a1 1 0 0 1 1-1h16a1 1 0 0 1 1 1v3a2 2 0 0 0 0 4v3a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-3a2 2 0 0 0 0-4z" />
      <path d="M15 6v2M15 11v2M15 16v2" />
    </svg>
  );
}

export function WheelchairIcon({ className }: IconProps) {
  return (
    <svg className={className} width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" focusable="false" {...STROKE}>
      <circle cx="11" cy="4" r="1.5" />
      <path d="M11 7v6h5l2.5 5" />
      <path d="M11 10h4" />
      <path d="M8 10.5a5 5 0 1 0 6.5 6.5" />
    </svg>
  );
}

export function PhoneIcon({ className }: IconProps) {
  return (
    <svg className={className} width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" focusable="false" {...STROKE}>
      <path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2" />
    </svg>
  );
}
