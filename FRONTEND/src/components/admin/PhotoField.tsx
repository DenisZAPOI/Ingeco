import { useId, useState, type ChangeEvent } from 'react';

import { photoUrl, type Account } from '../../api/admin';
import { useSavePhoto } from '../../hooks/useAdmin';
import { formatDateTime } from '../../lib/format';
import { reducePhoto, type ReducedPhoto } from '../../lib/photo';

const NOT_AN_IMAGE = "Ce fichier n'est pas une image. Choisissez une photo.";

type PhotoFieldProps = {
  account: Account;
  onSaved: (account: Account) => void;
};

/** The driver's face photo, taken at the in-person check: reduced on this
 *  device, shown before it is sent, then saved. The passenger will see it. */
export function PhotoField({ account, onSaved }: PhotoFieldProps) {
  const inputId = useId();
  const [photo, setPhoto] = useState<ReducedPhoto | null>(null);
  const [readError, setReadError] = useState<string | null>(null);
  const { submit, submitting, error } = useSavePhoto(account.id);
  const saved = photoUrl(account);

  async function choose(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    setReadError(null);
    setPhoto(null);
    if (!file) return;
    try {
      setPhoto(await reducePhoto(file));
    } catch {
      setReadError(NOT_AN_IMAGE);
    }
  }

  async function send() {
    if (!photo) return;
    const result = await submit(photo.base64);
    if (result) {
      setPhoto(null);
      onSaved(result);
    }
  }

  const shown = photo?.previewUrl ?? saved;
  return (
    <div className="field">
      {shown ? (
        <img src={shown} alt={`Photo de ${account.firstName}`} className="driver-photo" width={160} height={160} />
      ) : (
        <p className="note">Pas encore de photo.</p>
      )}
      {account.photoUpdatedAt && !photo && (
        <p className="note">Photo enregistrée le {formatDateTime(account.photoUpdatedAt)}.</p>
      )}
      <label htmlFor={inputId} className="button button-block button-secondary">
        {saved ? 'Reprendre la photo' : 'Prendre ou choisir une photo'}
      </label>
      {/* capture: on a phone, opens the camera directly. */}
      <input id={inputId} type="file" accept="image/*" capture="user" className="visually-hidden" onChange={choose} />
      {(readError ?? error) && (
        <p role="alert" className="alert alert-error">
          {readError ?? error}
        </p>
      )}
      {photo && (
        <button type="button" className="button button-block" onClick={send} disabled={submitting}>
          {submitting ? 'Envoi en cours…' : 'Enregistrer cette photo'}
        </button>
      )}
    </div>
  );
}
