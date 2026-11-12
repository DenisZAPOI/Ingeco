import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';

import type { PracticalGuide } from '../api/practicalGuides';
import { PageHero, PageSheet } from '../components/layout/PageHero';
import { RequestState } from '../components/ui/RequestState';
import { usePracticalGuide } from '../hooks/usePracticalGuides';
import { useSpeech } from '../hooks/useSpeech';
import { t } from '../i18n';
import { categoryLabel, formatUpdatedOn } from '../lib/helpServices';
import { GUIDES_PATH } from '../lib/paths';
import { guideFromState, guideSpeechText } from '../lib/practicalGuides';

/** One practical guide "Comment faire ?": its steps, read aloud on demand. */
export function PracticalGuidePage() {
  const id = Number(useParams().id);
  const location = useLocation();
  const navigate = useNavigate();
  const handed = guideFromState(location.state, id);
  const guide = usePracticalGuide(id, handed);

  return (
    <section>
      <PageHero title={guide.data?.title ?? t('guides.guideTitle')} lang={guide.data?.language}>
        {guide.data && <p className="hero-lead">{categoryLabel(guide.data.category)}</p>}
      </PageHero>
      <PageSheet>
        {/* A guide already shown stays shown if the confirmation fails (slow network). */}
        <RequestState loading={guide.loading && !guide.data} error={guide.data ? null : guide.error} onRetry={guide.retry}>
          {guide.data && <GuideDetail guide={guide.data} />}
        </RequestState>
        {/* Opened from a list: back to it. Opened from a link: to all the guides. */}
        <Link
          to={GUIDES_PATH}
          onClick={(event) => {
            if (handed) {
              event.preventDefault();
              navigate(-1);
            }
          }}
          className="link-action"
        >
          {t('guides.back')}
        </Link>
      </PageSheet>
    </section>
  );
}

function GuideDetail({ guide }: { guide: PracticalGuide }) {
  const speech = useSpeech(guide.language);

  return (
    <>
      <p className="lead" lang={guide.language}>
        {guide.intro}
      </p>
      {/* Only when the phone has a voice for this language (ADR 019). */}
      {speech.available && (
        <button
          type="button"
          className="button button-block button-secondary"
          onClick={() => (speech.speaking ? speech.stop() : speech.speak(guideSpeechText(guide)))}
        >
          {speech.speaking ? t('guides.stop') : t('guides.listen')}
        </button>
      )}
      <h2>{t('guides.stepsTitle')}</h2>
      {/* role="list": Safari drops the list semantics of a list without bullets. */}
      <ol className="guide-steps" role="list" lang={guide.language}>
        {guide.steps.map((step) => (
          <li key={step}>{step}</li>
        ))}
      </ol>
      {guide.toBring.length > 0 && (
        <div className="panel">
          <h2 className="panel-title">{t('guides.toBring')}</h2>
          <ul className="panel-list" lang={guide.language}>
            {guide.toBring.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      )}
      {guide.source && (
        <div className="panel">
          <h2 className="panel-title">{t('guides.sourceTitle')}</h2>
          <p>{t('guides.sourceText')}</p>
          {/* The text names the site: the user knows they leave the app. */}
          <a href={guide.source.url} className="button button-block button-secondary" rel="noopener noreferrer" lang={guide.language}>
            {guide.source.name}
          </a>
          <p className="note">{t('helpServices.simulators.outside')}</p>
        </div>
      )}
      <p className="note">
        {t('guides.updatedOn', { date: formatUpdatedOn(guide.updatedOn) })} {t('guides.demonstrator')}
      </p>
    </>
  );
}
