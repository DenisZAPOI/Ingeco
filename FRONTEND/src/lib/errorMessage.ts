import { ApiError } from '../api/client';

// Short, plain-language messages: the public is not always at ease with
// digital tools, a technical message would not help them.
const FALLBACK_BY_STATUS: Record<number, string> = {
  401: 'Vous devez vous reconnecter.',
  403: "Vous n'avez pas accès à cette page.",
};
const GENERIC = "Une erreur s'est produite.";

export function errorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) {
    return GENERIC;
  }
  if (error.status === 0) {
    return 'Pas de connexion internet. Vérifiez votre réseau.';
  }
  if (error.status >= 500) {
    return 'Le service ne répond pas pour le moment.';
  }
  if (error.status === 400) {
    // The detail lists the faulty fields: each form shows them next to the field.
    return 'Vérifiez les informations en rouge.';
  }
  // The API writes its business messages in French, for the user.
  if (typeof error.detail === 'string') {
    return error.detail;
  }
  return FALLBACK_BY_STATUS[error.status] ?? GENERIC;
}
