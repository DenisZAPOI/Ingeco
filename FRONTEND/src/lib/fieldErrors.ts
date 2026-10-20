import { ApiError } from '../api/client';

export type FieldErrors = Record<string, string>;

const BAD_REQUEST = 400;

/** Messages of a 400, by field name (camelCase, as in the request body). */
export function fieldErrors(error: unknown): FieldErrors {
  if (!(error instanceof ApiError) || error.status !== BAD_REQUEST) {
    return {};
  }
  const detail = error.detail;
  if (typeof detail !== 'object' || detail === null || !('fields' in detail) || !Array.isArray(detail.fields)) {
    return {};
  }
  const errors: FieldErrors = {};
  for (const problem of detail.fields as unknown[]) {
    if (typeof problem === 'object' && problem !== null && 'field' in problem && 'message' in problem) {
      errors[String(problem.field)] = String(problem.message);
    }
  }
  return errors;
}
