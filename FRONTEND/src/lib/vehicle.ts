import type { VehicleData } from '../api/admin';

// Same bounds as the API (chk_vehicule_places).
export const MIN_SEATS = 1;
export const MAX_SEATS = 8;
export const DEFAULT_SEATS = 4;

export type VehicleDraft = { plate: string; model: string; seats: string; isAccessible: boolean };

export function vehicleDraft(vehicle: VehicleData | null): VehicleDraft {
  return {
    plate: vehicle?.plate ?? '',
    model: vehicle?.model ?? '',
    seats: String(vehicle?.seats ?? DEFAULT_SEATS),
    isAccessible: vehicle?.isAccessible ?? false,
  };
}

/** What the API receives. A number of seats left empty is sent as 0: the API answers on the field. */
export function vehicleData(draft: VehicleDraft): VehicleData {
  return { plate: draft.plate, model: draft.model, seats: Number(draft.seats) || 0, isAccessible: draft.isAccessible };
}
