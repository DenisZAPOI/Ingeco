// CHANGER_SELON_DECISION (entretien du 03/11, illustration de l'accueil) : PLACEHOLDER.
// Provisional drawing made by the developers, to be replaced by a final
// illustration (from the client, or drawn with her). Copied in index.html for
// the welcome screen: change both together.

/** The home illustration, in the green band: a road to a workplace under the
 *  sun, a car on its way, two people waiting (one in a wheelchair). Inline SVG,
 *  a few hundred bytes, colors from the CSS. Decorative: the texts beside it
 *  say what the service is. */
export function HomeIllustration() {
  return (
    <svg className="hero-art" width="128" height="96" viewBox="0 0 160 120" aria-hidden="true" focusable="false">
      <circle className="art-sun" cx="132" cy="22" r="12" />
      <path className="art-hill" d="M0 78q40-14 80-6t80-4v52H0z" />
      {/* The workplace, on the horizon. */}
      <rect className="art-building" x="16" y="30" width="34" height="46" rx="3" />
      <path className="art-window" d="M22 38h8v7h-8zM36 38h8v7h-8zM22 51h8v7h-8zM36 51h8v7h-8zM29 65h8v11h-8z" />
      {/* The road, from the bottom of the band to the workplace. */}
      <path className="art-road" d="M56 120 78 76h10l26 44z" />
      <path className="art-road-line" d="M84 82v6M86 96v8M88 112v8" />
      {/* The car, on its way. */}
      <rect className="art-car" x="70" y="90" width="26" height="13" rx="4" />
      <circle className="art-wheel" cx="76" cy="104" r="3" />
      <circle className="art-wheel" cx="90" cy="104" r="3" />
      {/* Two people waiting by the road, one of them in a wheelchair. */}
      <circle className="art-person-a" cx="124" cy="72" r="6" />
      <rect className="art-person-a" x="117" y="80" width="14" height="24" rx="6" />
      <circle className="art-person-b" cx="146" cy="82" r="5" />
      <rect className="art-person-b" x="140" y="88" width="11" height="12" rx="4" />
      <circle className="art-wheelchair" cx="144" cy="106" r="7" />
    </svg>
  );
}
