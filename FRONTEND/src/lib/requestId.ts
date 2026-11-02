// Identifier of one booking, sent again as is if the network fails and the
// user retries: the API then returns the ride already booked instead of a
// second one (contract 6.7).

const UUID_BYTES = 16;
const VERSION_BYTE = 6;
const VARIANT_BYTE = 8;
const HEX = 16;

/** A UUID v4. crypto.randomUUID only exists over HTTPS; a phone testing the
 *  app by the computer's IP address is on plain http. */
export function newRequestId(): string {
  if (typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }
  const bytes = crypto.getRandomValues(new Uint8Array(UUID_BYTES));
  bytes[VERSION_BYTE] = (bytes[VERSION_BYTE] & 0x0f) | 0x40;
  bytes[VARIANT_BYTE] = (bytes[VARIANT_BYTE] & 0x3f) | 0x80;
  const hex = Array.from(bytes, (byte) => byte.toString(HEX).padStart(2, '0')).join('');
  return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}
