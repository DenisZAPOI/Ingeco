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

export function ArrowRightIcon({ className }: IconProps) {
  return (
    <svg className={className} width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" focusable="false" {...STROKE}>
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  );
}

export function UserIcon({ className }: IconProps) {
  return (
    <svg className={className} width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" focusable="false" {...STROKE}>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 20a8 8 0 0 1 16 0" />
    </svg>
  );
}

/** Filled when `filled`: the stars of a rating. */
export function StarIcon({ className, filled = false }: IconProps & { filled?: boolean }) {
  return (
    <svg
      className={className}
      width="24"
      height="24"
      viewBox="0 0 24 24"
      aria-hidden="true"
      focusable="false"
      {...STROKE}
      fill={filled ? 'currentColor' : 'none'}
    >
      <path d="M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9z" />
    </svg>
  );
}

export function CalendarIcon({ className }: IconProps) {
  return (
    <svg className={className} width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" focusable="false" {...STROKE}>
      <rect x="3" y="5" width="18" height="16" rx="2" />
      <path d="M3 10h18M8 3v4M16 3v4" />
    </svg>
  );
}

export function BriefcaseIcon({ className }: IconProps) {
  return (
    <svg className={className} width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" focusable="false" {...STROKE}>
      <rect x="3" y="7" width="18" height="13" rx="2" />
      <path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M3 13h18" />
    </svg>
  );
}

export function BookIcon({ className }: IconProps) {
  return (
    <svg className={className} width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" focusable="false" {...STROKE}>
      <path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z" />
      <path d="M4 21V5M8 7h7" />
    </svg>
  );
}
