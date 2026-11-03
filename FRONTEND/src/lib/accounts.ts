import type { Account, AccountRole, AccountStatus, ActivationCode } from '../api/admin';
import { t } from '../i18n';
import { ADMIN_ACCOUNTS_PATH } from './paths';

/** In the order of the filters. */
export const ROLES: readonly AccountRole[] = ['rider', 'driver', 'partner', 'operator', 'admin'];

export function roleLabel(role: AccountRole): string {
  return t(`admin.roles.${role}`);
}

export function accountStatusLabel(status: AccountStatus): string {
  return t(`admin.statuses.${status}`);
}

/** Badges of an account in a list: what the administrator must notice. */
export function accountBadges(account: Account): string[] {
  const badges: string[] = [];
  if (account.status === 'suspended') badges.push(accountStatusLabel('suspended'));
  if (!account.isActivated) badges.push(t('admin.notActivated'));
  if (account.isPriority) badges.push(t('admin.priority'));
  if (account.role === 'driver' && !account.photoUpdatedAt) badges.push(t('admin.noPhoto'));
  return badges;
}

/** '12345678' → '1234 5678': easier to dictate on the phone. */
export function formatActivationCode(code: string): string {
  const half = code.length / 2;
  return `${code.slice(0, half)} ${code.slice(half)}`;
}

/** The account handed over by the previous screen, if it is this one. */
export function accountFromState(state: unknown, id: number): Account | null {
  if (typeof state !== 'object' || state === null || !('account' in state)) return null;
  const { account } = state as { account: unknown };
  return typeof account === 'object' && account !== null && (account as Account).id === id ? (account as Account) : null;
}

/** The activation code handed over by the creation screen. */
export function activationFromState(state: unknown): ActivationCode | null {
  if (typeof state !== 'object' || state === null || !('activation' in state)) return null;
  const { activation } = state as { activation: unknown };
  return typeof activation === 'object' && activation !== null && 'code' in activation ? (activation as ActivationCode) : null;
}

export function accountPath(id: number): string {
  return `${ADMIN_ACCOUNTS_PATH}/${id}`;
}
