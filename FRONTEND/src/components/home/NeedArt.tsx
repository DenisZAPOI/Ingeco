// CHANGER_SELON_DECISION (entretien du 03/11, illustration de l'accueil) : PLACEHOLDER.
// Drawings of the three needs, made by the developers (entretien du 03/11 :
// « accueil illustré »). Inline SVG, under 1 kB each, colors from the CSS.
// Copied in index.html for the welcome screen: change both together.

/** The drawing at the right of a need tile. Decorative: the title of the tile
 *  says the need. */
export function NeedArt({ tone }: { tone: 'work' | 'ride' | 'help' }) {
  return (
    <svg className="need-art" width="104" height="104" viewBox="0 0 104 104" aria-hidden="true" focusable="false">
      {tone === 'work' && <WorkArt />}
      {tone === 'ride' && <RideArt />}
      {tone === 'help' && <HelpArt />}
    </svg>
  );
}

/** A briefcase. */
function WorkArt() {
  return (
    <>
      <circle className="art-work-disc" cx="70" cy="58" r="44" />
      <rect className="art-green" x="38" y="44" width="56" height="40" rx="8" />
      <path className="art-stroke-green" d="M56 44v-8a6 6 0 0 1 6-6h8a6 6 0 0 1 6 6v8" />
      <rect className="art-sun" x="60" y="58" width="12" height="9" rx="2" />
    </>
  );
}

/** A car. */
function RideArt() {
  return (
    <>
      <circle className="art-ride-disc" cx="70" cy="58" r="44" />
      <path className="art-blue" d="M30 72h64V56l-8-16H42l-8 16z" />
      <rect className="art-sky" x="46" y="44" width="34" height="12" rx="3" />
      <circle className="art-dark" cx="46" cy="74" r="8" />
      <circle className="art-dark" cx="80" cy="74" r="8" />
    </>
  );
}

/** A lifebuoy. */
function HelpArt() {
  return (
    <>
      <circle className="art-help-disc" cx="70" cy="58" r="44" />
      <circle className="art-white" cx="68" cy="58" r="26" />
      <circle className="art-stroke-coral" cx="68" cy="58" r="26" strokeDasharray="20 20.8" />
      <circle className="art-help-disc" cx="68" cy="58" r="12" />
    </>
  );
}
