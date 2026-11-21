import type { components } from '../types/api';
import { request } from './client';

export type Answers = components['schemas']['AnswersDto'];
export type PlanStep = components['schemas']['PlanStepDto'];
export type StepCode = PlanStep['code'];
export type Plan = components['schemas']['PlanDto'];

/** The plan for these answers, for anyone: nothing is kept. */
export async function previewPlan(answers: Answers): Promise<PlanStep[]> {
  return (await request<components['schemas']['PlanPreviewDto']>('POST', '/orientation/plan', answers)).steps;
}

/** A rider's answers and plan, kept: it becomes the current plan. */
export function saveQuestionnaire(answers: Answers): Promise<Plan> {
  return request<Plan>('POST', '/orientation/questionnaires', answers);
}

/** The rider's current plan; 404 before any questionnaire. */
export function fetchPlan(): Promise<Plan> {
  return request<Plan>('GET', '/orientation/plan');
}

export function markStep(position: number, done: boolean): Promise<Plan> {
  return request<Plan>('PUT', `/orientation/plan/steps/${position}`, { done });
}
