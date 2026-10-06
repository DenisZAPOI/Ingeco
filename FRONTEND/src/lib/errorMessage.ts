import { ApiError } from '../api/client';

// Short, plain-language messages: the public is not always at ease with
// digital tools, a technical message would not help them.
export function errorMessage(error: unknown): string {
  if (!(error instanceof ApiError)) {
    return "Une erreur s'est produite.";
  }
  if (error.status === 0) {
    return 'Pas de connexion internet. Vérifiez votre réseau.';
  }
  if (error.status === 401) {
    return 'Vous devez vous reconnecter.';
  }
  if (error.status === 403) {
    return "Vous n'avez pas accès à cette page.";
  }
  if (error.status >= 500) {
    return 'Le service ne répond pas pour le moment.';
  }
  return typeof error.detail === 'string' ? error.detail : "Une erreur s'est produite.";
}
