import { Link } from 'react-router-dom';

import type { PracticalGuide } from '../../api/practicalGuides';
import { categoryLabel } from '../../lib/helpServices';
import { guidePath } from '../../lib/paths';
import { ArrowRightIcon } from '../ui/icons';
import { CategoryIcon } from './CategoryIcon';

/** Practical guides as large links: the icon and name of their need, then their title. */
export function GuideList({ guides }: { guides: readonly PracticalGuide[] }) {
  return (
    <ul className="ride-list">
      {guides.map((guide) => (
        <li key={guide.id}>
          <Link to={guidePath(guide.id)} state={{ guide }} className="action-card">
            <span className="icon-chip">
              <CategoryIcon category={guide.category} />
            </span>
            <span className="action-card-text">
              {/* The guide's own text: French when it is not translated. */}
              <span className="action-card-title" lang={guide.language}>
                {guide.title}
              </span>
              <span className="action-card-hint">{categoryLabel(guide.category)}</span>
            </span>
            <ArrowRightIcon className="action-card-arrow" />
          </Link>
        </li>
      ))}
    </ul>
  );
}
