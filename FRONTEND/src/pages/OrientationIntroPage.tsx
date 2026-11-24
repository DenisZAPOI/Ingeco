import { useNavigate } from 'react-router-dom';

import { PageHero, PageSheet } from '../components/layout/PageHero';
import { CheckIcon, ClockIcon, QuestionIcon } from '../components/ui/icons';
import { PrivacyNote } from '../components/ui/PrivacyNote';
import { t } from '../i18n';
import { NO_ANSWER, saveDraft } from '../lib/orientation';
import { orientationQuestionPath } from '../lib/paths';

/** « Faire le point »: what the questionnaire is, before the first question (module M1). */
export function OrientationIntroPage() {
  const navigate = useNavigate();

  function start() {
    saveDraft({ answers: NO_ANSWER, finished: false });
    navigate(orientationQuestionPath(1));
  }

  return (
    <section>
      <PageHero title={t('orientation.introTitle')}>
        <p className="hero-lead">{t('orientation.introLead')}</p>
      </PageHero>
      <PageSheet>
        <ul className="icon-list">
          <li>
            <ClockIcon className="button-icon" />
            {t('orientation.introQuestions')}
          </li>
          <li>
            <CheckIcon className="button-icon" />
            {t('orientation.introNoWrong')}
          </li>
          <li>
            <QuestionIcon className="button-icon" />
            {t('orientation.introSkip')}
          </li>
        </ul>
        <p className="note">{t('orientation.introPrivacy')}</p>
        <PrivacyNote />
        <button type="button" className="button button-block" onClick={start}>
          {t('orientation.start')}
        </button>
      </PageSheet>
    </section>
  );
}
