import {
  createTariff,
  fetchServiceHours,
  fetchTariff,
  fetchZones,
  saveServiceHours,
  saveZones,
} from '../api/settings';
import { useRequest } from './useRequest';
import { useSubmit } from './useSubmit';

// The administrator's settings: each one loaded and saved on its own, so
// that a slow or failed call leaves the two others usable.

export function useServiceHours() {
  return useRequest(fetchServiceHours);
}

export function useSaveServiceHours() {
  return useSubmit(saveServiceHours);
}

export function useZones() {
  return useRequest(fetchZones);
}

export function useSaveZones() {
  return useSubmit(saveZones);
}

export function useTariff() {
  return useRequest(fetchTariff);
}

export function useCreateTariff() {
  return useSubmit(createTariff);
}
