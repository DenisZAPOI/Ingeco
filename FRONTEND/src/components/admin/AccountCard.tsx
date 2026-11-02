import { Link } from 'react-router-dom';

import type { Account } from '../../api/admin';
import { ROLE_LABELS, accountBadges, accountPath } from '../../lib/accounts';
import { formatPhone } from '../../lib/phone';
import { ArrowRightIcon } from '../ui/icons';

/** An account in the list: who, which role, what to notice. Opens its page without a new call. */
function AccountCard({ account }: { account: Account }) {
  return (
    <Link to={accountPath(account.id)} state={{ account }} className="ride-card">
      <span className="ride-card-text">
        <span className="ride-card-when">
          {account.firstName} {account.lastName}
        </span>
        <span>
          {ROLE_LABELS[account.role]} · {formatPhone(account.phone)}
        </span>
        <span className="ride-card-status">
          {accountBadges(account).map((badge) => (
            <span key={badge} className="badge">
              {badge}
            </span>
          ))}
        </span>
      </span>
      <ArrowRightIcon className="action-card-arrow" />
    </Link>
  );
}

export function AccountList({ accounts }: { accounts: Account[] }) {
  return (
    <ul className="ride-list">
      {accounts.map((account) => (
        <li key={account.id}>
          <AccountCard account={account} />
        </li>
      ))}
    </ul>
  );
}
