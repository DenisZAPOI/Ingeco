import { useCallback } from 'react';
import { Link } from 'react-router-dom';

import { ApiError } from '../../api/client';
import { fetchPlan, type Plan } from '../../api/orientation';
import { useRequest } from '../../hooks/useRequest';
import { t } from '../../i18n';
import { ORIENTATION_PLAN_PATH } from '../../lib/paths';
import { CheckIcon } from '../ui/icons';

const NOT_FOUND = 404;

/** « Mon plan d'action · 1 sur 4 » on a rider's home, below the three needs.
 *  Nothing before a first questionnaire, nor when the plan cannot be read:
 *  the home stays usable without it. */
export function PlanLink() {
  const load = useCallback(async (): Promise<Plan | null> => {
    try {
      return await fetchPlan();
    } catch (error) {
      if (error instanceof ApiError && error.status === NOT_FOUND) return null;
      throw error;
    }
  }, []);
  const { data: plan } = useRequest(load);
  if (!plan) return null;

  const done = plan.steps.filter((step) => step.doneAt !== null).length;
  return (
    <li>
      <Link to={ORIENTATION_PLAN_PATH} state={{ plan }} className="link-action">
        <CheckIcon className="button-icon" />
        {t('orientation.homeLink')}
        <span className="note"> · {t('orientation.homeProgress', { done, total: plan.steps.length })}</span>
      </Link>
    </li>
  );
}
