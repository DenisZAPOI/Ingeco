import type { ReactNode } from 'react';

type PageHeroProps = {
  title: string;
  /** Small line above the title ("Étape 2 sur 4", "Bonjour"). */
  eyebrow?: string;
  /** Under the title: a sentence, a progress bar, the logo… */
  children?: ReactNode;
  /** Language of the title when it is a content, not an interface text. */
  lang?: string;
};

/** The green band at the top of every screen, continuing the header. The
 *  page content follows in a <PageSheet>, which overlaps its rounded bottom. */
export function PageHero({ title, eyebrow, children, lang }: PageHeroProps) {
  return (
    <div className="hero">
      <RoadMotif />
      {eyebrow && <p className="hero-eyebrow">{eyebrow}</p>}
      <h1 className="hero-title" lang={lang}>
        {title}
      </h1>
      {children}
    </div>
  );
}

/** The white sheet holding the content of a screen. */
export function PageSheet({ children }: { children: ReactNode }) {
  return <div className="sheet">{children}</div>;
}

/** The road of the logo, large and faint: decoration only, inline (no file to download). */
function RoadMotif() {
  return (
    <svg className="hero-motif" width="150" height="90" viewBox="0 0 200 120" aria-hidden="true" focusable="false">
      <path d="M20 120 80 20h40l60 100" fill="none" stroke="currentColor" strokeWidth="10" strokeLinecap="round" strokeLinejoin="round" />
      <path className="hero-motif-line" d="M100 34v16m0 22v16" fill="none" strokeWidth="6" strokeLinecap="round" />
    </svg>
  );
}
