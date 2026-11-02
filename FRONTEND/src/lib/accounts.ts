import type { Account, AccountRole, AccountStatus, ActivationCode } from '../api/admin';
import { ADMIN_ACCOUNTS_PATH } from './paths';

export const ROLE_LABELS: Record<AccountRole, string> = {
  rider: 'Usager',
  driver: 'Chauffeur',
  partner: 'Référent partenaire',
  operator: 'Opérateur',
  admin: 'Administrateur',
};

export const ACCOUNT_STATUS_LABELS: Record<AccountStatus, string> = {
  active: 'Actif',
  suspended: 'Suspendu',
};

/** Badges of an account in a list: what the administrator must notice. */
export function accountBadges(account: Account): string[] {
  const badges: string[] = [];
  if (account.status === 'suspended') badges.push('Suspendu');
  if (!account.isActivated) badges.push('Pas encore activé');
  if (account.isPriority) badges.push('Prioritaire');
  if (account.role === 'driver' && !account.photoUpdatedAt) badges.push('Sans photo');
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
