import { PageHero, PageSheet } from '../components/layout/PageHero';
import { t, type TextKey } from '../i18n';

/** A text of the help page (none has a {placeholder}). */
type FaqKey = Extract<TextKey, `faq.${string}`>;

/** Each question with its answer, in the order shown. */
const QUESTIONS: [FaqKey, FaqKey][] = [
  ['faq.whatQ', 'faq.whatA'],
  ['faq.priceQ', 'faq.priceA'],
  ['faq.whereQ', 'faq.whereA'],
  ['faq.bookQ', 'faq.bookA'],
  ['faq.cancelQ', 'faq.cancelA'],
  ['faq.noDriverQ', 'faq.noDriverA'],
  ['faq.smsQ', 'faq.smsA'],
  ['faq.passwordQ', 'faq.passwordA'],
  ['faq.suspendedQ', 'faq.suspendedA'],
  ['faq.emergencyQ', 'faq.emergencyA'],
];

/** Frequently asked questions (cahier des charges §6). Public: linked from the
 *  footer of every screen. <details> opens without JavaScript and with the keyboard. */
export function FaqPage() {
  return (
    <section>
      <PageHero title={t('faq.title')}>
        <p className="hero-lead">{t('faq.intro')}</p>
      </PageHero>
      <PageSheet>
        <div className="faq">
          {QUESTIONS.map(([question, answer]) => (
            <details key={question} className="faq-item">
              <summary>{t(question)}</summary>
              <p>{t(answer)}</p>
            </details>
          ))}
        </div>
      </PageSheet>
    </section>
  );
}
