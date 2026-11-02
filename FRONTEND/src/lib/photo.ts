// The driver's photo is reduced here, in the browser, before it leaves: a
// phone camera picture weighs several MB, far too much for 2G and for the
// database. The API only checks the result (a JPEG of 100 KB at most).

// The passenger sees a face in a small circle: 320 px is plenty.
const MAX_SIDE_PX = 320;
// Aimed at about 15 KB (contract, H19): the quality is lowered while the picture is heavier.
const QUALITIES = [0.8, 0.65, 0.5];
const TARGET_BYTES = 20 * 1024;
const JPEG = 'image/jpeg';
const DATA_URL_PREFIX = /^data:image\/jpeg;base64,/;
// Base64 writes 4 characters for every 3 bytes.
const BASE64_CHARS_PER_BLOCK = 4;
const BYTES_PER_BLOCK = 3;

export type ReducedPhoto = { base64: string; previewUrl: string; bytes: number };

/** The picture chosen by the administrator, as a small JPEG in base64. Rejects if it is not an image. */
export async function reducePhoto(file: File): Promise<ReducedPhoto> {
  const image = await createImageBitmap(file);
  const scale = Math.min(1, MAX_SIDE_PX / Math.max(image.width, image.height));
  const canvas = document.createElement('canvas');
  canvas.width = Math.round(image.width * scale);
  canvas.height = Math.round(image.height * scale);
  const context = canvas.getContext('2d');
  if (!context) throw new Error('Canvas unavailable');
  context.drawImage(image, 0, 0, canvas.width, canvas.height);
  image.close();

  let dataUrl = '';
  for (const quality of QUALITIES) {
    dataUrl = canvas.toDataURL(JPEG, quality);
    if (base64Bytes(dataUrl) <= TARGET_BYTES) break;
  }
  return { base64: dataUrl.replace(DATA_URL_PREFIX, ''), previewUrl: dataUrl, bytes: base64Bytes(dataUrl) };
}

function base64Bytes(dataUrl: string): number {
  return Math.round((dataUrl.replace(DATA_URL_PREFIX, '').length * BYTES_PER_BLOCK) / BASE64_CHARS_PER_BLOCK);
}
